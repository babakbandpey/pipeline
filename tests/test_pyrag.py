"""
This file contains the tests for the PythonRAG class
"""

import os
import pytest
from pipeline import PyRAG, OPENAI_API_KEY


# getting the path to the current directory
# and then joining the path to the ./data/test.txt file
path = os.path.join(os.path.dirname(__file__), "data/test.py")

@pytest.fixture
def py_rag():
    """
    Create a TextRAG instance for testing
    return: TextRAG
    """
    return PyRAG(
        base_url="https://api.openai.com/v1/",
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY, path=path
    )


def test_python_rag_initialization(py_rag):
    """
    Test the initialization of the TextRAG class
    params: text_rag: TextRAG
    """
    assert py_rag.base_url == "https://api.openai.com/v1/"
    assert py_rag.model == "gpt-4o"
    assert py_rag.openai_api_key == OPENAI_API_KEY
    assert py_rag.path == path


def test_python_rag_invoke(py_rag):
    """
    Test the invoke method of the TextRAG class
    params: text_rag: TextRAG
    """

    response = py_rag.invoke("Summarize the python file.")
    assert isinstance(response, str)
