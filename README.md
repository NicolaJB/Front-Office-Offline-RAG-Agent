# Offline RAG Agent

An offline Retrieval-Augmented Generation (RAG) agent for financial documents. Combines vector embeddings and BM25 keyword search to retrieve context from local documents, and supports simple tool integration (e.g., financial price lookups).

## Features
- Load documents from the data/ folder: .txt, .pdf, .html, .csv
- Split documents into overlapping chunks for retrieval
- Vector-based retrieval using Sentence Transformers
- Keyword-based retrieval using BM25
- Hybrid retrieval (combining vector and BM25 results)
- Offline “answer generation” with context snippet
- Tool integration for custom queries (e.g., stock prices)
- Fully offline – no cloud dependencies required

## Grounded, Cited Answers

This offline RAG agent retrieves the most relevant document chunks for a query, calls the prices.json tool when appropriate, and appends a formal Sources section showing file names and locations. Answers are thus grounded and traceable. A placeholder in agent.py indicates where an LLM could be integrated to rewrite the answer in natural language with automatic citations. Example output includes context, tool results, and numbered sources, ensuring clarity and reproducibility for financial queries.

Example output for query stock price of AAPL:
```
Context (first 500 chars): red.
Benchmark: SPY; QQQ referenced for context only.
Risk model: simplified style proxies for demonstration.
...
Answer based on retrieved documents.

[Price Tool Output]: AAPL: [{'date': '2025-06-01', 'close': 210.12}, ... ]

Sources:
[1] data/fund_letters/q2_letter.html — unknown location
[2] data/fund_letters/q2_letter.html — unknown location
[3] data/fund_letters/q2_letter.html — unknown location
```

## Folder Structure
```
rag-agent-exercise/
├─ app/
│  ├─ __init__.py
│  ├─ main.py           # Entry point
│  ├─ ingest.py         # Document loading and vectorstore
│  ├─ retriever.py      # Vector + BM25 retrieval
│  ├─ agent.py          # Query handling & answer generation
│  └─ tools/
│     └─ prices.py      # Example tool for stock prices
├─ data/                # Place your documents here
│  ├─ fund_letters/
│  │  └─ q2_letter.ht...
│  └─ ...
├─ backend/
│  └─ venv/             # Python virtual environment
└─ README.md
```
## Setup
Clone the repository:
```bash
git clone https://github.com/NicolaJB/rag-agent-exercise.git
cd rag-agent-exercise
```
Create and activate a virtual environment:
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
```

Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Dependencies

### Core numerical / ML libraries
These are required for embeddings, vector similarity, and ML pipelines:
- numpy>=1.25.2,<2.6
- scipy>=1.11
- scikit-learn==1.8.0
- sentence-transformers==5.2.0
- huggingface_hub<1.0

### PDF / document processing
Used for reading, cleaning, and ranking text documents:
- pypdf==6.5.0
- beautifulsoup4==4.14.3
- nltk==3.9.2
- rank_bm25==0.2.2
- pandas==2.3.3

### Optional / web & API
For potential API or web interface integration:
- fastapi==0.128.0
- uvicorn==0.40.0
- tiktoken==0.12.0

⚠️ Ensure your virtual environment is activated before running the project.

## Running the Agent:
```bash
python3 -m app.main
```

- The agent will load and split documents into chunks.
- Builds vectorstore and BM25 model.


Enter financial queries when prompted:

```bash
Enter your financial query (or 'exit'): stock price of AAPL
```

Results include:

- Top retrieved document chunks
- Context snippet (first 500 characters)
- Tool outputs (e.g., stock prices)

Example Output:
```
Loading and splitting documents...
Loaded 3 documents, split into 11 chunks.
Vectorstore created with 11 embeddings.

=== Offline RAG Agent Ready ===

Enter your financial query (or 'exit'): stock price of AAPL
Vector Top-1: data/fund_letters/q2_letter.ht...
Vector Top-2: data/fund_letters/q2_letter.ht...
Vector Top-3: data/fund_letters/q2_letter.ht...

--- Answer ---
Context (first 500 chars): red. Benchmark: SPY; QQQ referenced for context only...
Answer based on retrieved documents.

[Price Tool Output]: AAPL: [{'date': '2025-06-01', 'close': 210.12}, ...]
```

## Notes
- The Document class is custom for offline usage, avoiding langchain_core.
- Hybrid retrieval combines vector similarity and BM25 keyword search.
- Tool integration is modular – add new tools under app/tools/.
- Designed for offline evaluation, but the vectorstore can scale with more documents.
- Ensure NumPy, SciPy, and scikit-learn versions are compatible to avoid runtime errors.

## Future Improvements
- Use an actual language model for answer generation
- Add caching of embeddings for faster startup
- Expand hybrid retrieval weighting between BM25 and vectors
- Improve context formatting and truncation for better readability