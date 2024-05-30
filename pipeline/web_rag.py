"""
file: pipeline/web_rag.py
class: WebRAG
author: Babak Bandpey
This module contains the WebRAG class, which is a pipeline for a chatbot that retrieves
documents from a website and answers questions based on the retrieved documents.
"""
from langchain_community.document_loaders import WebBaseLoader
from .retrieval import Retrieval
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebRAG(Retrieval):
    """Pipeline for a chatbot that retrieves documents from a website and answers questions based on the retrieved documents."""

    def __init__(self, **kwargs):
        """
        Initializes the WebRAG object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        """
        super().__init__(**kwargs)
        url = kwargs.get('url', None)
        if not self.is_valid_url(url):
            raise ValueError("Invalid URL provided.")

        try:
            document = self.web_base_loader(url)
            text_splitter = self.recursive_character_text_splitter()
            all_chunks = self.split_data(text_splitter, document)
            self.setup_vector_store(all_chunks)
        except Exception as e:
            logger.error("Error initializing WebRAG: %s", e)
            raise

    @staticmethod
    def is_valid_url(url):
        """
        Validates the provided URL.
        params: url: The URL to validate.
        returns: True if the URL is valid, False otherwise.
        """
        if not url:
            return False
        # Simple regex for URL validation
        regex = re.compile(
            r'^(?:http|https)://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    @staticmethod
    def web_base_loader(url):
        """
        Loads the data from the specified URL.
        params: url: The URL to load the data from.
        returns: The loaded data.
        """
        try:
            loader = WebBaseLoader(url)
            return loader.load()
        except Exception as e:
            logger.error("Error loading data from URL %s: %s", url=url, e=e)
            raise
