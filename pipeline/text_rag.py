import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders.generic import GenericLoader
from pipeline.pipeline import RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval


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

        self.load_documents()
        self.split_and_store_documents()


    def load_documents(self):
        """Loads text documents from the filesystem."""
        try:
            if os.path.isdir(self.path):
                loader = DirectoryLoader(self.path , glob="**/*.txt", loader_cls=TextLoader)
                self.documents = loader.load()
            # if path is a file, load the file
            elif os.path.isfile(self.path) and self.path.endswith(".txt"):
                loader = TextLoader(self.path)
                self.documents = [loader.load()]
        except Exception as e:
            print(f"UnicodeDecodeError: {e}")
            # read the .txt files from the directory and find non-ascii bytes
            for file in os.listdir(self.path):
                if file.endswith(".txt"):
                    file_path = os.path.join(self.path, file)
                    non_ascii_positions = self.find_non_ascii_bytes(file_path)
                    if non_ascii_positions:
                        print(f"Non-ASCII bytes found in file: {file_path}")
                        print(non_ascii_positions)
                        self.clean_non_ascii_bytes(file_path)

            raise ValueError(f"Invalid encoding in file: {self.path}") from e


    def split_and_store_documents(self):
        """Splits the documents into chunks and sets up the vector store."""
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
