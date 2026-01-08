# Application entrypoint
# infrastructure (ingestion, retrieval, and agent execution) is wired together exactly, once.
# Goal - API or CLI interface
# app/main.py
# Application entrypoint (CLI)
from app.ingest import load_and_split_docs, build_vectorstore
from app.agent import run_agent
from app.retriever import build_bm25
from app.tools.prices import get_price

if __name__ == "__main__":
    print("Loading and splitting documents...")
    chunks = load_and_split_docs()
    vectordb = build_vectorstore(chunks)
    build_bm25(chunks)

    tools = {"prices": get_price}

    print("\n=== Offline RAG Agent Ready ===\n")
    while True:
        query = input("Enter your financial query (or 'exit'): ")
        if query.lower() == "exit":
            break
        answer = run_agent(query, vectordb, tools=tools)
        print("\n--- Answer ---\n")
        print(answer)
        print("\n---------------\n")
