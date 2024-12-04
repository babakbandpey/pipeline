"""
file: pipeline/__init__.py
author: Babak Bandpey
Description: The pipeline module provides a high-level interface for running a chatbot.
"""

__version__ = '0.5.0'
__author__ = 'Babak Bandpey <bb@cocode.dk>'

# Essential imports
from .config import OPENAI_API_KEY
from .chatbot import Chatbot

# Utility imports
from .pipeline_utils import PipelineUtils
from .file_utils import FileUtils
from .chatbot_utils import ChatbotUtils
from .logger import logger

# RAG (Retrieval-Augmented Generation) imports
from .txt_rag import TxtRAG
from .web_rag import WebRAG
from .py_rag import PyRAG
from .pdf_rag import PdfRAG
from .json_rag import JsonRAG
from .md_rag import MdRAG

# Nmap project imports
from .nmap_project.nmap_scanner import NmapScanner
from .nmap_project.searchsploit import SearchSploit
from .ytdpl.youtube_caption_downloader import YouTubeCaptionDownloader as YTCaptionDownloader


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
    'NmapScanner',
    'SearchSploit',
    'YTCaptionDownloader'
]
