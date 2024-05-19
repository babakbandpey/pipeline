"""
file: tests/test_pipeline.py
class: TestChatbot
author: Babak Bandpey
This module contains the unit tests for the pipeline module.
"""

import unittest
from unittest.mock import patch
from src import Chatbot
from src import TextRAG
from src import WebRAG
from src import PythonRAG
from src import OPENAI_API_KEY

BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"

class TestChatbot(unittest.TestCase):

    def setUp(self):
        self.chatbot = Chatbot(base_url=BASE_URL, model=MODEL, openai_api_key=OPENAI_API_KEY)

    def test_setup_chat_prompt(self):
        self.chatbot.setup_chat_prompt(system_template="You are a happy and witty chatbot.")
        self.assertIsNotNone(self.chatbot.chat_prompt)

    # Additional tests for Chatbot class can be added here

class TestTextRAG(unittest.TestCase):

    def setUp(self):
        self.path = "./data/"
        self.textrag = TextRAG(path=self.path)

    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=["file1.txt", "file2.txt"])
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Sample text content")
    def test_load_documents_directory(self):
        self.textrag.load_documents()
        self.assertEqual(len(self.textrag.documents), 2)

    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Sample text content")
    def test_load_documents_file(self,):
        self.textrag.path = "./data/test.txt"
        self.textrag.load_documents()
        self.assertEqual(len(self.textrag.documents), 1)

    # Additional tests for TextRAG class can be added here

class TestWebRAG(unittest.TestCase):

    @patch('web_rag.WebBaseLoader')
    def setUp(self, MockWebBaseLoader):
        self.url = "https://dr.dk"
        self.webrag = WebRAG(url=self.url, base_url=BASE_URL, model=MODEL)
        self.MockWebBaseLoader = MockWebBaseLoader

    def test_web_base_loader(self):
        loader_instance = self.MockWebBaseLoader.return_value
        loader_instance.load.return_value = ["Sample web content"]
        document = self.webrag.web_base_loader(self.url)
        self.assertEqual(document, ["Sample web content"])

    # Additional tests for WebRAG class can be added here

class TestPythonRAG(unittest.TestCase):

    @patch('python_rag.Repo.clone_from')
    def setUp(self, mock_clone):
        self.git_url = "https://github.com/babakbandpey/pipeline"
        self.path = "./data/pipeline/"
        self.pythonrag = PythonRAG(git_url=self.git_url, path=self.path)
        mock_clone.assert_called_with(self.git_url, to_path=self.path)

    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=["file1.py", "file2.py"])
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Sample Python content")
    def test_load_documents_directory(self, mock_open, mock_listdir, mock_isdir):
        self.pythonrag.load_documents()
        self.assertEqual(len(self.pythonrag.documents), 2)

    # Additional tests for PythonRAG class can be added here

if __name__ == '__main__':
    unittest.main()
