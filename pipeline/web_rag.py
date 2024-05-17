"""
file: pipeline/web_rag.py
class: WebRAG
author: Babak Bandpey
This module contains the WebRAG class, which is a pipeline for a chatbot that retrieves
documents from a website and answers questions based on the retrieved documents.
"""
from langchain_community.document_loaders import WebBaseLoader
from pipeline.retrieval import Retrieval

# RETRIEVAL PIPELINE
class WebRAG(Retrieval):
    """_summary_
    Pipeline for a chatbot that retrieves documents from a
    website and answers questions based on the retrieved documents.
    """

    def __init__(self, **kwargs):
        """
        Initializes the ChatbotPipeline object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        """
        super().__init__(**kwargs)
        url = kwargs.get('url', None)
        document = self.web_base_loader(url)
        text_splitter = self.recursive_character_text_splitter()
        all_chunks = self.split_data(text_splitter, document)
        self.setup_vector_store(all_chunks)

    @staticmethod
    def web_base_loader(url):
        """
        Loads the data from the specified URL.
        params: url: The URL to load the data
        returns: The loaded data.
        """

        loader = WebBaseLoader(url)
        return loader.load()
