"""
file: src/__init__.py
author: Babak Bandpey
Description: The pipeline module provides a high-level interface for running a chatbot.
"""

from .config import OPENAI_API_KEY
from .chatbot import Chatbot
from .text_rag import TextRAG
from .web_rag import WebRAG
from .python_rag import PythonRAG
from .pdf_rag import PdfRAG

__all__ = [
    'Chatbot',
    'TextRAG',
    'WebRAG',
    'PythonRAG',
    'OPENAI_API_KEY',
    'PdfRAG'
]

__version__ = '0.5.0'
__author__ = 'Babak Bandpey <bb@cocode.dk>'
