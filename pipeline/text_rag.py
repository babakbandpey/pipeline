"""
file: pipeline/text_rag.py
class: TextRAG
author: Babak Bandpey
This module contains the TextRAG class.
"""
import os
import sys
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .retrieval import Retrieval


class TextRAG(Retrieval):
    """
    Represents a Python RAG pipeline.
    Extends the Retrieval class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the PythonRAG object.
        params: kwargs: Dictionary containing configuration parameters.
        """

        super().__init__(**kwargs)

        self.path = kwargs.get('path', None)

        if not self.path:
            raise ValueError("The path parameter is required.")

        self.documents = []

        self.check_for_non_ascii_bytes()
        self.load_documents()
        self.split_and_store_documents()


    def check_for_non_ascii_bytes(self):
        """
        Checks for non-ASCII bytes in a text file or directory.
        If non-ASCII bytes are found, the user is prompted to clean the file.
        """

        def detect_and_clean(file_path):
            print(f"Checking file: {file_path} for non-ASCII bytes...")
            non_ascii_positions = self.find_non_ascii_bytes(file_path)
            if non_ascii_positions:
                print(f"Non-ASCII bytes found in file: {file_path}")
                print(non_ascii_positions)
                answer = input("Do you want to clean the file? (y/n): ")
                if answer.lower() == 'y':
                    self.clean_non_ascii_bytes(file_path)
                else:
                    print("\n\nYou need to clean the file manaually before proceeding. Exiting.\n\n")
                    sys.exit(1)

        try:
            if not os.path.exists(self.path):
                raise ValueError(f"Invalid path: {self.path}. No such file or directory.")

            # if path is a directory, check all .txt files in the directory
            if os.path.isdir(self.path):
                for file in os.listdir(self.path):
                    if file.endswith(".txt"):
                        file_path = os.path.join(self.path, file)
                        detect_and_clean(file_path)
            else:
                non_ascii_positions = self.find_non_ascii_bytes(self.path)
                if non_ascii_positions:
                    detect_and_clean(self.path)
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
            sys.exit(1)


    def load_documents(self):
        """Loads text documents from the filesystem."""

        print(f"Loading document(s) from: {self.path}")

        try:
            if os.path.isdir(self.path):
                loader = DirectoryLoader(self.path , glob="**/*.txt", loader_cls=TextLoader)
                self.documents = loader.load()
            # if path is a file, load the file
            elif os.path.isfile(self.path) and self.path.endswith(".txt"):
                loader = TextLoader(self.path)
                self.documents = [loader.load()]
        except ValueError as e:
            print(f"ValueError: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"UnicodeDecodeError: {e}")
            # read the .txt files from the directory and find non-ascii bytes
            raise ValueError(f"Invalid encoding in file: {self.path}") from e


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""

        print("Splitting and storing documents in the local vector database...")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
        all_chunks = self.split_data(text_splitter, self.documents)
        self.setup_vector_store(all_chunks)


    @staticmethod
    def find_non_ascii_bytes(file_path):
        """
        Finds non-ASCII bytes in a text file.
        params: file_path: The path to the text file.
        returns: A list of tuples containing the position and byte value of non-ASCII bytes.
        """
        with open(file_path, 'rb') as file:
            data = file.read()

        non_ascii_positions = [(i, byte) for i, byte in enumerate(data) if byte > 0x7F]

        return non_ascii_positions

    @staticmethod
    def clean_non_ascii_bytes(file_path, replacement_byte=b' '):
        """
        Cleans non-ASCII bytes from a text file.
        params: file_path: The path to the text file.
        params: replacement_byte: The byte to replace non-ASCII bytes with.
        """

        with open(file_path, 'rb') as file:
            data = file.read()

        cleaned_data = bytearray()
        for byte in data:
            if byte > 0x7F:
                cleaned_data.extend(replacement_byte)  # Replace with replacement_byte or remove
            else:
                cleaned_data.append(byte)

        with open(file_path, 'wb') as file:
            file.write(cleaned_data)
