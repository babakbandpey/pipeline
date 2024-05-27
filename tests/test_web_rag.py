import pytest
import requests_mock
from pipeline import WebRAG, OPENAI_API_KEY

url = "https://americanliterature.com/author/philip-k-dick/short-story/the-eyes-have-it/"

@pytest.fixture
def web_rag():
    def _web_rag(url):
        return WebRAG(
            base_url="https://api.openai.com/v1/",
            model="gpt-4o",
            openai_api_key=OPENAI_API_KEY,
            url=url
        )
    return _web_rag

def test_web_rag_initialization(web_rag):
    web_rag_instance = web_rag(url)
    assert web_rag_instance.base_url == "https://api.openai.com/v1/"
    assert web_rag_instance.model == "gpt-4o"
    assert web_rag_instance.openai_api_key == OPENAI_API_KEY

def test_web_rag_invoke(web_rag):
    web_rag_instance = web_rag(url)
    response = web_rag_instance.invoke("Who is the author of the story?")
    assert isinstance(response, str)
    assert "Philip K. Dick" in response
