import json
import pytest
from src.classifier.intent import classify
from tests.conftest import entities_match

@pytest.mark.asyncio
async def test_classifier_routing_accuracy(gold_classifier_queries, mock_llm_client, user_001):
    correct = 0
    for case in gold_classifier_queries:
        # Mock LLM to return the expected agent
        mock_llm_client.complete.return_value = json.dumps({
            "intent": "test",
            "agent": case["expected_agent"],
            "entities": case["expected_entities"],
            "safety_verdict": "safe",
            "confidence": 1.0
        })
        
        result = await classify(case["query"], user_001, llm_client=mock_llm_client)
        if result.agent == case["expected_agent"]:
            correct += 1
            
    accuracy = correct / len(gold_classifier_queries)
    assert accuracy >= 0.85

@pytest.mark.asyncio
async def test_entity_normalization(mock_llm_client, user_001):
    # Test case with ticker casing and suffix
    expected_entities = {"tickers": ["AAPL", "MSFT"]}
    mock_llm_client.complete.return_value = json.dumps({
        "intent": "research",
        "agent": "market_research",
        "entities": {"tickers": ["aapl.us", "MSFT"]},
        "safety_verdict": "safe",
        "confidence": 1.0
    })
    
    result = await classify("check apple and msft", user_001, llm_client=mock_llm_client)
    assert entities_match(expected_entities, result.entities.model_dump())

@pytest.mark.asyncio
async def test_follow_up_resolution(mock_llm_client, user_001):
    history = [
        {"query": "how is apple doing?", "agent": "market_research"}
    ]
    query = "what about microsoft?"
    
    mock_llm_client.complete.return_value = json.dumps({
        "intent": "research",
        "agent": "market_research",
        "entities": {"tickers": ["MSFT"]},
        "safety_verdict": "safe",
        "confidence": 1.0
    })
    
    await classify(query, user_001, history=history, llm_client=mock_llm_client)
    
    # Verify history was passed to LLM
    args, kwargs = mock_llm_client.complete.call_args
    messages = kwargs["messages"]
    assert any("how is apple doing?" in str(m) for m in messages)
