# app/agent.py
import time
from app.retriever import retrieve

def run_agent(query, vectordb, tools=None, k=3):
    """
    Run offline RAG agent for a single query.

    Returns:
    - answer_text (str)
    - retrieved_chunks (list of dicts, unique)
    - tool_outputs (dict)
    - metrics (dict)
    """
    metrics = {}
    start_total = time.time()

    # --- Retrieval ---
    start_retrieval = time.time()
    retrieved_chunks = retrieve(query, vectordb, k=k)

    # --- Remove duplicates based on content ---
    unique_seen = set()
    unique_chunks = []
    for c in retrieved_chunks:
        content_hash = hash(c['context'])
        if content_hash not in unique_seen:
            unique_seen.add(content_hash)
            unique_chunks.append(c)
    retrieved_chunks = unique_chunks

    metrics['retrieval_time_ms'] = round((time.time() - start_retrieval) * 1000, 2)

    # --- Tool execution ---
    tool_outputs = {}
    tool_calls_count = 0
    if tools:
        for tool_name, tool_func in tools.items():
            # Define keywords that trigger this tool
            trigger_keywords = [tool_name.lower()]
            if tool_name.lower() == "prices":
                trigger_keywords += ["price", "prices", "eurusd"]

            # Trigger tool only if at least one keyword appears in the query
            if any(kw in query.lower() for kw in trigger_keywords):
                start_tool = time.time()
                try:
                    output = tool_func(query)
                    tool_outputs[tool_name] = output
                    tool_calls_count += 1
                    metrics[f"{tool_name}_latency_ms"] = round((time.time() - start_tool) * 1000, 2)
                except Exception as e:
                    tool_outputs[tool_name] = f"Tool failed: {str(e)}"
                    tool_calls_count += 1
                    metrics[f"{tool_name}_latency_ms"] = None

    # --- Compose professional answer ---
    if tool_outputs:
        answer_text = f"Tool-triggered answer:\n{tool_outputs}"
    else:
        answer_text = "Answer based on retrieved documents."

    # --- Metrics ---
    metrics['retrieved_chunks'] = len(retrieved_chunks)
    # Count unique source files only
    metrics['sources_cited'] = len(set(c['source_file'] for c in retrieved_chunks))
    metrics['tool_calls'] = tool_calls_count
    metrics['total_time_ms'] = round((time.time() - start_total) * 1000, 2)

    return answer_text, retrieved_chunks, tool_outputs, metrics
