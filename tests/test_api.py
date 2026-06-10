from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_chat():
    res = client.post("/chat", json={"query": "hello", "session_id": "t1"})
    assert res.status_code == 200
    assert "response" in res.json()