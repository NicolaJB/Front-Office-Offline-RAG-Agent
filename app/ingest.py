# app/ingest.py
import os
import pandas as pd
from bs4 import BeautifulSoup
from pypdf import PdfReader

# Simple offline Document class
class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

DATA_DIR = "data"

def load_text_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def load_and_split_docs(data_dir=DATA_DIR, chunk_size=500, chunk_overlap=50):
    docs = []

    for root, _, files in os.walk(data_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            text = None

            if filename.endswith(".txt"):
                text = load_text_file(filepath)
            elif filename.endswith(".pdf"):
                reader = PdfReader(filepath)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
            elif filename.endswith(".html") or filename.endswith(".htm"):
                with open(filepath, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "lxml")
                    text = soup.get_text()
            elif filename.endswith(".csv"):
                df = pd.read_csv(filepath)
                text = "\n".join(df.astype(str).agg(" | ".join, axis=1))
            else:
                continue

            if text:
                docs.append(Document(page_content=text, metadata={"source": filepath}))

    # Split documents into chunks
    chunks = []
    for doc in docs:
        text = doc.page_content
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunks.append(Document(page_content=chunk_text, metadata=doc.metadata))
            start += chunk_size - chunk_overlap

    print(f"Loaded {len(docs)} documents, split into {len(chunks)} chunks.")
    return chunks

def build_vectorstore(chunks):
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np

    texts = [doc.page_content for doc in chunks]
    vectorizer = TfidfVectorizer()
    embeddings = vectorizer.fit_transform(texts)  # sparse matrix

    vectordb = {"vectorizer": vectorizer, "embeddings": embeddings, "docs": chunks}
    print(f"Vectorstore created with {len(chunks)} embeddings.")
    return vectordb
