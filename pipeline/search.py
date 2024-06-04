""" The wrapper for the search functionality. """

from scrapegraphai.graphs import SearchGraph
from .retrieval import Retrieval

class Search(Retrieval):
    """ Pipeline for a chatbot that searches for information based on the given queries. """
    def __init__(self, **kwargs):
        """
        Initializes the Search object.
        params: kwargs: Dictionary containing configuration parameters.
        """
        super().__init__(**kwargs)

        self.search = SearchGraph(
            prompt=kwargs.get('prompt', None),
            config={
                "llm": {
                    "model": self.model,
                    "api_key": self.openai_api_key
                }
            }
        )

    def invoke(self, prompt):
        """
        Searches for the given queries.
        params: queries: The queries to search for.
        returns: The search results.
        """
        self.search.prompt = self.sanitize_input(prompt)
        return self.search.run()
