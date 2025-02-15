"""
Pipeline: A high-level interface for running a chatbot.

This package provides tools and utilities for building and running chatbots
with features like RAG (Retrieval-Augmented Generation) and various utilities.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pipeline")
except PackageNotFoundError:
    __version__ = "unknown"

__author__ = 'Babak Bandpey <bb@cocode.dk>'

# Essential imports
from .config import OPENAI_API_KEY
from .chatbot import Chatbot

# Utility imports
from .utils.pipeline_utils import PipelineUtils
from .utils.file_utils import FileUtils
from .utils.chatbot_utils import ChatbotUtils
from .utils.logger import logger

# RAG (Retrieval-Augmented Generation) imports
from .rag import (
    TxtRAG,
    WebRAG,
    PyRAG,
    PdfRAG,
    JsonRAG,
    MdRAG,
)

# YouTube downloader import
from .ytdpl.youtube_caption_downloader import YouTubeCaptionDownloader

__all__ = [
    'OPENAI_API_KEY',
    'PipelineUtils',
    'FileUtils',
    'ChatbotUtils',
    'Chatbot',
    'TxtRAG',
    'WebRAG',
    'PyRAG',
    'PdfRAG',
    'JsonRAG',
    'MdRAG',
    'logger',
    'YouTubeCaptionDownloader'
]
