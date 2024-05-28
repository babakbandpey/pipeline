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
    return os.path.join(os.path.dirname(__file__), "data\\test.pdf")


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
        path=valid_path
    )


def test_pdf_rag_initialization(pdf_rag, valid_path):
    """
    Test the initialization of the PdfRAG class
    params: pdf_rag: PdfRAG
    """
    assert pdf_rag.base_url == "https://api.openai.com/v1/"
    assert pdf_rag.model == "gpt-4o"
    assert pdf_rag.openai_api_key == OPENAI_API_KEY
    assert pdf_rag.path == valid_path


def test_pdf_rag_invoke(pdf_rag):
    """
    Test the invoke method of the PdfRAG class
    params: pdf_rag: PdfRAG
    """

    response = pdf_rag.invoke("Summarize the PDF file.")
    assert isinstance(response, str)
