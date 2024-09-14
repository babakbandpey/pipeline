"""
Factory class for creating RAG objects based on _type.
"""

import importlib
from .retrieval import Retrieval

rag_mapping = {
    'chat': ('pipeline.chatbot', 'Chatbot'),
    'txt': ('pipeline.txt_rag', 'TxtRAG'),
    'py': ('pipeline.py_rag', 'PyRAG'),
    'web': ('pipeline.web_rag', 'WebRAG'),
    'pdf': ('pipeline.pdf_rag', 'PdfRAG'),
    'json': ('pipeline.json_rag', 'JsonRAG'),
    'md': ('pipeline.md_rag', 'MdRAG'),
    'json': ('pipeline.json_rag', 'JsonRAG'),
    'md': ('pipeline.md_rag', 'MdRAG'),
}

class RAGFactory:
    """
    Factory class for creating RAG objects based on _type.
    """

    @staticmethod
    def get_rag_class(_type: str = 'txt', **kwargs) -> Retrieval:
        """
        Get the RAG class based on the specified type.

        Args:
            _type (str, optional): The type of RAG class to retrieve. Defaults to 'txt'.
            **kwargs: Additional keyword arguments to pass to the RAG class constructor.

        Returns:
            rag_class: An instance of the specified RAG class.

        Raises:
            ValueError: If no RAG class is found for the specified type.
        """

        module_name, class_name = rag_mapping.get(_type, (None, None))

        if not class_name or not module_name:
            raise ValueError(f"No RAG class found for type: {_type}")

        # Import the module
        module = importlib.import_module(module_name)
        # Get the class from the module
        rag_class = getattr(module, class_name)
        return rag_class(**kwargs)
