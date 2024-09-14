import os
from .logger import logger

class FileUtils:
    """Utility class for file operations."""

    @staticmethod
    def get_files(root_path=".", extension=".py", exclude_dirs=None) -> list:
        """
        Get all files with the specified extension in the codebase, excluding certain directories.
        params: root_path: The root directory to start searching for files.
        params: extension: The file extension to search for.
        params: exclude_dirs: Directories to exclude from the search.
        """

        if exclude_dirs is None:
            exclude_dirs = [".env", ".git"]

        files = []
        for root, _, filenames in os.walk(root_path):
            if any(exclude in root for exclude in exclude_dirs):
                continue
            files.extend(os.path.join(root, f) for f in filenames if f.endswith(extension))
        return files

    @staticmethod
    def write_to_file(file_path, content, mode='w', encoding='utf-8'):
        """
        Write or append content to a file.
        params: file_path: The path to the output file.
        params: content: The content to write to the file.
        params: mode: The mode to open the file ('w' for write, 'a' for append, 'x' for exclusive creation).
        params: encoding: The encoding to use for writing the file.
        Supported modes:
            'w': Write (overwrite) the file. If the file exists, it will be truncated to zero length.
            'a': Append to the file. If the file does not exist, it will be created.
            'x': Exclusive creation. The file will be created, and an error will be raised if it already exists.
        """
        if mode not in ['w', 'a', 'x']:
            raise ValueError("Unsupported mode. Use 'w' for write, 'a' for append, or 'x' for exclusive creation.")

        try:
            with open(file_path, mode, encoding=encoding) as file:
                file.write(content)
                if mode == 'a':
                    file.write("\n\n")
            logger.info("File written successfully: %s", file_path)
        except FileNotFoundError as e:
            logger.error("Error: %s", e)

    @staticmethod
    def read_file(file_path, encoding='utf-8') -> str:
        """
        Read content from a file.
        params: file_path: The path to the file.
        params: encoding: The encoding to use for reading the file.
        returns: The content of the file as a string.
        """
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            logger.info("File read successfully: %s", file_path)
            return content
        except FileNotFoundError as e:
            logger.error("Error: %s", e)
            return ""
        except Exception as e:
            logger.error("Error: %s", e)
            return ""

    @staticmethod
    def prepend_to_file(file_path, content, encoding='utf-8'):
        """
        Prepend content to a file.
        params: file_path: The path to the file.
        params: content: The content to prepend to the file.
        params: encoding: The encoding to use for writing the file.
        """
        try:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding=encoding) as file:
                    file.write(content)
                logger.info("File created and content written successfully: %s", file_path)
            else:
                with open(file_path, 'r+', encoding=encoding) as file:
                    file_content = file.read()
                    file.seek(0, 0)
                    file.write(content + file_content)
                logger.info("Content prepended successfully: %s", file_path)
        except FileNotFoundError as e:
            logger.error("Error: %s", e)

    @staticmethod
    def clean_non_ascii_positions(file_path, positions, replacement_byte=b' '):
        """
        Cleans non-ASCII bytes from a text file at specified positions.
        params: file_path: The path to the text file.
        params: positions: A list of tuples with positions and values of non-ASCII bytes.
        params: replacement_byte: The byte to replace non-ASCII bytes with.
        """
        try:
            if len(replacement_byte) != 1:
                raise ValueError("replacement_byte must be a single byte.")

            replacement_byte_int = replacement_byte[0]  # Get the integer value of the replacement byte

            with open(file_path, 'rb') as file:
                data = bytearray(file.read())

            for pos, _ in positions:
                if pos < len(data):
                    data[pos] = replacement_byte_int

            with open(file_path, 'wb') as file:
                file.write(data)

            logger.info("Non-ASCII bytes cleaned from file: %s", file_path)
        except FileNotFoundError as e:
            logger.error("File not found: %s", e)
        except ValueError as e:
            logger.error("Value error: %s", e)
        except Exception as e:
            logger.error("An error occurred: %s", e)

    @staticmethod
    def find_non_ascii_bytes(file_path):
        """
        Finds non-ASCII bytes in a text file.
        params: file_path: The path to the text file.
        returns: A list of tuples containing the position and byte value of non-ASCII bytes.
        """
        try:
            with open(file_path, 'rb') as file:
                data = file.read()
            non_ascii_positions = [(i, byte) for i, byte in enumerate(data) if byte > 0x7F]
            return non_ascii_positions
        except FileNotFoundError as e:
            logger.error("Error: %s", e)
            return []
