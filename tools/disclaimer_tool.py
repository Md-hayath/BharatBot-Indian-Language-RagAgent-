from langchain.tools import tool


@tool
def add_disclaimer(response: str, sources: list) -> str:
    """Appends source citations and disclaimer to a response."""
    source_block = ""
    if sources:
        source_block = "\n\n📄 Sources:\n" + "\n".join([f"  - {s}" for s in set(sources)])
    disclaimer = "\n\n---\n_Responses are based on uploaded documents. Please verify with original sources._"
    return response + source_block + disclaimer