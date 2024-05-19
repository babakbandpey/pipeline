"""
file: src/__init__.py
author: Babak Bandpey
Description: The pipeline module provides a high-level interface for running a chatbot.
"""

# from .pipeline import Pipeline
# from .chatbot import Chatbot
# from .text_rag import TextRAG
# from .web_rag import WebRAG
# from .python_rag import PythonRAG
# from .config import OPENAI_API_KEY

# # Package-level variables
# __version__ = '0.1.0'
# __author__ = 'Babak Bandpey <bb@cocode.dk>'
# __all__ = [
#     'Pipeline',
#     'Retrieval',
#     'Chatbot',
#     'TextRAG',
#     'WebRAG',
#     'PythonRAG',
#     'OPENAI_API_KEY'
# ]


import os
import sys
from .config import OPENAI_API_KEY
from .pipeline import Pipeline
from .chatbot import Chatbot
from .text_rag import TextRAG
from .web_rag import WebRAG
from .python_rag import PythonRAG

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

__all__ = []

__all__.append('OPENAI_API_KEY')
__all__.append('Pipeline')
__all__.append('Chatbot')
__all__.append('TextRAG')
__all__.append('WebRAG')
__all__.append('PythonRAG')
