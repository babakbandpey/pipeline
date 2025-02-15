"""
The user can load PDF documents from a local directory
"""
# file: pipeline/pdf_rag.py
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval

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
        self.extract_images = kwargs.get('extract_images', False)
        self.headers = kwargs.get('headers', None)
        self.password = kwargs.get('password', None)

        self.documents = []
        self.load_documents()
        self.split_and_store_documents()


    def _load_documents(self):
        """Loads PDF documents from the filesystem."""
        if not self.path or not os.path.exists(self.path):
            raise ValueError(f"Invalid path: {self.path}. No such file or directory.")

        if os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for file in files:
                    if file.endswith(".pdf"):
                        loader = PyPDFLoader(
                            os.path.join(root, file),
                            extract_images=self.extract_images,
                            headers=self.headers,
                        )
                        self.documents.extend(loader.load_and_split())
        else:
            loader = PyPDFLoader(
                self.path,
                extract_images=self.extract_images,
                headers=self.headers,
                password=self.password
            )
            self.documents = loader.load_and_split()

        self.logger.info("Loaded %s documents.", len(self.documents))
        self.logger.debug(self.documents)

    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        all_chunks = self.split_data(pdf_splitter, self.documents)
        self.setup_vector_store(all_chunks)
