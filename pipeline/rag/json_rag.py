"""
file: pipeline/json_rag.py
class: JsonRAG
author: Babak Bandpey
This module contains the JsonRAG class.
"""
import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval

class JsonRAG(Retrieval):
    """
    Represents a Python RAG pipeline for JSON documents.
    Extends the Retrieval class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the JsonRAG object.
        params: kwargs: Dictionary containing configuration parameters.
        """
        super().__init__(**kwargs)
        self.path = kwargs.get('path', None)
        self.auto_clean = kwargs.get('auto_clean', False)
        if not self.path:
            raise ValueError("The path parameter is required.")
        self.documents = []
        self.check_for_non_ascii_bytes()
        self.load_documents()
        self.split_and_store_documents()


    def _load_documents(self):
        """Loads JSON documents from the filesystem."""
        if os.path.isdir(self.path):
            loader = DirectoryLoader(self.path, glob="**/*.json", loader_cls=JSONLoader)
            self.documents = loader.load()
        elif os.path.isfile(self.path) and self.path.endswith(".json"):
            loader = JSONLoader(self.path, jq_schema=".", text_content=False)
            self.documents = loader.load()


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        self.logger.info("Splitting and storing documents in the local vector database...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
        all_chunks = self.split_data(text_splitter, self.documents)
        self.setup_vector_store(all_chunks)
