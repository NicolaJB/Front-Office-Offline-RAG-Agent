ingest:
	python -m app.ingest

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -q


eval:
	python eval/run_eval.py
