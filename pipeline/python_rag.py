from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from pipeline.pipeline import RecursiveCharacterTextSplitter
from pipeline.retrieval import Retrieval

class PythonRAG(Retrieval):
    """
    Pipeline for a chatbot that retrieves documents from a
    website and answers questions based on the retrieved documents.
    """

    def __init__(self, base_url, model, path, git_url=None, git_clone=False):
        """
        Initializes the PythonRAG object.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        params: path: The path to the repo.
        params: git_url: The URL of the git repo.
        params: git_clone: Whether to clone the git repo.
        """
        super().__init__(base_url=base_url, model=model)

        if git_clone:
            Repo.clone_from(git_url, to_path=path)

        loader = GenericLoader.from_filesystem(
            path=path,
            glob="**/*",
            suffixes=[".py"],
            exclude=["**/non-utf8-encoding.py"],
            parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
        )
        documents = loader.load()

        print(f"Loaded {len(documents)} documents")
        for doc in documents:
            print(doc)

        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
        )

        all_chunks = self.split_data(python_splitter, documents)
        self.setup_vector_store(all_chunks)
