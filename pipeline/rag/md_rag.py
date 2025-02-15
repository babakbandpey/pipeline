"""
file: pipeline/md_rag.py
class: MdRAG
author: Babak Bandpey
This module contains the MdRAG class.
"""
# file: pipeline/markdown_rag.py
import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval


class MdRAG(Retrieval):
    """
    Represents a Markdown RAG pipeline.
    Extends the Retrieval class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the MarkdownRAG object.
        params: kwargs: Dictionary containing configuration parameters.
        """
        super().__init__(**kwargs)
        self.path = kwargs.get('path')
        self.headers = kwargs.get('headers', None)

        self.documents = []
        self.load_documents()
        self.split_and_store_documents()

    def _load_documents(self):
        """
        Loads Markdown documents from the filesystem.
        """

        if not self.path or not os.path.exists(self.path):
            raise ValueError(f"Invalid path: {self.path}. No such file or directory.")

        if os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for file in files:
                    if file.endswith(".md"):
                        loader = UnstructuredMarkdownLoader(os.path.join(root, file))
                        self.documents.extend(loader.load_and_split())
        else:
            loader = UnstructuredMarkdownLoader(self.path)
            self.documents = loader.load_and_split()

        self.logger.info("Loaded %s documents.", len(self.documents))
        self.logger.debug(self.documents)

    def split_and_store_documents(self):
        """
        Splits the documents into chunks and sets up the vector store.
        """
        markdown_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        all_chunks = self.split_data(markdown_splitter, self.documents)
        self.setup_vector_store(all_chunks)
