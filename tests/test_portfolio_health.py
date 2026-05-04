import pytest
from unittest.mock import MagicMock, patch
from src.agents.portfolio_health import PortfolioHealthAgent
from src.models.classifier import ClassifierOutput, ExtractedEntities

@pytest.fixture
def mock_yf():
    with patch("yfinance.Ticker") as mock:
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = MagicMock(
            empty=False,
            Close=MagicMock(iloc=[MagicMock(__getitem__=lambda s, i: 100 if i==0 else 110)])
        )
        # Fix the indexing mock
        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.__getitem__.return_value.iloc = [100, 110]
        ticker_instance.history.return_value = mock_hist
        
        mock.return_value = ticker_instance
        yield mock

@pytest.mark.asyncio
async def test_portfolio_health_all_profiles(user_001, user_003, user_004, user_006, user_008):
    agent = PortfolioHealthAgent()
    classifier_output = ClassifierOutput(
        intent="health_check", agent="portfolio_health", 
        entities=ExtractedEntities(), safety_verdict="safe", confidence=1.0
    )
    
    for user in [user_001, user_003, user_004, user_006, user_008]:
        with patch("yfinance.Ticker") as mock_ticker:
            mock_hist = MagicMock()
            mock_hist.empty = False
            # Simulate 10% return for benchmark
            mock_hist["Close"].iloc = [100, 110]
            mock_ticker.return_value.history.return_value = mock_hist
            
            response = await agent.run(classifier_output, user)
            
            assert response.concentration_risk is not None
            assert response.performance is not None
            assert response.disclaimer is not None
            assert "investment advice" in response.disclaimer.lower()

@pytest.mark.asyncio
async def test_empty_portfolio_build_message(user_004):
    agent = PortfolioHealthAgent()
    classifier_output = ClassifierOutput(
        intent="health_check", agent="portfolio_health", 
        entities=ExtractedEntities(), safety_verdict="safe", confidence=1.0
    )
    
    response = await agent.run(classifier_output, user_004)
    
    assert any("consider diversifying" in obs.text.lower() for obs in response.observations)
    assert any("risk profile" in obs.text.lower() for obs in response.observations)
