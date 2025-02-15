"""
file: pipeline/web_rag.py
class: WebRAG
author: Babak Bandpey
This module contains the WebRAG class, which is a pipeline for a chatbot that retrieves
documents from a website and answers questions based on the retrieved documents.
"""

from langchain_community.document_loaders import WebBaseLoader
from pipeline.retrieval import Retrieval
from pipeline.utils.chatbot_utils import ChatbotUtils

class WebRAG(Retrieval):
    """
    Pipeline for a chatbot that retrieves documents from a website and
    answers questions based on the retrieved documents.
    """

    def __init__(self, **kwargs):
        """
        Initializes the WebRAG object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        """
        super().__init__(**kwargs)

        self.documents = []

        if not ChatbotUtils.is_valid_url(self.url):
            raise ValueError("Invalid URL provided.")

        try:
            self.load_documents()
            text_splitter = self.recursive_character_text_splitter()
            all_chunks = self.split_data(text_splitter, self.documents)
            self.setup_vector_store(all_chunks)
        except Exception as e:
            self.logger.exception("Error initializing WebRAG: %s", e)
            raise

    def _load_documents(self):
        """
        Loads the data from the specified URL.
        params: url: The URL to load the data from.
        """
        try:
            loader = WebBaseLoader(self.url)
            self.documents = loader.load()
        except Exception as e:
            self.logger.exception("Error loading data from URL %s: %s", url=self.url, e=e)
            raise
