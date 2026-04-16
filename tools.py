from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load HuggingFace index — in-process embeddings, no Ollama round-trip at query time
vectorstore = FAISS.load_local(
    "shakespeare_docs_hf",
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    allow_dangerous_deserialization=True
)

def doc_search(query: str) -> str:
    results = vectorstore.similarity_search(query, k=3)
    return "\n\n".join(r.page_content for r in results) if results else "No relevant information found."
