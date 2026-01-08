# test_main.py
"""
Quick offline test for the RAG agent CLI.
Checks document ingestion, vectorstore, BM25, and query pipeline.
"""

from app.ingest import load_and_split_docs, build_vectorstore
from app.retriever import build_bm25
from app.agent import run_agent


def run_test():
    print("Loading and splitting documents...")
    chunks = load_and_split_docs()  # loads from data/

    print("Building vectorstore...")
    vectordb = build_vectorstore(chunks)

    print("Initializing BM25...")
    build_bm25(chunks)

    # Sample queries for testing
    test_queries = [
        "What are the key risks for JP Morgan in Q3 2024?",
        "Summarize Apple's revenue in the last quarter.",
        "List the latest Amazon logistics challenges."
    ]

    for query in test_queries:
        print("\n====================")
        print(f"Query: {query}")
        answer = run_agent(query, vectordb)
        print("\n--- Answer ---")
        print(answer)
        print("====================\n")


if __name__ == "__main__":
    run_test()
