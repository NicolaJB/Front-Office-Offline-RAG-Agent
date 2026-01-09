# Offline RAG Agent
An interactive offline Retrieval-Augmented Generation (RAG) agent for financial documents.
It combines semantic vector search (TF-IDF) with keyword-based BM25 retrieval, supports modular tools, and prints lightweight runtime metrics.

## Features
- **Hybrid retrieval**: TF-IDF embeddings + BM25 keyword search
- Handles queries that embeddings alone may miss (numbers, tickers, rare terms)
- Deduplicates overlapping chunks for accurate citations

## Answer generation
- Returns relevant context, tool outputs (e.g., price lookup), and sources
- Terminal displays first 500 characters of context; full answers logged

## Modular tools
- Add tools under app/tools/ and update mapping in app/main.py
Example: price tool triggered for queries containing "price"

## Lightweight observability
- Per-query metrics: retrieval latency, tool runtime, sources cited
- Fully offline, no external services required

## Installation
```bash
git clone https://github.com/NicolaJB/Front-Office-RAG-Agent-Exercise
cd rag-agent-exercise
pip install -r requirements.txt
```

## Data

Required:
- fund_letters/ — HTML fund letters
- addendum.pdf — PDF addendum
- chat_logs/ — CSV chat logs

Optional:
- analyst_notes/
- glossary/
- sample_prices/

The agent runs fully with required data; optional folders demonstrate ingestion of extra document types.

## Quick CLI Usage
```bash
python -m app.main
```
- Loads and splits documents from data/
- Builds in-memory TF-IDF vectorstore
- Initialises BM25 index for hybrid retrieval
- Starts interactive prompt; type 'exit' to quit

Example query session:
```
Enter your financial query (or 'exit'): price of MSFT

Vector Top-1: data/fund_letters/q2_letter.html...
Context (first 500 chars): ...
[Price Tool Output]: MSFT: [{'date': '2025-06-01', 'close': 410.5}, ...]
Sources: [1] data/fund_letters/q2_letter.html — chunk 16
--- Metrics ---
Retrieval time: 4.7 ms
Tool 'prices' latency: 0.76 ms
Total time: 5.5 ms
```

## Offline Test & Evaluation
Quick Offline Test:
```bash
python -m backend.test_main
```
- Checks document ingestion, vectorstore, BM25 index
- Executes sample queries through the agent
- Prints answers with context, sources, and retrieval metrics

## Evaluation Harness
```bash
python -m eval.run_eval
```
- Loads queries from eval/queries.jsonl
- Prints truncated answers (first 500 chars) in terminal
- Logs full answers to eval/full_eval_output.txt for reproducibility and inspection



## Usage Example
1. Interactive CLI
```bash
python -m app.main
```
```
=== Offline RAG Agent Ready ===
Enter your financial query (or 'exit'): price of MSFT
Vector Top-1: data/fund_letters/q2_letter.html
Context (first 500 chars): ...
[Price Tool Output]: MSFT: [{'date': '2025-06-01', 'close': 410.5}, ...]
Sources: [1] data/fund_letters/q2_letter.html — chunk 16
--- Metrics ---
Retrieval time: 4.7 ms
Tool 'prices' latency: 0.76 ms
Total time: 5.5 ms
Enter your financial query (or 'exit'):
```

2. Quick Offline Test
```bash
python -m backend.test_main
```
- Runs a small set of sample queries
- Prints context, sources, and retrieval metrics
- Confirms vectorstore and BM25 ingestion are working

3. Evaluation Harness
```bash
python -m eval.run_eval
```
- Loads queries from eval/queries.jsonl
- Prints truncated answers (first 500 chars) in terminal
- Logs full answers to eval/full_eval_output.txt for reference

## Vector Storage
- TF-IDF vectors stored in memory (sklearn.TfidfVectorizer)
- Combined with BM25 for hybrid retrieval 
- Optional: integrate Qdrant for persistent vector storage, scaling, or multi-user deployments
- CLI pipeline does not require Qdrant; included only for demonstration/optional scaling.

## Extending the Agent

- **Add tools:** app/tools/ + update app/main.py
- **Add data types:** extend app/ingest.py for new formats (PDF, CSV, HTML, text)
- **Metrics/logging:** captured per-query, can extend or redirect to logs

## Environment Configuration (.env)
Optional, for extensions only:

- OPENAI_API_KEY — if connecting to an external LLM
- DEFAULT_MODEL — defaults to local embeddings, not used in offline CLI
- QDRANT_URL / QDRANT_COLLECTION — optional Qdrant database
- EMBED_MODEL — embedding model for vector representations
- HOST / PORT — relevant only for API server deployments
- LOG_DIR — directory for logs

Offline RAG agent runs fully without OpenAI, Qdrant, or a web server.