from typing import Any
from src.models.classifier import ClassifierOutput, ExtractedEntities
from src.models.request import UserProfile

class BaseStub:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    async def run(self, classifier_output: ClassifierOutput, user: UserProfile) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "classified_intent": classifier_output.intent,
            "extracted_entities": classifier_output.entities.dict(),
            "agent": self.agent_name,
            "message": f"{self.agent_name.replace('_', ' ').title()} agent is not implemented in this build."
        }

class MarketResearchStub(BaseStub):
    def __init__(self): super().__init__("market_research")

class InvestmentStrategyStub(BaseStub):
    def __init__(self): super().__init__("investment_strategy")

class FinancialPlanningStub(BaseStub):
    def __init__(self): super().__init__("financial_planning")

class FinancialCalculatorStub(BaseStub):
    def __init__(self): super().__init__("financial_calculator")

class RiskAssessmentStub(BaseStub):
    def __init__(self): super().__init__("risk_assessment")

class ProductRecommendationStub(BaseStub):
    def __init__(self): super().__init__("product_recommendation")

class PredictiveAnalysisStub(BaseStub):
    def __init__(self): super().__init__("predictive_analysis")

class SupportStub(BaseStub):
    def __init__(self): super().__init__("customer_support")

class GeneralQueryStub(BaseStub):
    def __init__(self): super().__init__("general_query")
