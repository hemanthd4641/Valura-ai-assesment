import json
import logging
from typing import Optional
from src.llm.client import get_llm_client
from src.models.classifier import ClassifierOutput, ExtractedEntities
from src.models.request import UserProfile

logger = logging.getLogger(__name__)

AGENT_TAXONOMY = {
    "portfolio_health": "structured assessment of the user's portfolio (concentration, performance, benchmarking, observations)",
    "market_research": "factual/recent info about an instrument, sector, or market event",
    "investment_strategy": "advice/strategy questions: should I buy/sell/rebalance, allocation guidance",
    "financial_planning": "long-term planning: retirement, goals, savings rate",
    "financial_calculator": "deterministic numerical computation: DCA returns, mortgage, tax, future value, FX conversion",
    "risk_assessment": "risk metrics, exposure analysis, what-if scenarios",
    "product_recommendation": "recommend specific products/funds matching user profile",
    "predictive_analysis": "forward-looking analysis: forecasts, trend extrapolation",
    "customer_support": "platform issues, account questions, how-to-use-app",
    "general_query": "educational, conversational, definitions, greetings"
}

SYSTEM_PROMPT = """
You are the Intent Classifier for Valura AI, a wealth management platform.
Your job is to classify the user's financial query, extract entities, and route to the correct specialist agent.

AGENT TAXONOMY:
{taxonomy}

RESPONSE FORMAT:
You must respond with a JSON object matching this schema:
{{
    "intent": "string (brief description of user intent)",
    "agent": "string (one of the valid agent names above)",
    "entities": {{
        "tickers": ["array of stock tickers mentioned, uppercase"],
        "amounts": ["array of numbers mentioned"],
        "time_periods": ["array of time periods like 'today', 'this_month'"],
        "sectors": ["array of sectors mentioned like 'tech', 'healthcare'"],
        "topics": ["array of general topics mentioned"]
    }},
    "safety_verdict": "safe | caution | unsafe",
    "confidence": float (0.0 to 1.0)
}}

CONTEXTUAL RULES:
1. Follow-up resolution: Use the provided conversation history to resolve ambiguous references (e.g., "what about it?" after "how is Apple doing?" refers to AAPL).
2. Tickers: Normalize tickers to uppercase (e.g., "apple" -> "AAPL").
3. Multi-intent: If multiple intents are present, pick the most dominant one.
4. If you are unsure or the query is gibberish, route to 'general_query'.
5. Always output valid JSON.
"""

async def classify(
    query: str, 
    user_profile: UserProfile, 
    history: list[dict] = None,
    llm_client = None
) -> ClassifierOutput:
    """
    Classifies a user query using a single LLM call.
    """
    if llm_client is None:
        llm_client = get_llm_client()

    history = history or []
    
    # Format taxonomy for prompt
    taxonomy_str = "\n".join([f"- {name}: {desc}" for name, desc in AGENT_TAXONOMY.items()])
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(taxonomy=taxonomy_str)},
    ]
    
    # Add history
    for turn in history:
        messages.append({"role": "user", "content": turn.get("query", "")})
        messages.append({"role": "assistant", "content": f"Handled by {turn.get('agent', 'unknown')}"})
    
    # Add current query with profile context
    user_context = f"User Risk Profile: {user_profile.risk_profile}. Query: {query}"
    messages.append({"role": "user", "content": user_context})

    try:
        response_text = await llm_client.complete(
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response_text)
        
        # Ensure entities structure is correct
        if "entities" not in data:
            data["entities"] = {}
        
        return ClassifierOutput(**data)

    except Exception as e:
        logger.error(f"Classifier failure: {str(e)}")
        # Fallback behavior
        return ClassifierOutput(
            intent="unknown",
            agent="customer_support",
            entities=ExtractedEntities(),
            safety_verdict="safe",
            confidence=0.0
        )
