"""This module contains utility functions for file operations."""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileUtils:
    """Utility class for file operations."""


    @staticmethod
    def get_files() -> list:
        """Get all python files in the codebase."""
        files = []
        for root, _, filenames in os.walk("."):
            for filename in filenames:
                if filename.endswith(".py") and "env" not in root and '.git' not in root:
                    files.append(os.path.join(root, filename))
        return files


    @staticmethod
    def write_to_file(output_file, response):
        """Write the response to a file."""
        with open(output_file, "a", encoding='utf-8') as file:
            file.write(response)
            file.write("\n\n")


    @staticmethod
    def prepend_to_file(file_path, text):
        """Prepend text to a file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
            file.write(content)


    @staticmethod
    def get_files_from_path(path, file_extension=".py") -> list:
        """Get a list of Python files from the given path."""
        if not os.path.exists(path):
            logging.error("Error: The path '%s' does not exist.", path)
            return []

        if os.path.isfile(path):
            return [path]

        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(file_extension)]


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
