import numpy as np
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL

_model = None

def get_model():
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_chunks(chunks: list) -> np.ndarray:
    model = get_model()
    texts = [f"passage: {c['text']}" for c in chunks]
    return model.encode(texts, show_progress_bar=True)

def embed_query(query: str) -> np.ndarray:
    model = get_model()
    return model.encode(f"query: {query}")