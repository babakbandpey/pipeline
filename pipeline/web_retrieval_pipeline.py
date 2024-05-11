from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import WebBaseLoader
from pipeline.pipeline import Pipeline
from pipeline.pipeline import ChatPromptTemplate
from pipeline.pipeline import MessagesPlaceholder

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
    def web_base_loader(url):
        """
        Loads the data from the specified URL.
        params: url: The URL to load the data
        returns: The loaded data.
        """

        loader = WebBaseLoader(url)
        return loader.load()


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
        returns: The answer from the chatbot.
        """
        self.chat_history.add_user_message(prompt)
        response = super().invoke(prompt)
        answer = response["answer"]
        self.chat_history.add_ai_message(answer)
        return answer


    def setup_chain(self, search_type=None, search_kwargs=None):
        '''
        Set up the chatbot pipeline chain.

        This method creates a chain of processing steps for the chatbot pipeline.
        It first creates a chain of documents using the `create_stuff_documents_chain` function,
        passing in the `chat` and `chat_prompt` parameters.
        Then, it creates a retrieval chain using the `vector_store.as_retriever()` method
        and the previously created document chain.
        The retrieval chain is returned as the final result.

        Returns:
            The retrieval chain for the retrieval chatbot pipeline.
        '''

        if search_type is None:
            search_type = "similarity"

        if search_kwargs is None:
            search_kwargs = {"k": 6}

        doc_combination_chain = create_stuff_documents_chain(self.chat, self.chat_prompt)
        return create_retrieval_chain(
            self.vector_store.as_retriever(
                search_type=search_type,
                search_kwargs=search_kwargs
            ),
            doc_combination_chain
        )
