import os
import dotenv

# Importing main classes to make them available directly under the package
from .chatbot import Chatbot
from .text_rag import TextRAG
from .web_rag import WebRAG
from .python_rag import PythonRAG


# OPENAI
dotenv.load_dotenv(dotenv_path='.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Package-level variables
__version__ = '0.1.0'
__author__ = 'Babak Bandpey <[email protected]>'
__all__ = ['Chatbot', 'TextRAG', 'WebRAG', 'PythonRAG', 'OPENAI_API_KEY']
