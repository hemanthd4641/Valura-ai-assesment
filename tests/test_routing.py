import pytest
from src.router import route, AGENT_REGISTRY
from src.models.classifier import ClassifierOutput, ExtractedEntities

@pytest.mark.asyncio
async def test_router_dispatches_to_all_agents(user_001):
    for agent_name in AGENT_REGISTRY.keys():
        classifier_output = ClassifierOutput(
            intent="test",
            agent=agent_name,
            entities=ExtractedEntities(),
            safety_verdict="safe",
            confidence=1.0
        )
        
        # Should not raise any exception
        response = await route(classifier_output, user_001)
        assert response is not None

@pytest.mark.asyncio
async def test_router_fallback_to_support(user_001):
    classifier_output = ClassifierOutput(
        intent="test",
        agent="non_existent_agent",
        entities=ExtractedEntities(),
        safety_verdict="safe",
        confidence=1.0
    )
    
    response = await route(classifier_output, user_001)
    assert response["agent"] == "customer_support"
    assert "not implemented" in response["message"].lower()
