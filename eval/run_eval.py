# app/eval/run_eval.py
"""
Basic evaluation harness for offline RAG agent responses.
- Iterates over a set of example queries loaded from eval/queries.jsonl
- Runs the agent with hybrid retrieval (BM25 + vector)
- Prints answers (truncated to first 500 chars) for manual inspection
- Logs full answers to eval/full_eval_output.txt
- Intended as a simple demonstration; no automated scoring implemented
"""
from app.ingest import load_and_split_docs, build_vectorstore
from app.agent import run_agent
from app.retriever import build_bm25
import json

def load_eval_queries(filepath="eval/queries.jsonl"):
    """Load evaluation queries from JSONL file."""
    queries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            queries.append(json.loads(line)["q"])
    return queries

EVAL_QUERIES = load_eval_queries()

FULL_OUTPUT_FILE = "eval/full_eval_output.txt"

def run_eval():
    if not EVAL_QUERIES:
        print("No evaluation queries found. Exiting.")
        return

    # Load documents and build vectorstore
    chunks = load_and_split_docs()
    vectordb = build_vectorstore(chunks)

    # Build BM25 index for hybrid retrieval
    build_bm25(chunks)

    print("=== Offline RAG Agent Evaluation ===")

    # Ensure output folder exists
    import os
    os.makedirs("eval", exist_ok=True)

    # Open file for full answers
    with open(FULL_OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for query in EVAL_QUERIES:
            print("\n----------------------------")
            print(f"Query: {query}")
            answer = run_agent(query, vectordb)

            # Truncate long answers for readability in terminal
            truncated_answer = answer if len(answer) <= 500 else answer[:500] + "..."
            print("--- Answer (first 500 chars, truncated if needed) ---")
            print(truncated_answer)
            print("----------------------------")

            # Write full answer to file
            f_out.write(f"Query: {query}\n")
            f_out.write(f"Full Answer:\n{answer}\n")
            f_out.write("-" * 80 + "\n")

    print(f"\nFull answers also saved to {FULL_OUTPUT_FILE}")

if __name__ == "__main__":
    run_eval()
