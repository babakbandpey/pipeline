"""
file: pipeline/__init__.py
author: Babak Bandpey
Description: The pipeline module provides a high-level interface for running a chatbot.
"""

from .config import OPENAI_API_KEY
from .chatbot import Chatbot
from .txt_rag import TxtRAG
from .web_rag import WebRAG
from .py_rag import PyRAG
from .pdf_rag import PdfRAG
from .pipeline_utils import PipelineUtils
from .file_utils import FileUtils
from .chatbot_utils import ChatbotUtils

__all__ = [
    'PipelineUtils',
    'FileUtils',
    'ChatbotUtils',
    'Chatbot',
    'TxtRAG',
    'WebRAG',
    'PyRAG',
    'OPENAI_API_KEY',
    'PdfRAG',
]

__version__ = '0.5.0'
__author__ = 'Babak Bandpey <bb@cocode.dk>'
