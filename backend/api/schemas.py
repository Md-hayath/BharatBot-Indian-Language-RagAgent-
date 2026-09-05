from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"
    document: str = ""


class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    detected_language: str


class UploadResponse(BaseModel):
    message: str
    chunks_added: int
    filename: str


class DocumentListResponse(BaseModel):
    documents: List[str]