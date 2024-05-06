from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

ollama = Ollama(base_url="http://localhost:11434", model="llama3")

loader = WebBaseLoader('https://www.cnn.com/')
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_chunks = text_splitter.split_documents(data)

vectore_store = Chroma.from_documents(documents=all_chunks, embedding=GPT4AllEmbeddings())

system_prompt = (
    "Using the retrieved documents, answer the questions asked. "
    "add the links to the news. "
    "Context: {context}. "
)

print(system_prompt)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{context}")
    ]
)

doc_combination_chain = create_stuff_documents_chain(ollama, prompt)
full_chain = create_retrieval_chain(vectore_store.as_retriever(), doc_combination_chain)

query = "What are the most important news on CNN.com?"
result = full_chain.invoke({"input": query})
print(result)

query = "What are the most important news about Iran?"
result = full_chain.invoke({"input": query})
print(result)
