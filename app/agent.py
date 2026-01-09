# app/agent.py
# Agent orchestration logic (combine retriever + model + tools)

# Note:
# This agent returns grounded answers using retrieved context and tools only.
# LLM-based answer generation was intentionally excluded for offline reproducibility.

from app.retriever import retrieve
from app.observability import init_metrics, finalize_metrics, format_metrics

import time

def format_citations(docs):
    """
    Build a formal Sources section from retrieved documents.
    """
    lines = []
    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata or {}
        source = meta.get("source", "unknown")
        source_type = meta.get("source_type")

        if source_type == "pdf" and meta.get("page") is not None:
            location = f"page {meta['page']}"
        elif source_type == "csv" and meta.get("row") is not None:
            location = f"row {meta['row']}"
        elif meta.get("chunk_id") is not None:
            location = f"chunk {meta['chunk_id']}"
        else:
            location = "unknown location"

        lines.append(f"[{i}] {source} — {location}")

    return "Sources:\n" + "\n".join(lines) if lines else "Sources:\n(no sources retrieved)"

def run_agent(query, vectordb, tools=None, k=3, verbose=True):
    """
    Offline RAG agent orchestrator with modular observability.
    Returns string with context snippet, tool output, citations, and optional metrics.
    """
    start_time = time.time()
    metrics = init_metrics()

    # Step 1: Retrieve relevant documents
    t0 = time.time()
    docs = retrieve(query, vectordb, k=k)
    metrics["retrieval_time_ms"] = round((time.time() - t0) * 1000, 2)
    metrics["num_retrieved_chunks"] = len(docs)

    context = "\n".join([d.page_content for d in docs])

    # Step 2: Use tools if relevant
    tool_output = ""
    if tools and "prices" in tools and "price" in query.lower():
        t_tool = time.time()
        try:
            price_result = tools["prices"](query)
            tool_output = f"\n\n[Price Tool Output]: {price_result}"
            metrics["tool_calls"]["prices"] += 1
        except Exception as e:
            tool_output = f"\n\n[Price Tool Error]: {str(e)}"
        metrics["tool_prices_ms"] = round((time.time() - t_tool) * 1000, 2)

    # Step 3: Build answer text
    answer_text = (
        f"Context (first 500 chars): {context[:500]}...\n"
        f"Answer based on retrieved documents.{tool_output}"
    )

    # Step 4: Append formal citations
    citations = format_citations(docs)
    metrics["num_sources"] = len(docs)

    # Step 5: Finalise and format metrics
    metrics = finalize_metrics(metrics, start_time)
    metrics_block_str = format_metrics(metrics, verbose=verbose)

    return f"{answer_text}\n\n{citations}{metrics_block_str}"
