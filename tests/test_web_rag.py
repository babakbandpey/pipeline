"""
Tests for the WebRAG class.
"""

import pytest
from pipeline import WebRAG, OPENAI_API_KEY

URL = "https://americanliterature.com/author/philip-k-dick/short-story/the-eyes-have-it/"

@pytest.fixture
def web_rag():
    """
    Returns a function that creates a WebRAG object with the specified URL.

    Parameters:
    - url (str): The URL to be used by the WebRAG object.

    Returns:
    - function: A function that takes a URL as input and returns a WebRAG object.

    Example usage:
    ```
    create_web_rag = web_rag()
    web_rag_obj = create_web_rag("https://example.com")
    ```
    """
    def _web_rag(url):
        return WebRAG(
            base_url="https://api.openai.com/v1/",
            model="gpt-4o",
            openai_api_key=OPENAI_API_KEY,
            url=url
        )
    return _web_rag


def test_web_rag_initialization(web_rag):
    """
    Test the initialization of the WebRag class.

    Args:
        web_rag: An instance of the WebRag class.

    Returns:
        None
    """
    web_rag_instance = web_rag(URL)
    assert web_rag_instance.base_url == "https://api.openai.com/v1/"
    assert web_rag_instance.model == "gpt-4o"
    assert web_rag_instance.openai_api_key == OPENAI_API_KEY


def test_web_rag_invoke(web_rag):
    """
    Test the invoke method of the web_rag instance.

    Args:
        web_rag: An instance of the web_rag class.

    Returns:
        None
    """
    web_rag_instance = web_rag(URL)
    response = web_rag_instance.invoke("Who is the author of the story?")
    assert isinstance(response, str)
    assert "Philip K. Dick" in response
