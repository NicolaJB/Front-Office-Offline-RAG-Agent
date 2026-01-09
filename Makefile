# Ingest documents into vectorstore (Qdrant or local store)
ingest:
	python -m app.ingest  # runs the ingestion script that loads PDFs, HTML, CSVs, etc.

# Run the offline RAG agent (interactive prompt)
run:
	@echo "Running offline RAG agent..."
	python3 -m app.main   # replaced uvicorn; no FastAPI server needed

# Run unit tests
test:
	pytest -q             # quiet pytest output for CI-style feedback

# Run the evaluation harness
eval:
	python eval/run_eval.py  # runs simple eval on your agent responses
