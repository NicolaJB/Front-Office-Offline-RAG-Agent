# app/retriever.py
"""
Hybrid retriever with source-aware output.

Features:
- TF-IDF vector search + optional BM25 keyword search
- Weighted hybrid score
- Ensures top-k unique sources first
- Returns chunks with metadata for business-friendly display

Returned dict per chunk:
- source_file
- context
- place_within_source
- score
"""

from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity

bm25_model = None
bm25_corpus = []

def build_bm25(docs):
    """Build BM25 index from document chunks"""
    global bm25_model, bm25_corpus
    bm25_corpus = [doc.page_content.split() for doc in docs]
    bm25_model = BM25Okapi(bm25_corpus)

def retrieve(query, vectordb, k=3, hybrid=True, alpha=0.5, min_score_ratio=0.5):
    vectorizer = vectordb["vectorizer"]
    embeddings = vectordb["embeddings"]
    docs = vectordb["docs"]

    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, embeddings).flatten()

    if hybrid:
        global bm25_model
        if bm25_model is None:
            raise ValueError("BM25 not built. Call build_bm25 first.")
        query_tokens = query.split()
        bm25_scores = bm25_model.get_scores(query_tokens)
        combined_scores = alpha * sims + (1 - alpha) * bm25_scores
    else:
        combined_scores = sims

    threshold = min_score_ratio * combined_scores.max()
    candidates = [(i, combined_scores[i]) for i in range(len(combined_scores)) if combined_scores[i] >= threshold]
    candidates.sort(key=lambda x: x[1], reverse=True)

    selected = []
    sources_seen = set()

    # Unique sources first
    for idx, score in candidates:
        doc = docs[idx]
        source = doc.metadata.get("source", "unknown")
        if source not in sources_seen:
            selected.append({
                "source_file": source,
                "context": doc.page_content[:300].replace("\n", " "),
                "place_within_source": doc.metadata.get("chunk", "unknown"),
                "score": score
            })
            sources_seen.add(source)
        if len(selected) >= k:
            break

    # Fill remaining if needed
    if len(selected) < k:
        for idx, score in candidates:
            doc = docs[idx]
            source = doc.metadata.get("source", "unknown")
            if any(d['source_file'] == source and d['context'] == doc.page_content[:300] for d in selected):
                continue
            selected.append({
                "source_file": source,
                "context": doc.page_content[:300].replace("\n", " "),
                "place_within_source": doc.metadata.get("chunk", "unknown"),
                "score": score
            })
            if len(selected) >= k:
                break

    return selected
