from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders.generic import GenericLoader
from pipeline.pipeline import RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval


class TextRAG(Retrieval):
    """
    Represents a Python RAG pipeline.
    Extends the Retrieval class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the PythonRAG object.
        params: kwargs: Dictionary containing configuration parameters.
        """
        base_url = kwargs.get('base_url')
        model = kwargs.get('model')
        super().__init__(base_url=base_url, model=model)

        self.path = kwargs.get('path')
        self.documents = []

        self.load_documents()
        self.split_and_store_documents()


    def load_documents(self):
        """Loads text documents from the filesystem."""
        loader = DirectoryLoader(self.path , glob="**/*.txt", loader_cls=TextLoader)
        self.documents = loader.load()


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
        all_chunks = self.split_data(text_splitter, self.documents)
        self.setup_vector_store(all_chunks)
