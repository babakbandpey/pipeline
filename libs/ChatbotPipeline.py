from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

class ChatbotPipeline:
    """_summary_
    Pipeline for a chatbot that retrieves documents from a
    website and answers questions based on the retrieved documents.
    """

    def __init__(self, base_url, model):
        self.ollama = self.setup_ollama(base_url, model)
        self.prompt = self.setup_prompt()
        self.vector_store = None  # Will be initialized later when data is ready
        self.chat_history = ChatMessageHistory()  # Using LangChain's built-in message history
        self.chat_prompt = self.setup_chat_prompt()
        self.chain_with_message_history = RunnableWithMessageHistory(
            self.get_chat_chain(),
            lambda session_id: self.chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def setup_ollama(self, base_url, model):
        """
        Sets up the Ollama object with the specified base URL and model.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        returns: The initialized Ollama object.
        """
        return Ollama(base_url=base_url, model=model)


    def setup_prompt(self):
        """
        Sets up the prompt for the chatbot.
        returns: The initialized ChatPromptTemplate object.
        """

        system_prompt = (
            "Using the retrieved documents, answer the questions asked. "
            "add the links to the news. "
            "Context: {context}. "
        )
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{context}")
        ])


    @staticmethod
    def setup_chat_prompt():
        """
        Sets up the chat prompt for the chatbot.
        returns: The initialized ChatPromptTemplate object.
        """

        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Answer all questions to the best of your ability.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )


    def load_data(self, loader):
        '''
        Loads the data from the specified loader.
        params: loader: The loader object to load the data from.
        returns: The loaded data.
        '''
        return loader.load()


    def split_data(self, text_splitter, data):
        '''
        Splits the data into chunks using the specified text splitter.
        params: text_splitter: The text splitter object to split the data with.
        params: data: The data to split.
        returns: The split data.
        '''
        return text_splitter.split_documents(data)


    def setup_vector_store(self, all_chunks):
        '''
        Sets up the vector store with the specified chunks.
        params: all_chunks: The chunks to set up the vector store with.
        returns: The initialized vector store.
        '''

        self.vector_store = Chroma.from_documents(documents=all_chunks, embedding=GPT4AllEmbeddings())


    def setup_chains(self):
        '''
        Sets up the chains for the chatbot.
        returns: The full chain for the chatbot.
        '''

        doc_combination_chain = create_stuff_documents_chain(self.ollama, self.prompt)
        return create_retrieval_chain(self.vector_store.as_retriever(), doc_combination_chain)


    def query_chain(self, full_chain, query):
        '''
        Queries the full chain with the specified query.
        params: full_chain: The full chain to query.
        params: query: The query to use.
        '''

        result = full_chain.invoke({"input": query})
        print(result)


    def process_data(self, loader, text_splitter):
        '''
        Processes the data using the specified loader and text splitter.
        params: loader: The loader object to load the data
        params: text_splitter: The text splitter object to split the data with.
        returns: The full chain for the chatbot.
        '''

        data = self.load_data(loader)
        all_chunks = self.split_data(text_splitter, data)
        self.setup_vector_store(all_chunks)
        return self.setup_chains()


    @staticmethod
    def read_file(file_path):
        """
        Reads the file at the specified path.
        params: file_path: The path to the file to read.
        returns: The contents of the file.
        """

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


    def get_chat_chain(self):
        """
        Gets the chat chain for the chatbot.
        returns: The chat chain for the chatbot.
        """

        return self.chat_prompt | self.ollama


    def invoke(self, prompt):
        """
        Invokes the chatbot with the specified query.
        params: query: The query to use.
        """
        # self.chat_history.add_user_message(prompt)
        # Generate the response considering the entire chat history

        response = self.chain_with_message_history.invoke(
            {"input": prompt,},
            {"configurable": {"session_id": "unused"}},
        )

        # Add AI's response to the chat history
        # self.chat_history.add_ai_message(response)

        return response
        # return self.ollama.invoke(prompt)


    def clear_chat_history(self):
        """
        Clears the chat history.
        """

        self.chat_history.clear()


    def web_base_loader(self, url):
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

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter
