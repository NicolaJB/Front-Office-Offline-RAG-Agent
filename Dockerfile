# Dockerfile for offline RAG agent (CLI)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Run the CLI agent by default
CMD ["python", "-m", "app.main"]
# CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"] No FastAPI, no Uvicorn (no exposed ports needed)