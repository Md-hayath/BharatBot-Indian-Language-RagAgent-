from langchain.tools import tool
from ingestion.embedder import embed_query
from ingestion.vector_store import search, has_documents
from config.settings import TOP_K_RESULTS


@tool
def search_documents(query: str) -> str:
    """Search uploaded documents for relevant information."""
    if not has_documents():
        return "No documents uploaded yet."

    q_vec = embed_query(query)
    results = search(q_vec, TOP_K_RESULTS)

    if not results:
        return "No relevant content found."

    return "\n\n---\n\n".join(f"[Source: {source}]\n{text}" for text, source in results)
