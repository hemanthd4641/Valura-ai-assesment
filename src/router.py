import logging
from typing import Any
from src.models.classifier import ClassifierOutput
from src.models.request import UserProfile
from src.agents.portfolio_health import PortfolioHealthAgent
from src.agents.stubs import (
    MarketResearchStub,
    InvestmentStrategyStub,
    FinancialPlanningStub,
    FinancialCalculatorStub,
    RiskAssessmentStub,
    ProductRecommendationStub,
    PredictiveAnalysisStub,
    SupportStub,
    GeneralQueryStub
)

logger = logging.getLogger(__name__)

AGENT_REGISTRY = {
    "portfolio_health": PortfolioHealthAgent(),
    "market_research": MarketResearchStub(),
    "investment_strategy": InvestmentStrategyStub(),
    "financial_planning": FinancialPlanningStub(),
    "financial_calculator": FinancialCalculatorStub(),
    "risk_assessment": RiskAssessmentStub(),
    "product_recommendation": ProductRecommendationStub(),
    "predictive_analysis": PredictiveAnalysisStub(),
    "customer_support": SupportStub(),
    "general_query": GeneralQueryStub(),
}

async def route(classifier_output: ClassifierOutput, user: UserProfile) -> Any:
    """
    Routes the classified query to the correct agent.
    """
    try:
        agent = AGENT_REGISTRY.get(classifier_output.agent)
        if agent is None:
            logger.warning(f"Agent {classifier_output.agent} not found in registry. Falling back to support.")
            agent = AGENT_REGISTRY["customer_support"]
        
        return await agent.run(classifier_output, user)
    except Exception as e:
        logger.error(f"Routing error: {str(e)}")
        # Fallback to support stub
        fallback_agent = AGENT_REGISTRY["customer_support"]
        return await fallback_agent.run(classifier_output, user)
