"""
This module contains the Scraper class, which is responsible for scraping data from a given URL.
This is a wrapper around the SmartScraperGraph class.
"""


import re
import os
from scrapegraphai.graphs import SmartScraperGraph
from .retrieval import Retrieval

class Scraper(Retrieval):
    """
    Pipeline for a chatbot that scrapes data from a website
    and answers questions based on the scraped data.
    """
    def __init__(self, **kwargs):
        """
        Initializes the Scraper object.
        params: kwargs: Dictionary containing configuration parameters.
        """
        super().__init__(**kwargs)

        self.url = kwargs.get('url', None)
        if not self.is_valid_url(self.url):
            raise ValueError("Invalid URL provided.")

        self.scraper = SmartScraperGraph(
            self.sanitize_input(kwargs.get('prompt', None)),
            self.url,
            {
                "llm": {
                    "model": self.model,
                    "api_key": self.openai_api_key
                }
            }
        )

    @staticmethod
    def is_valid_url(url):
        """
        Validates the provided URL.
        params: url: The URL to validate.
        returns: True if the URL is valid, False otherwise.
        """
        if not url:
            return False

        # checking if the url is actually a local file path
        if url.startswith("file://"):
            # check if the file exists
            file_path = url.replace("file://", "")
            if not os.path.exists(file_path):
                raise ValueError(f"Invalid URL provided. File not found: {file_path}")
            return True

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


    def invoke(self, prompt):
        """
        Invokes the scraper with the given prompt.
        params: prompt: The prompt for the scraper.
        returns: The result of the scraper.
        """

        self.scraper.prompt = self.sanitize_input(prompt)
        return self.scraper.run()
