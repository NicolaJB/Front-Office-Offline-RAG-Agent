# app/observability.py
"""Lightweight per-query metrics for offline RAG agent,
    optionally printed to CLI; fully offline, no external dependencies."""
import time
from collections import Counter

def init_metrics():
    """
    Initialize lightweight per-query metrics.
    """
    return {
        "retrieval_time_ms": 0.0,
        "tool_calls": Counter(),
        "num_retrieved_chunks": 0,
        "num_sources": 0,
        "tool_prices_ms": 0.0,
        "total_time_ms": 0.0,
    }

def finalize_metrics(metrics, start_time):
    """
    Finalize total_time_ms metric.
    """
    metrics["total_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return metrics

def format_metrics(metrics, verbose=True):
    """
    Return formatted metrics string for CLI output.
    """
    if not verbose:
        return ""

    metrics_block = (
        "\n\n--- Metrics ---\n"
        f"Retrieval time: {metrics.get('retrieval_time_ms', 0.0)} ms\n"
        f"Tool 'prices' latency: {metrics.get('tool_prices_ms', 0.0)} ms\n"
        f"Total time: {metrics.get('total_time_ms', 0.0)} ms\n"
        f"Retrieved chunks: {metrics.get('num_retrieved_chunks', 0)}\n"
        f"Sources cited: {metrics.get('num_sources', 0)}\n"
        f"Tool calls: {dict(metrics.get('tool_calls', {}))}"
    )
    return metrics_block
