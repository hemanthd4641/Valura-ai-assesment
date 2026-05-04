from typing import Any
from src.models.classifier import ExtractedEntities

def get_stub_response(agent_name: str, intent: str, entities: ExtractedEntities) -> dict[str, Any]:
    """
    Returns a structured 'not implemented' response for unimplemented agents.
    """
    return {
        "status": "not_implemented",
        "classified_intent": intent,
        "extracted_entities": entities.dict(),
        "agent": agent_name,
        "message": f"{agent_name.replace('_', ' ').title()} agent is not implemented in this build."
    }

# Specific agent stubs if needed for the router to import
async def handle_market_research(intent: str, entities: ExtractedEntities):
    return get_stub_response("market_research", intent, entities)

async def handle_investment_strategy(intent: str, entities: ExtractedEntities):
    return get_stub_response("investment_strategy", intent, entities)

async def handle_financial_planning(intent: str, entities: ExtractedEntities):
    return get_stub_response("financial_planning", intent, entities)

async def handle_financial_calculator(intent: str, entities: ExtractedEntities):
    return get_stub_response("financial_calculator", intent, entities)

async def handle_risk_assessment(intent: str, entities: ExtractedEntities):
    return get_stub_response("risk_assessment", intent, entities)

async def handle_product_recommendation(intent: str, entities: ExtractedEntities):
    return get_stub_response("product_recommendation", intent, entities)

async def handle_predictive_analysis(intent: str, entities: ExtractedEntities):
    return get_stub_response("predictive_analysis", intent, entities)

async def handle_customer_support(intent: str, entities: ExtractedEntities):
    return get_stub_response("customer_support", intent, entities)

async def handle_general_query(intent: str, entities: ExtractedEntities):
    return get_stub_response("general_query", intent, entities)
