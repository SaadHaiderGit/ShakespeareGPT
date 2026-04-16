# Rebuilds FAISS index using HuggingFace local embeddings (no Ollama dependency for retrieval)
# Saves to shakespeare_docs_hf/ — run alongside store_docs.py to compare both indexes
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import time

# all-MiniLM-L6-v2: fast, in-process, no network call at query time (~50ms vs ~2s for Ollama)
# Swap to "sentence-transformers/all-mpnet-base-v2" for higher accuracy at ~2x the size
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OUTPUT_DIR  = "shakespeare_docs_hf"

folder_path = "./docs"
documents = []

for file in os.listdir(folder_path):
    if file.endswith(".txt"):
        file_path = os.path.join(folder_path, file)
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())
            print("Loading:", file)
        except Exception as e:
            print("Failed to load:", file, e)

splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
chunks = splitter.split_documents(documents)
print(f"Split into {len(chunks)} chunks.")

print(f"Embedding with {EMBED_MODEL} (downloads on first run, cached after)...")
start = time.time()
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
vectorstore = FAISS.from_documents(chunks, embeddings)
elapsed = (time.time() - start) / 60

print(f"Done in {elapsed:.1f} minutes. Saving to {OUTPUT_DIR}/")
vectorstore.save_local(OUTPUT_DIR)
print("Index saved. To use it, update tools.py to load from shakespeare_docs_hf/ with HuggingFaceEmbeddings.")
