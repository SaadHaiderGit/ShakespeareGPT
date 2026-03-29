from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.load_local("shakespeare_docs", OllamaEmbeddings(model="nomic-embed-text"), allow_dangerous_deserialization = True)

def doc_search(query: str) -> str:
    results = vectorstore.similarity_search(query, k=1)
    return results[0].page_content if results else "No relevant information found."