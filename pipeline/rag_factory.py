# file: pipeline/rag_factory.py

import importlib

class_mapping = {
    'chat': 'Chatbot',
    'txt': 'TxtRAG',
    'py': 'PyRAG',
    'web': 'WebRAG',
    'pdf': 'PdfRAG',
    'json': 'JsonRAG'
}

module_mapping = {
    'chat': 'pipeline.chatbot',
    'txt': 'pipeline.txt_rag',
    'py': 'pipeline.py_rag',
    'web': 'pipeline.web_rag',
    'pdf': 'pipeline.pdf_rag',
    'json': 'pipeline.json_rag'
}

class RAGFactory:
    """
    Factory class for creating RAG objects based on _type.
    """

    @staticmethod
    def get_rag_class(_type: str = 'txt', **kwargs):
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

        class_name = class_mapping.get(_type)
        module_name = module_mapping.get(_type)

        if not class_name or not module_name:
            raise ValueError(f"No RAG class found for type: {_type}")

        # Import the module
        module = importlib.import_module(module_name)
        # Get the class from the module
        rag_class = getattr(module, class_name)

        return rag_class(**kwargs)
