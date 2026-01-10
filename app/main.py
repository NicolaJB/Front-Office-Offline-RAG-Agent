# app/main.py
"""
Offline RAG Agent - Main Entry Point

This script provides an interactive offline Retrieval-Augmented Generation (RAG) agent
for financial documents. Users can query the system for insights based on ingested
documents and also retrieve tool-specific data, e.g., EURUSD prices.

Features:
- Loads and splits documents into chunks, attaching source-aware metadata.
- Builds a TF-IDF vectorstore and a BM25 retriever for semantic search.
- Highlights query terms in retrieved document snippets (red bold in terminal).
- Truncates displayed snippets to the last complete sentence within a max length.
- Invokes tools (like price lookup) alongside document retrieval.
- Displays metrics for retrieval and tool latency.
- Handles Ctrl+C gracefully for clean exit.
"""

import re
from app.ingest import load_and_split_docs, build_vectorstore
from app.agent import run_agent
from app.retriever import build_bm25
from app.tools.prices import get_price

# --- Utility to highlight query terms in terminal ---
# Highlights each query term (single or multi-word) in red bold using ANSI escape codes
def highlight_terms(text, query):
    terms = query.strip().split()
    terms = sorted(terms, key=len, reverse=True)  # longer phrases first
    terms = [re.escape(t) for t in terms]        # escape regex special characters
    pattern = r'(' + '|'.join(terms) + r')'
    highlighted = re.sub(pattern, '\033[1;31m\\1\033[0m', text, flags=re.IGNORECASE)
    return highlighted

# --- Utility to truncate snippet to last complete sentence within max length ---
def truncate_to_sentence(text, max_len=500):
    """
    Truncate text to max_len characters, but cut at the last full sentence (., !, ?) if possible.
    """
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    trunc = text[:max_len]
    last_period = max(trunc.rfind("."), trunc.rfind("!"), trunc.rfind("?"))
    if last_period > 0:
        return trunc[:last_period+1]
    return trunc  # fallback if no sentence-ending punctuation found

if __name__ == "__main__":
    print("Loading and splitting documents...")
    chunks = load_and_split_docs()

    # Report ingestion results
    num_docs = len(set(c.metadata.get("source", "") for c in chunks))
    num_chunks = len(chunks)
    print(f"Loaded {num_docs} documents, split into {num_chunks} chunks.")

    vectordb = build_vectorstore(chunks)
    print(f"Vectorstore created with {num_chunks} embeddings.")

    build_bm25(chunks)

    tools = {"prices": get_price}

    print("\n=== Offline RAG Agent Ready ===\n")

    # --- Main interactive loop wrapped in try/except for graceful Ctrl+C exit ---
    try:
        while True:
            query = input("Enter your financial query (or 'exit'): ")
            if query.lower() == "exit":
                break

            # Run agent
            answer, retrieved_chunks, tool_outputs, metrics = run_agent(query, vectordb, tools=tools, k=3)

            # --- Display retrieved context ---
            print("\n--- Retrieved Context ---\n")
            seen_snippets = set()
            for chunk in retrieved_chunks:
                snippet = truncate_to_sentence(chunk['context'], max_len=500)
                if snippet in seen_snippets:
                    continue
                seen_snippets.add(snippet)

                snippet_highlighted = highlight_terms(snippet, query)

                source_file = chunk['source_file'].split("/")[-1]
                chunk_index = chunk.get('place_within_source', chunk.get('chunk', 'unknown'))

                print(f"SOURCE FILE: {source_file}")
                print(f"CHUNK INDEX: {chunk_index}")
                print(f"CONTEXT: {snippet_highlighted}\n")

            # --- Display answer / tool outputs ---
            print("--- Answer / Tool Output ---\n")
            if tool_outputs:
                for tool_name, output in tool_outputs.items():
                    print(f"[Tool: {tool_name}] {output}")
            else:
                print(answer)

            # --- Display metrics ---
            print("\n--- Metrics ---")
            for k, v in metrics.items():
                if v is None:
                    continue  # skip None values
                print(f"{k}: {v}")

            print("\n---------------\n")

    except KeyboardInterrupt:
        print("\n\nExiting RAG agent. Goodbye!")
