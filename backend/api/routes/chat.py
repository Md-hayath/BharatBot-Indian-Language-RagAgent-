from fastapi import APIRouter
from api.schemas import ChatRequest, ChatResponse
from agents.graph import bharatbot_app

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    state = {
        "messages": [],
        "query": request.query,
        "query_language": "",
        "retrieved_docs": [],
        "sources": [],
        "response": "",
        "session_id": request.session_id
    }
    config = {"configurable": {"thread_id": request.session_id}}
    result = bharatbot_app.invoke(state, config)

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
        detected_language=result["query_language"]
    )