"""
file: pipeline/python_rag.py
class: PythonRAG
This module contains the PythonRAG class.
The user can load Python code from a local directory or a git repository
and set up a RAG pipeline.
"""
import os
import sys
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
        self.exclude = kwargs.get('exclude', [])
        # if exclude is not a list, convert it to a list
        if not isinstance(self.exclude, list):
            self.exclude = [self.exclude]

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

        try:
            # control the path and if the path does not exist, raise an error
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
        except ValueError as e:
            print(f"ValueError: {e}")
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"FileNotFoundError occurred: {e}")
        except PermissionError as e:
            print(f"PermissionError occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
        )
        all_chunks = self.split_data(python_splitter, self.documents)
        self.setup_vector_store(all_chunks)
