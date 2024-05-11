from git import Repo
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from pipeline.pipeline import RecursiveCharacterTextSplitter
from pipeline.pipeline import Pipeline
from pipeline.pipeline import ChatPromptTemplate
from pipeline.pipeline import MessagesPlaceholder

class PythonRAGPipeline(Pipeline):
    """
    Pipeline for a chatbot that retrieves documents from a
    website and answers questions based on the retrieved documents.
    """

    def __init__(self, base_url, model, path, git_url=None, git_clone=False):
        """
        Initializes the PythonRAGPipeline object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        params: path: The path to the repo.
        params: git_url: The URL of the git repo.
        params: git_clone: Whether to clone the git repo.
        """
        super().__init__(base_url=base_url, model=model)

        if git_clone:
            Repo.clone_from(git_url, to_path=path)

        loader = GenericLoader.from_filesystem(
            path=path,
            glob="**/*",
            suffixes=[".py"],
            exclude=["**/non-utf8-encoding.py"],
            parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
        )
        documents = loader.load()

        print(f"Loaded {len(documents)} documents")
        for doc in documents:
            print(doc)

        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
        )

        all_chunks = self.split_data(python_splitter, documents)
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
                ("user", "{input}"),
            ]
        )

        return prompt


    def setup_chain(self, search_type=None, search_kwargs=None):
        '''
        Set up the chatbot pipeline chain.

        This method creates a chain of processing steps for the chatbot pipeline.

        This Python code is part of a class method named setup_chain.
        This method is used to set up a chatbot pipeline chain,
        which is a sequence of processing steps for the chatbot.
        The method takes two optional parameters: search_type and search_kwargs.

        The search_type parameter specifies the type of search to use.
        If no search type is provided, the method defaults to using "mmr" as the search type.

        The search_kwargs parameter is a dictionary that contains keyword arguments for the search.
        If no arguments are provided,
        the method defaults to a dictionary with a single key-value pair: {"k": 8}.

        The method then creates a prompt object using the ChatPromptTemplate.
        from_messages method. This method takes a list of messages as input.
        In this case, the list contains three messages.
        The first message is a placeholder for the chat history.
        The second message is the user's input.
        The third message is a prompt for the user to generate a search query based
        on the conversation.

        Next, the method creates a retriever object using the vector_store.as_retriever method.
        This method takes the search_type and search_kwargs as arguments.

        The retriever_chain is then created using the create_history_aware_retriever function.
        This function takes the chat history, the retriever, and the prompt as arguments.

        The doc_combination_chain is created using the create_stuff_documents_chain function.
        This function takes the chat history and the chat prompt as arguments.

        Finally, the method returns a retrieval chain created by the create_retrieval_chain function.
        This function takes the retriever_chain and the doc_combination_chain as arguments.
        The retrieval chain is the final output of the setup_chain method.

        params: search_type: The type of search to use.
        params: search_kwargs: The keyword arguments for the search.

        Returns:
            The retrieval chain for the retrieval chatbot pipeline.
        '''

        if search_type is None:
            search_type = "mmr"

        if search_kwargs is None:
            search_kwargs = {"k": 8}

        prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                (
                    "user",
                    "Given the above conversation, generate a search query to look up to get information relevant to the conversation",
                ),
            ]
        )

        retriever = self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )

        retriever_chain = create_history_aware_retriever(self.chat, retriever, prompt)

        doc_combination_chain = create_stuff_documents_chain(self.chat, self.chat_prompt)
        return create_retrieval_chain(
            retriever_chain,
            doc_combination_chain
        )

    def invoke(self, prompt):
        """
        Invokes the chatbot with the specified query.
        params: prompt: The prompt to use.
        returns: The answer from the chatbot.
        """
        self.chat_history.add_user_message(prompt)
        response = super().invoke(prompt)
        answer = response["answer"]
        self.chat_history.add_ai_message(answer)
        return answer
