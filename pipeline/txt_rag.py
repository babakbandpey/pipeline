"""
file: pipeline/text_rag.py
class: TextRAG
author: Babak Bandpey
This module contains the TextRAG class.
"""
import json
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .retrieval import Retrieval
from .chatbot_utils import ChatbotUtils


class TxtRAG(Retrieval):
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
        self.path = kwargs.get('path', None)
        if not self.path:
            raise ValueError("The path parameter is required.")
        self.documents = []
        self.check_for_non_ascii_bytes()
        self.load_documents()
        self.extract_and_add_metadata()
        self.split_and_store_documents()


    def _load_documents(self):
        """Loads text documents from the filesystem."""
        if os.path.isdir(self.path):
            loader = DirectoryLoader(self.path, glob="**/*.txt", loader_cls=TextLoader)
            self.documents = loader.load()
        elif os.path.isfile(self.path) and self.path.endswith(".txt"):
            loader = TextLoader(self.path)
            self.documents = loader.load()


    def extract_and_add_metadata(self):
        """
        If the Documents(page_content)'s first line begins with metadata,
        the first line contains a json object with metadata.
        This metadata shall be extracted and added to the document's metadata.
        """
        self.logger.info("Extracting metadata from the documents...")
        for document in self.documents:
            first_line = document.page_content.split("\n")[0]
            if first_line.startswith("{") and first_line.endswith("}"):
                try:
                    metadata = ChatbotUtils.clean_and_parse_json(first_line)
                    self.logger.info("Metadata found in document: %s", metadata)
                    document.metadata.update(metadata)
                    document.page_content = "\n".join(document.page_content.split("\n")[1:])
                except json.JSONDecodeError as e:
                    self.logger.error("Line: %s", first_line)
                    self.logger.error("JSONDecodeError: %s", e)
                    raise


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        self.logger.info("Splitting and storing documents in the local vector database...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
        all_chunks = self.split_data(text_splitter, self.documents)
        self.setup_vector_store(all_chunks)
