# Implement agent planning + tool-use here.
# Agent orchestrator - combine retriever + model + tools.
# orchestration logic
# app/agent.py
from app.retriever import retrieve

def run_agent(query, vectordb, tools=None, k=3):
    """
    Offline agent orchestrator:
    - Retrieves top-k relevant documents (hybrid BM25 + vector)
    - Uses simple tools like prices.json if query mentions 'price'
    - Returns a text answer combining context + tool output
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
    answer = f"Context (first 500 chars): {context[:500]}...\nAnswer based on retrieved documents.{tool_output}"
    return answer
