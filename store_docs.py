from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import os
import time

# Load and split the documents
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
            print("Failed to load:", file)
            print(e)

start = time.time()

splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
chunks = splitter.split_documents(documents)

# Embed using local Ollama embedding model, then store in FAISS for later use
embeddings = OllamaEmbeddings(model="nomic-embed-text")
print("Storing documents as vectors. This may take many minutes/hours depending on their size, please keep this in mind.")

vectorstore = FAISS.from_documents(chunks, embeddings)

# embedding step
print("DONE! Time it took:", (time.time() - start) / 60, "minutes")
vectorstore.save_local("shakespeare_docs")
