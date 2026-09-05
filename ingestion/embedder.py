import numpy as np
from openai import OpenAI
from config.settings import (
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT, EMBEDDING_DIM
)

_client = None


def get_client():
    global _client
    if _client is None:
        # Azure's unified v1 API endpoint (".../openai/v1") works directly
        # with the standard OpenAI client via base_url - no api_version needed.
        _client = OpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            base_url=AZURE_OPENAI_ENDPOINT,
        )
    return _client


def _embed(texts: list, batch_size: int = 100) -> np.ndarray:
    client = get_client()
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input=batch,
            dimensions=EMBEDDING_DIM,
        )
        vectors.extend(d.embedding for d in response.data)
    return np.array(vectors, dtype="float32")


def embed_chunks(chunks: list) -> np.ndarray:
    texts = [c["text"] for c in chunks]
    return _embed(texts)


def embed_query(query: str) -> np.ndarray:
    return _embed([query])[0]
