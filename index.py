from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate


def setup_ollama():
    """
    Sets up the Ollama object with the specified base URL and model.

    Returns:
        Ollama: The initialized Ollama object.
    """

    return Ollama(base_url="http://localhost:11434", model="llama3")


def load_data(loader):
    """
    Loads the data from the specified loader.
    params: loader: The loader object to load the data from.
    returns: The loaded data.
    """

    return loader.load()


def split_data(text_splitter, data):
    """
    Splits the data into chunks using the specified text splitter.
    params: text_splitter: The text splitter object to split the data with.
    params: data: The data to split.
    returns: The split data.
    """

    return text_splitter.split_documents(data)


def setup_vector_store(all_chunks):
    """
    Sets up the vector store with the specified chunks.
    params: all_chunks: The chunks to set up the vector store with.
    returns: The initialized vector store.
    """

    return Chroma.from_documents(documents=all_chunks, embedding=GPT4AllEmbeddings())


def setup_prompt():
    """
    Sets up the prompt for the chatbot.
    returns: The initialized ChatPromptTemplate object.
    """

    system_prompt = (
        "Using the retrieved documents, answer the questions asked. "
        "add the links to the news. "
        "Context: {context}. "
    )
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{context}")
        ]
    )


def setup_chains(ollama, prompt, vector_store):
    """
    Sets up the chains for the chatbot.
    params: ollama: The Ollama object to use.
    params: prompt: The prompt to use.
    params: vector_store: The vector store to use.
    returns: The full chain.
    """

    doc_combination_chain = create_stuff_documents_chain(ollama, prompt)
    return create_retrieval_chain(vector_store.as_retriever(), doc_combination_chain)


def query_chain(full_chain, query):
    """
    Queries the full chain with the specified query.
    params: full_chain: The full chain to query.
    params: query: The query to use.
    """

    result = full_chain.invoke({"input": query})
    print(result)


def read_file(file_path):
    """
    Reads the file at the specified path.
    params: file_path: The path to the file to read.
    returns: The contents of the file.
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def chunk_text(text, chunk_size):
    """
    Chunks the text into chunks of the specified size.
    params: text: The text to chunk.
    params: chunk_size: The size of the chunks.
    returns: The chunked text.
    """

    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def main():
    """
    The main function.
    """

    ollama = setup_ollama()
    loader = WebBaseLoader('https://www.cnn.com/')
    data = load_data(loader)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_chunks = split_data(text_splitter, data)
    vector_store = setup_vector_store(all_chunks)
    prompt = setup_prompt()
    full_chain = setup_chains(ollama, prompt, vector_store)
    query_chain(full_chain, "What are the most important news on CNN.com?")
    query_chain(full_chain, "How many news about Xin?")

if __name__ == "__main__":
    main()
