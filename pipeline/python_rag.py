"""
This module contains the PythonRAG class.
The user can load Python code from a local directory or a git repository and set up a RAG pipeline.
"""

from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from pipeline.pipeline import RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval


class PythonRAG(Retrieval):
    """
    Represents a Python RAG pipeline.
    Extends the Retrieval class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the PythonRAG object.
        params: kwargs: Dictionary containing configuration parameters.
        """

        super().__init__(**kwargs)

        self.path = kwargs.get('path')
        self.git_url = kwargs.get('git_url')
        self.documents = []

        if self.git_url:
            self.clone_repository()

        self.load_documents()
        self.split_and_store_documents()


    def clone_repository(self):
        """Clones the git repository to the specified path."""
        Repo.clone_from(self.git_url, to_path=self.path)


    def load_documents(self):
        """Loads Python documents from the filesystem."""
        loader = GenericLoader.from_filesystem(
            path=self.path,
            glob="**/*",
            suffixes=[".py"],
            exclude=["**/non-utf8-encoding.py"],
            parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
        )
        self.documents = loader.load()


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
        )
        all_chunks = self.split_data(python_splitter, self.documents)
        self.setup_vector_store(all_chunks)
