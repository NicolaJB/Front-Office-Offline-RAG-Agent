# Implement agent planning + tool-use here.
# Agent orchestrator - combine retriever + model + tools.
# orchestration logic
# app/agent.py
from app.retriever import retrieve

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
        elif meta.get("chunk_id") is not None:
            location = f"chunk {meta['chunk_id']}"
        elif meta.get("row") is not None:
            location = f"row {meta['row']}"
        else:
            location = "unknown location"

        lines.append(f"[{i}] {source} — {location}")

    if not lines:
        return "Sources:\n(no sources retrieved)"

    return "Sources:\n" + "\n".join(lines)

def run_agent(query, vectordb, tools=None, k=3):
    """
    Offline agent orchestrator:
    - Retrieves top-k relevant documents (hybrid BM25 + vector)
    - Uses simple tools like prices.json if query mentions 'price'
    - Returns a text answer combining context + tool output + formal citations
    """
    # Step 1: Retrieve relevant documents
    docs = retrieve(query, vectordb, k=k)
    context = "\n".join([d.page_content for d in docs])

    # Step 2: Use tools if relevant
    tool_output = ""
    if tools:
        if "prices" in tools and "price" in query.lower():
            try:
                price_result = tools["prices"](query)
                tool_output = f"\n\n[Price Tool Output]: {price_result}"
            except Exception as e:
                tool_output = f"\n\n[Price Tool Error]: {str(e)}"

    # Step 3: Generate offline "answer" (truncated context for readability)
    # NOTE: If in a full LLM-based implementation, could use a prompt like:
    # prompt = f"Answer the question based on the following context:\n{context}\n\nDo NOT invent sources; citations will be added automatically."
    # answer = llm.generate(prompt)  # pseudo-code for LLM call

    answer_text = f"Context (first 500 chars): {context[:500]}...\nAnswer based on retrieved documents.{tool_output}"

    # Step 4: Append formal citations
    citations = format_citations(docs)
    final_answer = f"{answer_text}\n\n{citations}"

    return final_answer

def run_agent(query, vectordb, tools=None, k=3):
    """
    Offline agent orchestrator:
    - Retrieves top-k relevant documents (hybrid BM25 + vector)
    - Uses simple tools like prices.json if query mentions 'price'
    - Returns a text answer combining context + tool output
    - Appends a formal Sources section
    """
    # Step 1: Retrieve relevant documents
    docs = retrieve(query, vectordb, k=k)
    context = "\n".join([d.page_content for d in docs])

    # Step 2: Use tools if relevant
    tool_output = ""
    if tools:
        if "prices" in tools and "price" in query.lower():
            try:
                price_result = tools["prices"](query)
                tool_output = f"\n\n[Price Tool Output]: {price_result}"
            except Exception as e:
                tool_output = f"\n\n[Price Tool Error]: {str(e)}"

    # Step 3: Build answer text
    # Note: placeholder prompt for LLM could go here
    # prompt = f"Answer the question based on the following context:\n{context}\n\nDo NOT invent sources; citations will be added automatically."

    answer_text = f"Context (first 500 chars): {context[:500]}...\nAnswer based on retrieved documents.{tool_output}"

    # Step 4: Append formal citations
    citations = format_citations(docs)
    answer_with_citations = f"{answer_text}\n\n{citations}"

    return answer_with_citations
