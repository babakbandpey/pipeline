"""
The user can load PDF documents from a local directory
"""
# file: pipeline/pdf_rag.py
import os
import sys
import logging
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .retrieval import Retrieval

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PdfRAG(Retrieval):
    """
    Represents a PDF RAG pipeline.
    Extends the Retrieval class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the PdfRAG object.
        params: kwargs: Dictionary containing configuration parameters.
        """
        super().__init__(**kwargs)
        self.path = kwargs.get('path')
        self.recursive = kwargs.get('recursive', False)
        self.load_hidden = kwargs.get('load_hidden', False)
        self.extract_images = kwargs.get('extract_images', False)
        self.silent_errors = kwargs.get('silent_errors', False)
        self.headers = kwargs.get('headers', None)
        self.password = kwargs.get('password', None)

        self.documents = []
        self.load_documents()
        self.split_and_store_documents()

    def load_documents(self):
        """Loads PDF documents from the filesystem."""
        try:
            if not self.path or not os.path.exists(self.path):
                raise ValueError(f"Invalid path: {self.path}. No such file or directory.")

            if os.path.isdir(self.path):
                loader = PyPDFDirectoryLoader(
                    path=self.path,
                    recursive=self.recursive,
                    load_hidden=self.load_hidden,
                    extract_images=self.extract_images,
                    silent_errors=self.silent_errors
                )
            else:
                loader = PyPDFLoader(
                    self.path,
                    extract_images=self.extract_images,
                    headers=self.headers,
                    password=self.password
                )

            self.documents = loader.load_and_split()

            logger.info("Loaded %s documents.", len(self.documents))
            logger.debug(self.documents)

        except ValueError as e:
            logger.error("ValueError: %s", e)
            sys.exit(1)
        except FileNotFoundError as e:
            logger.error("FileNotFoundError occurred: %s", e)
        except PermissionError as e:
            logger.error("PermissionError occurred: %s", e)

    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        try:
            pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            all_chunks = self.split_data(pdf_splitter, self.documents)
            self.setup_vector_store(all_chunks)
        except Exception as e:
            logger.error("An error occurred while splitting and storing documents: %s", e)
