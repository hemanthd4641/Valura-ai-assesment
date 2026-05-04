import asyncio
from src.main import app
import src.classifier.intent
import yfinance as yf
from unittest.mock import MagicMock
import pandas as pd

class SimulatedLLMClient:
    async def complete(self, *args, **kwargs):
        await asyncio.sleep(0.4)
        return '{"intent": "health_check", "agent": "portfolio_health", "entities": {}, "safety_verdict": "safe", "confidence": 0.99}'

src.classifier.intent.get_llm_client = lambda: SimulatedLLMClient()

# Mock yfinance to prevent network timeouts during benchmark
mock_hist = pd.DataFrame({"Close": [100.0, 110.0]})
mock_ticker = MagicMock()
mock_ticker.history.return_value = mock_hist
yf.Ticker = MagicMock(return_value=mock_ticker)
