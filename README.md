# Front Office Offline RAG Agent
An interactive offline Retrieval-Augmented Generation (RAG) agent for financial documents.
It combines semantic vector search (TF-IDF) with keyword-based BM25 retrieval, supports modular tools, and prints lightweight runtime metrics.

## Features
- **Hybrid retrieval**: TF-IDF embeddings + BM25 keyword search.
- Handles queries that embeddings alone may miss (numbers, tickers, rare terms).
- Deduplicates overlapping chunks and ensures top-k results are unique for accurate citations.

## Answer Generation
- Returns relevant context, tool outputs (e.g., price lookup), and sources.
- Terminal displays first 500 characters of context; full answers logged.

## Modular Tools
Add tools under app/tools/ and update mapping in app/main.py.
- Example: price tool triggered for queries containing "price".

## Lightweight Observability
Per-query metrics: retrieval latency, tool runtime, sources cited.

## Project Structure
```
rag-agent-exercise/
├─ app/
│  ├─ main.py            # CLI entrypoint: orchestrates ingestion, retrieval, and agent execution
│  ├─ agent.py           # Offline RAG agent: retrieves documents, calls tools, formats citations & metrics
│  ├─ ingest.py          # Document loading, splitting into chunks, and vectorstore creation (TF-IDF)
│  ├─ retriever.py       # Hybrid retrieval (TF-IDF + BM25), deduplicates overlapping chunks, ensures top-k results are unique
│  ├─ observability.py   # Lightweight per-query metrics: init, finalise, format for CLI output
│  └─ tools/
│     └─ prices.py       # Price lookup tool from stub JSON for queries containing "price"
├─ backend/
│  ├─ test_main.py       # Offline test harness: verifies ingestion, vectorstore, BM25, and query pipeline
│  └─ requirements.txt   # Python dependencies
├─ eval/
│  ├─ queries.jsonl      # Sample evaluation queries
│  └─ run_eval.py        # Evaluation harness: runs agent on queries.jsonl, logs full answers to eval/full_eval_output.txt
├─ data/                 # Required: fund_letters/, addendum.pdf, chat_logs/
│  └─ optional: analyst_notes/, glossary/, sample_prices/
├─ prices_stub/
│  └─ prices.json        # Stub data for the price lookup tool
├─ Dockerfile / Makefile # Optional automation for ingestion, building, or containerised execution
├─ .env.example          # Template for environment configuration (optional keys for OpenAI, Qdrant, embeddings, **not required**)
└─ README.md             # Project overview, installation, features, usage, and evaluation instructions
```
*Notes on structure*:
- The agent runs fully offline, with no external services required.
- Hybrid retrieval combines vector-based TF-IDF with BM25 keyword search for robust query handling.
- Modular design allows easy addition of new tools (app/tools/) or new document types (app/ingest.py).
- Metrics and evaluation are captured per query, and full outputs are logged for inspection (eval/full_eval_output.txt).

- **prompts/answer_system.txt** — provided in the original scaffold for LLM-based prompting; not used by the offline agent. Included for reference or potential future extensions.
- **docker/directory** included as provided in the original scaffold with a placeholder docker-compose.yml; not used by the offline agent and not required for local execution.

## Getting Started
Although the scaffold provided for the task includes Docker and Make targets, this implementation runs fully offline and can be executed directly via the Python CLI.

### Installation

*Prerequisites:*
- **Python 3.11** (older versions may require dependency adjustments)
- **pip, venv** (standard Python tools)
- **Data files:** Make sure the data/ folder contains all PDFs, CSVs, and HTML files needed by the agent

1. Clone the repository:
```bash
git clone https://github.com/NicolaJB/Front-Office-RAG-Agent-Exercise
```
2. Navigate into the project folder. Note: If you cloned from GitHub, the folder will be named 'Front-Office-RAG-Agent-Exercise':
```bash
cd <project-folder>
```
3. Create and activate a Python 3.11 virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # Mac/Linux
# For Windows: venv\Scripts\activate
```
4. Upgrade pip, wheel, and setuptools:
```bash
pip install --upgrade pip wheel setuptools
```
5. Install project dependencies:
```bash
pip install -r backend/requirements.txt
```
*Note: lxml should install automatically from precompiled wheels. On macOS, installation errors are rare, but if they occur, you may need the required libraries. Ensure Homebrew is installed, then run:*
```bash
# Optional, macOS only
brew install libxml2 libxslt
pip install lxml --force-reinstall
```
6. Start the Offline RAG Agent:
```bash
python -m app.main
```
### Data

#### Required
- `fund_letters/` — Fund research letters (`.html` and `.pdf`)
- `chat_logs/` — Internal desk chat logs (`.csv`)

#### Optional
- `analyst_notes/`
- `glossary/`
- `sample_prices/`

Optional folders demonstrate ingestion of additional document types; the agent runs fully with the required data only.

#### Text Sanitisation
All documents are cleaned and chunked to remove parsing artifacts, ensuring coherent context in CLI output.

#### Error Handling
Error handling is intentionally minimal: malformed or unsupported queries may return empty or partial results. This is a deliberate design trade-off to keep the implementation concise, fully offline, and suitable as a junior-level exercise.

## Interactive CLI/Terminal Usage Example
- Uses hybrid retrieval (TF-IDF semantic ranking + BM25 keyword matching).
- Displays the top retrieved sources, per-query metrics, and any triggered tools (e.g., price lookup).
- Only the first 500 characters of retrieved context are shown in the terminal for readability.
- Full context and answers are internally used and logged to eval/full_eval_output.txt.
- Tool calls are optional and modular; queries containing registered trigger keywords (such as "price") automatically invoke the corresponding tool.
**Example CLI Session: Price + Document Query**

Start the agent (as per the installation steps above):
```bash
python -m app.main
```
Initial startup output, ending with the user prompt (example query shown):
```
Loading and splitting documents...
Loaded 6 documents, split into 13 chunks.
Vectorstore created with 13 embeddings.

