"""
file: pipeline/text_rag.py
class: TextRAG
author: Babak Bandpey
This module contains the TextRAG class.
"""
import json
import os
import logging
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .retrieval import Retrieval

logging.basicConfig(level=logging.INFO)

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
        self.auto_clean = kwargs.get('auto_clean', False)
        if not self.path:
            raise ValueError("The path parameter is required.")
        self.documents = []
        self.check_for_non_ascii_bytes()
        self.load_documents()
        self.extract_and_add_metadata()
        self.split_and_store_documents()

    def check_for_non_ascii_bytes(self):
        """
        Checks for non-ASCII bytes in a text file or directory.
        If non-ASCII bytes are found, the user is prompted to clean the file.
        """
        def detect_and_clean(file_path):
            logging.info("Checking file: %s for non-ASCII bytes...", file_path)
            non_ascii_positions = self.find_non_ascii_bytes(file_path)
            if non_ascii_positions:
                logging.warning("Non-ASCII bytes found in file: %s", file_path)
                logging.warning(non_ascii_positions)
                if self.auto_clean:
                    self.clean_non_ascii_bytes(file_path)
                else:
                    raise ValueError(f"Non-ASCII bytes found in file: {file_path}. Please clean the file manually.")

        if not os.path.exists(self.path):
            raise ValueError(f"Invalid path: {self.path}. No such file or directory.")
        if os.path.isdir(self.path):
            for file in os.listdir(self.path):
                if file.endswith(".txt"):
                    file_path = os.path.join(self.path, file)
                    detect_and_clean(file_path)
        else:
            detect_and_clean(self.path)

    def load_documents(self):
        """Loads text documents from the filesystem."""
        logging.info("Loading document(s) from: %s", self.path)
        try:
            if os.path.isdir(self.path):
                loader = DirectoryLoader(self.path, glob="**/*.txt", loader_cls=TextLoader)
                self.documents = loader.load()
            elif os.path.isfile(self.path) and self.path.endswith(".txt"):
                loader = TextLoader(self.path)
                self.documents = loader.load()
        except ValueError as e:
            logging.error("ValueError: %s", e)
            raise
        except Exception as e:
            logging.error("UnicodeDecodeError: %s", e)
            raise ValueError(f"Invalid encoding in file: {self.path}") from e

    def extract_and_add_metadata(self):
        """
        If the Documents(page_content)'s first line begins with metadata,
        the first line contains a json object with metadata.
        This metadata shall be extracted and added to the document's metadata.
        """
        logging.info("Extracting metadata from the documents...")
        for document in self.documents:
            first_line = document.page_content.split("\n")[0]
            if first_line.startswith("{") and first_line.endswith("}"):
                try:
                    metadata = self.clean_and_parse_json(first_line)
                    logging.info("Metadata found in document: %s", metadata)
                    document.metadata.update(metadata)
                    document.page_content = "\n".join(document.page_content.split("\n")[1:])
                except json.JSONDecodeError as e:
                    logging.error("Line: %s", first_line)
                    logging.error("JSONDecodeError: %s", e)
                    raise

    @staticmethod
    def clean_and_parse_json(text):
        """
        Cleans and parses poorly formed JSON text to a dictionary.
        Parameters:
        - text: A string with poorly formed JSON.
        Returns:
        - A dictionary representation of the JSON text or None if parsing fails.
        """
        try:
            text = text.replace("'", '"')
            def replace_inner_quotes(part):
                part = part.strip()
                if part.startswith('"') and part.endswith('"'):
                    part = part[1:-1]
                    part = part.replace('"', "'")
                    part = f'"{part}"'
                return part
            parts = text.split(":")
            for index, part in enumerate(parts):
                if "," in part:
                    sub_parts = part.split(",")
                    sub_parts = [replace_inner_quotes(sub_part) for sub_part in sub_parts]
                    parts[index] = ",".join(sub_parts)
                else:
                    parts[index] = replace_inner_quotes(part)
            text = ":".join(parts)
            return json.loads(text)
        except json.JSONDecodeError as e:
            logging.error("Line: %s", text)
            logging.error("JSONDecodeError: %s", e)
            return None

    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
        logging.info("Splitting and storing documents in the local vector database...")
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
                cleaned_data.extend(replacement_byte)
            else:
                cleaned_data.append(byte)
        with open(file_path, 'wb') as file:
            file.write(cleaned_data)
