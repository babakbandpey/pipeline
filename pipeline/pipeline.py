"""
This class defines a pipeline for integrating Ollama with the Langchain library.
This class is in its early stages and will be updated as the project progresses.
Git Repo: https://github.com/babakbandpey/pipeline

Documentation: https://python.langchain.com/docs/use_cases/chatbots/memory_management/
"""

import uuid
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
from openai import APIConnectionError

# The base class for the ChatbotPipeline and RetrievalPipeline
class Pipeline:
    """
    Represents a pipeline for the chatbot.
    """

    def __init__(self, **kwargs):
        """
        Initializes the Pipeline object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        """

        self.base_url = kwargs.get('base_url', None)
        self.model = kwargs.get('model', None)
        self.openai_api_key = kwargs.get('openai_api_key', None)
        self.chat = None
        self.setup_chat()
        self.chat_history = ChatMessageHistory()
        self.chat_prompt = None
        self.setup_chat_prompt()
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
            runnable=self.setup_chain(),
            get_session_history=lambda session_history: self.chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )


    def setup_chat(self):
        """
        Sets up the Ollama object with the specified base URL and model.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        returns: The initialized Ollama object.
        """

        try:

            if self.openai_api_key is not None and self.model is not None and self.base_url is not None:
                # OpenAI
                chat: ChatOpenAI = ChatOpenAI(
                    base_url=self.base_url,
                    temperature=0,
                    api_key=self.openai_api_key,
                    model=self.model
                )
            elif self.model is None and self.base_url is not None:
                # LM Studio
                chat: ChatOpenAI = ChatOpenAI(
                    base_url=self.base_url,
                    temperature=0,
                    api_key=self.openai_api_key if self.openai_api_key is not None else "not-needed"
                )
            else:
                # Ollama
                chat = Ollama(
                    base_url=self.base_url,
                    model=self.model
                )

            self.chat = chat

        except APIConnectionError as e:
            print(f"API Connection Error: {e}")
            raise e
        except Exception as e:
            print(f"Unknown exception occured: {e}")
            raise e


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
        Summarizes the chat history and deletes the messages.
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
    def split_data(document_splitter, data):
        '''
        Splits the data into chunks using the specified text splitter.
        params: document_splitter: The text splitter object to split the data with.
        params: data: The data to split.
        returns: The split data.
        '''
        return document_splitter.split_documents(data)


    def setup_chat_prompt(self, system_template: str = None):
        """
        Sets up the chat prompt for the chatbot.
        params: system_template: The system template to use.
        returns: The initialized ChatPromptTemplate object.
        """

        if system_template is None:
            system_template = """You are a helpful assistant.
            Answer all questions to the best of your ability. """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_template
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )

        self.chat_prompt = prompt