=== Offline RAG Agent Ready ===

Enter your financial query (or 'exit'):  EURUSD price and Q2 macro liquidity
```
Output after submitting the query (hybrid retrieval + tool invocation):
```
--- Retrieved Context ---

SOURCE FILE: q2_letter.html
CHUNK INDEX: 1
CONTEXT: Q2 Research Letter — Breadth, Factor Tilts, and Liquidity Q2 Research Letter Executive Summary... (truncated)

SOURCE FILE: sample_note.pdf
CHUNK INDEX: 1
CONTEXT: Subject: June 2025 Market Summary  This synthetic note summarizes market conditions for demonstration purposes... (truncated)

SOURCE FILE: q2_macro_addendum.pdf
CHUNK INDEX: 1
CONTEXT: Q2 Macro Addendum Purpose. This addendum clarifies positioning nuances from the primary Q2 letter... (truncated)

--- Answer / Tool Output ---

[Tool: prices] EURUSD: [{'date': '2025-06-01', 'close': 1.086}, {'date': '2025-06-10', 'close': 1.0785}, {'date': '2025-06-20', 'close': 1.0812}]

--- Metrics ---
retrieval_time_ms: 2.14
prices_latency_ms: 1.72
retrieved_chunks: 3
sources_cited: 3
tool_calls: 1
total_time_ms: 3.9
```
- Only the first 500 characters of retrieved context are shown in the terminal.
- **Full answers are only logged when running the evaluation harness (python -m eval.run_eval)**.
- Regular CLI usage (python -m app.main) does not write full answers to a file.

## Offline Test & Evaluation

**Quick Offline Test**
```bash
python -m backend.test_main
```
- Runs a small set of sample queries.
- Prints context, sources, and retrieval metrics.
- Confirms vectorstore and BM25 ingestion are working.

**Evaluation Harness**
```bash
python -m eval.run_eval
```
- Loads a set of example queries from eval/queries.jsonl.
- Prints truncated answers (first 500 chars) in the terminal.
- Logs full answers to eval/full_eval_output.txt for reference.
- **Important:** full_eval_output.txt captures the retrieval tuples with context, sources, and per-query metrics, but tool outputs (e.g., price lookups) are only displayed in the interactive CLI and do not appear in the evaluation log. This ensures the offline evaluation remains fully reproducible without external calls.

*Notes on evaluation and metrics:*
- Evaluation is manual: full answers are logged; no automated correctness scoring.
- Per-query metrics (retrieval time, tool latency, sources cited) are captured in the terminal and logs.
- Demonstrates a robust hybrid RAG pipeline with optional tool integration, suitable for the scope of the current exercise.

**Vector Storage**
- TF-IDF vectors stored in memory (sklearn.TfidfVectorizer)
- Combined with BM25 for hybrid retrieval 
- Optional: integrate Qdrant for persistent vector storage, scaling, or multi-user deployments
- CLI pipeline does not require Qdrant; included only for demonstration/optional scaling.

## Extending the Agent
- **Add tools:** app/tools/ + update app/main.py
- **Add data types:** extend app/ingest.py for new formats (PDF, CSV, HTML, text)
- **Metrics/logging:** captured per-query, can extend or redirect to logs

## Environment Configuration (.env)
These environment variables are optional (for extensions only) and not required to run the offline CLI agent:

- OPENAI_API_KEY — if connecting to an external LLM
- DEFAULT_MODEL — defaults to local embeddings, not used in offline CLI
- QDRANT_URL / QDRANT_COLLECTION — optional Qdrant database
- EMBED_MODEL — embedding model for vector representations
- HOST / PORT — relevant only for API server deployments
- LOG_DIR — directory for logs

Offline RAG agent runs fully without OpenAI, Qdrant, or a web server.
