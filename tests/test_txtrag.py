"""
Test the TextRAG class in the pipeline module.
"""

import os
import pytest
from pipeline import TxtRAG, OPENAI_API_KEY


# getting the path to the current directory
# and then joining the path to the ./data/test.txt file
path = os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture
def txt_rag():
    """
    Create a TextRAG instance for testing
    return: TextRAG
    """
    return TxtRAG(
        base_url="https://api.openai.com/v1/",
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY,
        path=path
    )


def test_text_rag_initialization(txt_rag):
    """
    Test the initialization of the TextRAG class
    params: text_rag: TextRAG
    """
    assert txt_rag.base_url == "https://api.openai.com/v1/"
    assert txt_rag.model == "gpt-4o"
    assert txt_rag.openai_api_key == OPENAI_API_KEY
    assert txt_rag.path == path


def test_text_rag_invoke(txt_rag):
    """
    Test the invoke method of the TextRAG class
    params: text_rag: TextRAG
    """

    response = txt_rag.invoke("Summarize the text file.")
    assert isinstance(response, str)
