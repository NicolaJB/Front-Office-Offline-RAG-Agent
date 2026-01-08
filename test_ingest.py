# test_ingest.py
from app.ingest import load_and_split_docs, build_vectorstore

def main():
    print("Loading and splitting documents...")
    chunks = load_and_split_docs()
    print(f"Loaded {len(chunks)} chunks.")

    print("Building FAISS vectorstore...")
    vectordb = build_vectorstore(chunks)
    print("Vectorstore built successfully!")

    # Optional: test similarity search
    if len(chunks) > 0:
        query = "financial report"
        results = vectordb.similarity_search(query, k=3)
        print(f"Top 3 results for '{query}':")
        for i, doc in enumerate(results, start=1):
            print(f"{i}: {doc.page_content[:200]}...")  # print first 200 chars

if __name__ == "__main__":
    main()
