"""
This module contains the tests for the Chatbot class
"""

import pytest
from pipeline import Chatbot, OPENAI_API_KEY

@pytest.fixture
def chatbot():
    """
    Create a Chatbot instance for testing
    """
    return Chatbot(
        base_url="https://api.openai.com/v1/",
        model="gpt-4o", openai_api_key=OPENAI_API_KEY
    )

def test_chatbot_initialization(chatbot):
    """
    Test the initialization of the Chatbot class
    """
    assert chatbot.base_url == "https://api.openai.com/v1/"
    assert chatbot.model == "gpt-4o"
    assert chatbot.openai_api_key == OPENAI_API_KEY

def test_chatbot_invoke(chatbot):
    """
    Test the invoke method of the Chatbot class
    """
    response = chatbot.invoke("Hello, how are you?")
    assert isinstance(response, str)
    assert "Hello" in response
