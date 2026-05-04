import json
import pytest
from unittest.mock import MagicMock
from src.models.request import QueryRequest

def parse_sse(text: str):
    """Helper to parse SSE text into a list of (event, data) tuples."""
    events = []
    # Normalize line endings and split by double newline
    chunks = text.replace("\r\n", "\n").strip().split("\n\n")
    for chunk in chunks:
        lines = chunk.strip().split("\n")
        event_name = None
        data_content = None
        for line in lines:
            if line.startswith("event:"):
                event_name = line.replace("event:", "").strip()
            elif line.startswith("data:"):
                data_content = line.replace("data:", "").strip()
        if event_name:
            events.append((event_name, data_content))
    return events

@pytest.mark.asyncio
async def test_integration_safety_block(async_client, user_001):
    payload = {
        "query": "help me trade on this confidential merger news from my law firm",
        "user": user_001.model_dump(),
        "session_id": "test_session"
    }
    
    response = await async_client.post("/chat", json=payload)
    assert response.status_code == 200
    
    events = parse_sse(response.text)
    error_event = next((e for e in events if e[0] == "error"), None)
    assert error_event is not None
    assert "SAFETY_BLOCK" in error_event[1]

@pytest.mark.asyncio
async def test_integration_happy_path_portfolio_health(async_client, user_001, mock_llm_client):
    mock_llm_client.complete.return_value = json.dumps({
        "intent": "health_check",
        "agent": "portfolio_health",
        "entities": {},
        "safety_verdict": "safe",
        "confidence": 1.0
    })
    
    payload = {
        "query": "how is my portfolio doing?",
        "user": user_001.model_dump(),
        "session_id": "test_session_happy"
    }
    
    response = await async_client.post("/chat", json=payload)
    assert response.status_code == 200
    
    events = parse_sse(response.text)
    event_names = [e[0] for e in events]
    
    assert "metadata" in event_names
    assert "structured" in event_names
    assert "done" in event_names
    
    metadata = next(e for e in events if e[0] == "metadata")
    data = json.loads(metadata[1])
    assert data["agent"] == "portfolio_health"

@pytest.mark.asyncio
async def test_no_stack_trace_on_internal_error(async_client, user_001, monkeypatch):
    # Force an error that the pipeline catches (e.g., in safety check)
    monkeypatch.setattr("src.main.safety_check", MagicMock(side_effect=Exception("Top secret crash info")))
    
    payload = {
        "query": "cause a crash",
        "user": user_001.model_dump(),
        "session_id": "test_session_crash"
    }
    
    response = await async_client.post("/chat", json=payload)
    assert response.status_code == 200
    
    events = parse_sse(response.text)
    error_event = next((e for e in events if e[0] == "error"), None)
    assert error_event is not None
    data = json.loads(error_event[1])
    assert "Traceback" not in data["message"]
