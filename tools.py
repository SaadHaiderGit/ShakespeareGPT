from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# Load vectorstore once at import time; k=3 returns broader context per query
vectorstore = FAISS.load_local("shakespeare_docs", OllamaEmbeddings(model="nomic-embed-text"), allow_dangerous_deserialization=True)

def doc_search(query: str) -> str:
    results = vectorstore.similarity_search(query, k=3)
    return "\n\n".join(r.page_content for r in results) if results else "No relevant information found."
