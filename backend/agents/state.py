from typing import TypedDict, List


class BharatBotState(TypedDict):
    messages: List[dict]
    query: str
    query_language: str
    retrieved_docs: List[str]
    sources: List[str]
    response: str
    session_id: str
    selected_document: str