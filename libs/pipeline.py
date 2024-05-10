"""
This class defines a pipeline for integrating Ollama with the Langchain library.
This class is in its early stages and will be updated as the project progresses.
Git Repo: https://github.com/babakbandpey/pipeline
"""

import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


# The base class for the ChatbotPipeline and RetrievalPipeline
class Pipeline:
    """
    Represents a pipeline for the chatbot.
    """

    def __init__(self, base_url, model):
        """
        Initializes the Pipeline object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        """
        self.chat = self.setup_chat(base_url, model)
        self.chat_history = ChatMessageHistory()
        self.chat_prompt = self.setup_chat_prompt()
        self.vector_store = None
        self.chain_with_message_history = None
        # This is a unique session ID for the chatbot to keep track of the conversation
        self.chat_session_id = self.generate_session_id()


    def setup_chain_with_message_history(self):
            """
            Sets up a chain with message history.

            Returns:
                RunnableWithMessageHistory: A runnable object with message history.
            """
            return RunnableWithMessageHistory(
                self.setup_chain(),
                lambda session_id: self.chat_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )


    def setup_chat(self, base_url, model):
        """
        Sets up the Ollama object with the specified base URL and model.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        returns: The initialized Ollama object.
        """

        return Ollama(base_url=base_url, model=model)


    @staticmethod
    def read_file(file_path):
        """
        Reads the file at the specified path.
        params: file_path: The path to the file to read.
        returns: The contents of the file.
        """

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


    def setup_chain(self):
        """
        Gets the chat chain for the chatbot.
        returns: The chat chain for the chatbot.
        """

        return self.chat_prompt | self.chat


    def setup_vector_store(self, all_chunks):
        '''
        Sets up the vector store with the specified chunks.
        params: all_chunks: The chunks to set up the vector store with.
        returns: The initialized vector store.
        '''

        self.vector_store = Chroma.from_documents(
            documents=all_chunks,
            embedding=GPT4AllEmbeddings())


    def invoke(self, prompt):
        """
        Invokes the chatbot with the specified query.
        params: prompt: The prompt to use.
        """

        if self.chain_with_message_history is None:
            self.chain_with_message_history = self.setup_chain_with_message_history()

        response = self.chain_with_message_history.invoke(
            {"input": prompt,},
            {"configurable": {"session_id": self.chat_session_id}},
        )

        return response


    def clear_chat_history(self):
        """
        Clears the chat history.
        """

        self.chat_history.clear()


    def modify_chat_history(self, num_messages: int):
        """
        Deletes the chat history.
        params: num_messages: The number of messages to keep.
            If set to 0, all messages will be deleted.
            If number is positive deleting form the start of the list.
            If number is negative deleting form the end of the list.
        returns: True if the chat history is modified, False otherwise.
        """

        # If no num_messages is provided, return False
        if num_messages is None:
            return False

        messages = self.chat_history.messages
        len_messages = len(messages)

        if num_messages > len_messages:
            return False

        if num_messages == 0:
            self.clear_chat_history()
        elif num_messages > 0:
            self.chat_history.clear()
            for i in range(num_messages, len_messages):
                self.chat_history.add_message(messages[i])
        elif num_messages < 0:
            self.chat_history.clear()
            for i in range(len_messages + num_messages):
                self.chat_history.add_message(messages[i])

        return True


    def summarize_messages(self):
        """
        Summarizes the chat history.
        returns: True if the chat history is summarized, False otherwise.
        """

        stored_messages = self.chat_history.messages
        if len(stored_messages) == 0:
            return False
        summarization_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    "Distill the above chat messages into a single summary message. Include as many specific details as you can.",
                ),
            ]
        )
        summarization_chain = summarization_prompt | self.chat

        summary_message = summarization_chain.invoke({"chat_history": stored_messages})

        self.chat_history.clear()

        self.chat_history.add_message(summary_message)

        return True


    @staticmethod
    def web_base_loader(url):
        """
        Loads the data from the specified URL.
        params: url: The URL to load the data
        returns: The loaded data.
        """

        loader = WebBaseLoader(url)
        return loader.load()


    @staticmethod
    def recursive_character_text_splitter(chunk_size=500, chunk_overlap=0):
        """
        Splits the data into chunks using the specified chunk size and overlap.
        params: chunk_size: The size of the chunks.
        params: chunk_overlap: The overlap between the chunks.
        returns: The split data.
        """

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap)
        return text_splitter


    @staticmethod
    def generate_session_id():
        """
        Generates a unique session ID.
        returns: A unique session ID.
        """
        return str(uuid.uuid4())


    @staticmethod
    def split_data(text_splitter, data):
        '''
        Splits the data into chunks using the specified text splitter.
        params: text_splitter: The text splitter object to split the data with.
        params: data: The data to split.
        returns: The split data.
        '''
        return text_splitter.split_documents(data)


    @staticmethod
    def setup_chat_prompt():
        """
        Placeholder method for setting up the chat prompt.
        """
        raise NotImplementedError("Chat prompt not implemented.")


# CHATBOT PIPELINE
class ChatbotPipeline(Pipeline):
    """_summary_
    Pipeline for a chatbot
    """

    @staticmethod
    def setup_chat_prompt():
        """
        Sets up the chat prompt for the chatbot.
        returns: The initialized ChatPromptTemplate object.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Answer all questions to the best of your ability.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        return prompt


# RETRIEVAL PIPELINE
class WebRetrievalPipeline(Pipeline):
    """_summary_
    Pipeline for a chatbot that retrieves documents from a
    website and answers questions based on the retrieved documents.
    """

    def __init__(self, base_url, model, url):
        """
        Initializes the ChatbotPipeline object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        """
        super().__init__(base_url=base_url, model=model)

        document = self.web_base_loader(url)
        text_splitter = self.recursive_character_text_splitter()
        all_chunks = self.split_data(text_splitter, document)
        self.setup_vector_store(all_chunks)


    @staticmethod
    def setup_chat_prompt():
        """
        Sets up the prompt for the chatbot.
        returns: The initialized ChatPromptTemplate object.
        """

        system_template = """
        Answer the user's questions based on the below context.
        If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

        <context>
        {context}
        </context>
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_template
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        return prompt


    def invoke(self, prompt):
        """
        Invokes the chatbot with the specified query.
        This method adds the user message to the chat history and then invokes the chatbot.
        The method implemented in the parent class for memory management does not work as expected.
        params: prompt: The prompt to use.
        returns: The response from the chatbot.
        """
        self.chat_history.add_user_message(prompt)
        response = super().invoke(prompt)
        answer = response["answer"]
        self.chat_history.add_ai_message(answer)
        return answer


    def setup_chain(self):
        '''
        Set up the chatbot pipeline chain.

        This method creates a chain of processing steps for the chatbot pipeline.
        It first creates a chain of documents using the `create_stuff_documents_chain` function,
        passing in the `chat` and `chat_prompt` parameters.
        Then, it creates a retrieval chain using the `vector_store.as_retriever()` method
        and the previously created document chain.
        The retrieval chain is returned as the final result.

        Returns:
            The retrieval chain for the chatbot pipeline.
        '''

        doc_combination_chain = create_stuff_documents_chain(self.chat, self.chat_prompt)
        return create_retrieval_chain(self.vector_store.as_retriever(), doc_combination_chain)
