"""
file: pipeline/md_rag.py
class: MdRAG
author: Babak Bandpey
This module contains the MdRAG class.
"""
import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .retrieval import Retrieval


class MdRAG(Retrieval):
    """
    Represents a Markdown RAG pipeline.
    Extends the Retrieval class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the PythonRAG object.
        params: kwargs: Dictionary containing configuration parameters.
        """
        super().__init__(**kwargs)
        self.documents = []
        self.check_for_non_ascii_bytes()
        self.load_documents()
        self.split_and_store_documents()


    def _load_documents(self):
        """Loads markdown documents from the filesystem."""
        self.documents = []
        if os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for file in files:
                    if file.endswith(".md"):
                        full_path = os.path.join(root, file)
                        loader = UnstructuredMarkdownLoader(full_path, mode="elements")
                        self.documents.extend(loader.load())
        elif os.path.isfile(self.path) and self.path.endswith(".md"):
            loader = UnstructuredMarkdownLoader(self.path, mode="elements")
            self.documents.extend(loader.load())

        if not self.documents:
            raise ValueError("No Markdown documents found in the specified path.")


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        self.logger.info("Splitting and storing documents in the local vector database...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
        all_chunks = self.split_data(text_splitter, self.documents)
        self.setup_vector_store(all_chunks)
