# app/ingest.py
"""
Document ingestion and vectorstore construction.

- Load TXT, HTML, Markdown, CSV, PDF
- Split into chunks
- Attach metadata (source file, chunk index)
- Build TF-IDF vectorstore
"""

import os
import csv
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
from pypdf import PdfReader

@dataclass
class Document:
    page_content: str
    metadata: dict

TEXT_EXTENSIONS = (".txt", ".html", ".md")
CSV_EXTENSIONS = (".csv",)
PDF_EXTENSIONS = (".pdf",)

def load_and_split_docs(data_dir="data", chunk_size=500):
    docs = []

    for root, _, files in os.walk(data_dir):
        for fname in files:
            if fname.startswith("."):
                continue
            path = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()

            text = ""

            if ext in PDF_EXTENSIONS:
                try:
                    reader = PdfReader(path)
                    text = "\n".join(page.extract_text() or "" for page in reader.pages)
                except Exception as e:
                    print(f"Failed to read PDF {path}: {e}")
                    continue

            elif ext in CSV_EXTENSIONS:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        reader = csv.reader(f)
                        rows = [", ".join(row) for row in reader]
                        text = "\n".join(rows)
                except Exception as e:
                    print(f"Failed to read CSV {path}: {e}")
                    continue

            elif ext in TEXT_EXTENSIONS:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    if ext == ".html":
                        soup = BeautifulSoup(text, "lxml")
                        text = soup.get_text(separator="\n")
                except Exception as e:
                    print(f"Failed to read {ext} file {path}: {e}")
                    continue
            else:
                continue  # skip unsupported files

            # Split into chunks
            for i in range(0, len(text), chunk_size):
                chunk_text = text[i:i+chunk_size].strip()
                if not chunk_text:
                    continue
                docs.append(
                    Document(
                        page_content=chunk_text,
                        metadata={
                            "source": path,
                            "chunk": i // chunk_size + 1
                        }
                    )
                )
    return docs


def build_vectorstore(docs):
    """Build a TF-IDF vectorstore from document chunks"""
    vectorizer = TfidfVectorizer(stop_words="english")
    embeddings = vectorizer.fit_transform([d.page_content for d in docs])
    return {
        "vectorizer": vectorizer,
        "embeddings": embeddings,
        "docs": docs
    }
