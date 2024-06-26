# file: tests/test_pdf_rag.py
"""
This file contains the tests for the PdfRAG class
"""

import os
import pytest
from pipeline import PdfRAG, OPENAI_API_KEY


@pytest.fixture
def valid_path():
    """
    Return the path to a valid PDF file
    """
    return os.path.join(os.path.dirname(__file__), "data/test.pdf")


@pytest.fixture
def pdf_rag(valid_path):
    """
    Create a PdfRAG instance for testing
    return: PdfRAG
    """
    return PdfRAG(
        base_url="https://api.openai.com/v1/",
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY,
        path=valid_path,
        collection_name="pdf_collection",
    )


def test_pdf_rag_initialization(pdf_rag: PdfRAG, valid_path: str):
    """
    Test the initialization of the PdfRAG class
    params: pdf_rag: PdfRAG
    """
    assert pdf_rag.base_url == "https://api.openai.com/v1/"
    assert pdf_rag.model == "gpt-4o"
    assert pdf_rag.openai_api_key == OPENAI_API_KEY
    assert pdf_rag.collection_name == "pdf_collection"
    assert pdf_rag.path == valid_path


def test_pdf_rag_invoke(pdf_rag: PdfRAG):
    """
    Test the invoke method of the PdfRAG class
    params: pdf_rag: PdfRAG
    """

    response = pdf_rag.invoke("Summarize the PDF file.")
    assert isinstance(response, str)
    print(response)
    assert response != "I don't know"


# def test_pdf_rag_delete_collection(pdf_rag: PdfRAG):
#     """
#     Test the delete_collection method of the PdfRAG class
#     params: pdf_rag: PdfRAG
#     """
#     pdf_rag.delete_collection()
#     response = pdf_rag.invoke("Summarize the PDF file.")
#     assert isinstance(response, str)
#     assert response == "I don't know"
