from agents.graph import bharatbot_app

def test_no_docs_response():
    state = {
        "messages": [], "query": "Hello",
        "query_language": "", "retrieved_docs": [],
        "sources": [], "response": "", "session_id": "test-1"
    }
    result = bharatbot_app.invoke(state, {"configurable": {"thread_id": "test-1"}})
    assert result["response"] != ""