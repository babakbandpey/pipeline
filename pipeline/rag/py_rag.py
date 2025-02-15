"""
file: pipeline/python_rag.py
class: PythonRAG
This module contains the PythonRAG class.
The user can load Python code from a local directory or a git repository
and set up a RAG pipeline.
"""
import os
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval

class PyRAG(Retrieval):
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
        self.exclude = kwargs.get('exclude', [])
        if not isinstance(self.exclude, list):
            self.exclude = [self.exclude]

        self.documents = []

        if self.git_url:
            self.clone_repository()

        self.load_documents()
        self.split_and_store_documents()

    def clone_repository(self):
        """Clones the git repository to the specified path."""
        if not self.git_url or not self.path:
            raise ValueError("Both git_url and path to clone the repo to must be provided.")

        # Validate git_url
        if not self.is_valid_git_url(self.git_url):
            raise ValueError(f"Invalid git_url: {self.git_url}")

        try:
            Repo.clone_from(self.git_url, to_path=self.path)
            self.logger.info("Repository cloned from %s to %s", self.git_url, self.path)
        except Exception as e:
            self.logger.error("Failed to clone repository: %s", e)
            raise

    @staticmethod
    def is_valid_git_url(git_url: str) -> bool:
        """Validates the git URL."""
        # Add your validation logic here
        return git_url.startswith("https://") or git_url.startswith("git@")


    def _load_documents(self):
        """Loads Python documents from the filesystem."""
        if not os.path.exists(self.path):
            raise ValueError(f"Invalid path: {self.path}. No such file or directory.")

        loader = GenericLoader.from_filesystem(
                path=self.path,
                glob="**/*",
                suffixes=[".py"],
                exclude=self.exclude,
                parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
            )
        self.documents = loader.load()
        self.logger.info("Loaded %s documents.", len(self.documents))


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
        )
        all_chunks = self.split_data(python_splitter, self.documents)
        self.setup_vector_store(all_chunks)
