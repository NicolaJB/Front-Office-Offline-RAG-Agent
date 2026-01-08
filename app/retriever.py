# app/retriever.py - Implement hybrid/BM25+vector retrieval
# Supports semantic search via vectors and keyword search via BM25,
# where exact numbers, tickers, or terms might not be captured well by embeddings alone
# Retriever to combine classical IR (BM25, handling exact keyword matches, as against pure FAISS similarity search)
# with vector embeddings (handling semantic matches)
# app/retriever.py
from rank_bm25 import BM25Okapi
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

bm25_model = None
bm25_corpus = []

def build_bm25(docs):
    global bm25_model, bm25_corpus
    bm25_corpus = [doc.page_content.split() for doc in docs]
    bm25_model = BM25Okapi(bm25_corpus)

def retrieve(query, vectordb, k=3, hybrid=True):
    # Vector retrieval using TF-IDF
    vectorizer = vectordb["vectorizer"]
    embeddings = vectordb["embeddings"]
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, embeddings).flatten()
    top_vec_indices = sims.argsort()[-k:][::-1]
    vector_results = [vectordb["docs"][i] for i in top_vec_indices]

    if hybrid:
        global bm25_model, bm25_corpus
        if bm25_model is None:
            raise ValueError("BM25 not built. Call build_bm25 first.")

        query_tokens = query.split()
        bm25_scores = bm25_model.get_scores(query_tokens)
        top_bm25_indices = bm25_scores.argsort()[-k:][::-1]
        bm25_results = [vectordb["docs"][i] for i in top_bm25_indices if i < len(vectordb["docs"])]

        # Print top vector results
        for i, doc in enumerate(vector_results):
            print(f"Vector Top-{i + 1}: {doc.metadata.get('source', 'unknown')[:30]}...")

        # Merge and deduplicate
        combined = {doc.page_content: doc for doc in vector_results + bm25_results}
        return list(combined.values())[:k]

    return vector_results
