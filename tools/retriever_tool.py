import os
import faiss
import pickle
import numpy as np
from langchain.tools import tool
from ingestion.embedder import embed_query
from config.settings import INDEX_FILE, META_FILE, TOP_K_RESULTS


@tool
def search_documents(query: str) -> str:
    """Search uploaded documents for relevant information."""
    if not os.path.exists(INDEX_FILE):
        return "No documents uploaded yet."

    q_vec = embed_query(query).astype("float32").reshape(1, -1)
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        metadata = pickle.load(f)

    _, indices = index.search(q_vec, TOP_K_RESULTS)
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(metadata):
            m = metadata[idx]
            results.append(f"[Source: {m['source']}]\n{m['text']}")

    return "\n\n---\n\n".join(results) if results else "No relevant content found."