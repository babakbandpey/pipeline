import pytest
import os
from pipeline import PythonRAG, OPENAI_API_KEY


# getting the path to the current directory
# and then joining the path to the ./data/test.txt file
path = os.path.join(os.path.dirname(__file__), "data/test.py")

@pytest.fixture
def python_rag():
    """
    Create a TextRAG instance for testing
    return: TextRAG
    """
    return PythonRAG(base_url="https://api.openai.com/v1/", model="gpt-4o", openai_api_key=OPENAI_API_KEY, path=path)

def test_python_rag_initialization(python_rag):
    """
    Test the initialization of the TextRAG class
    params: text_rag: TextRAG
    """
    assert python_rag.base_url == "https://api.openai.com/v1/"
    assert python_rag.model == "gpt-4o"
    assert python_rag.openai_api_key == OPENAI_API_KEY
    assert python_rag.path == path

def test_python_rag_invoke(python_rag):
    """
    Test the invoke method of the TextRAG class
    params: text_rag: TextRAG
    """

    response = python_rag.invoke("Summarize the python file.")
    assert isinstance(response, str)
