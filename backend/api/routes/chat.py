from fastapi import APIRouter, Request
from api.schemas import ChatRequest, ChatResponse
from api.limiter import limiter
from config.settings import RATE_LIMIT_CHAT
from agents.graph import bharatbot_app

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT_CHAT)
async def chat(request: Request, body: ChatRequest):
    state = {
        "messages": [],
        "query": body.query,
        "query_language": "",
        "retrieved_docs": [],
        "sources": [],
        "response": "",
        "session_id": body.session_id,
        "selected_document": body.document
    }
    config = {"configurable": {"thread_id": body.session_id}}
    result = bharatbot_app.invoke(state, config)

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
        detected_language=result["query_language"]
    )
