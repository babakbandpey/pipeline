import pytest
import os
from pipeline import TextRAG, OPENAI_API_KEY


# getting the path to the current directory
# and then joining the path to the ./data/test.txt file
path = os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture
def text_rag():
    """
    Create a TextRAG instance for testing
    return: TextRAG
    """
    return TextRAG(base_url="https://api.openai.com/v1/", model="gpt-4o", openai_api_key=OPENAI_API_KEY, path=path)

def test_text_rag_initialization(text_rag):
    """
    Test the initialization of the TextRAG class
    params: text_rag: TextRAG
    """
    assert text_rag.base_url == "https://api.openai.com/v1/"
    assert text_rag.model == "gpt-4o"
    assert text_rag.openai_api_key == OPENAI_API_KEY
    assert text_rag.path == path

def test_text_rag_invoke(text_rag):
    """
    Test the invoke method of the TextRAG class
    params: text_rag: TextRAG
    """

    response = text_rag.invoke("Summarize the text file.")
    assert isinstance(response, str)
