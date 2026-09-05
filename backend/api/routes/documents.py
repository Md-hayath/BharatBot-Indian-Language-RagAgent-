from fastapi import APIRouter
from api.schemas import DocumentListResponse
from ingestion.vector_store import list_documents

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
async def get_documents():
    return DocumentListResponse(documents=list_documents())
