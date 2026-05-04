import json
import pytest
import httpx
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from src.main import app
from src.models.request import UserProfile, Holding

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

class MockLLMClient:
    def __init__(self):
        self.complete = AsyncMock()

@pytest.fixture
def mock_llm_client(monkeypatch):
    mock = MockLLMClient()
    monkeypatch.setattr("src.classifier.intent.get_llm_client", lambda: mock)
    return mock

@pytest.fixture
async def async_client():
    from httpx import ASGITransport
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def load_user():
    def _load(user_id: str) -> UserProfile:
        for p in (FIXTURES_DIR / "users").glob("*.json"):
            with open(p) as f:
                u_data = json.load(f)
            if u_data.get("user_id") == user_id:
                transformed = {
                    "user_id": u_data["user_id"],
                    "risk_profile": u_data["risk_profile"],
                    "base_currency": u_data.get("base_currency", "USD"),
                    "kyc_status": u_data["kyc"]["status"],
                    "portfolio": [
                        {
                            "ticker": h["ticker"],
                            "quantity": h["quantity"],
                            "purchase_price": h["avg_cost"],
                            "current_price": h.get("current_price", h["avg_cost"]),
                            "currency": h.get("currency", "USD")
                        }
                        for h in u_data.get("positions", [])
                    ]
                }
                return UserProfile(**transformed)
        raise FileNotFoundError(f"User {user_id} not found")
    return _load

@pytest.fixture
def user_001(load_user): return load_user("usr_001")
@pytest.fixture
def user_003(load_user): return load_user("usr_003")
@pytest.fixture
def user_004(load_user): return load_user("usr_004")
@pytest.fixture
def user_006(load_user): return load_user("usr_006")
@pytest.fixture
def user_008(load_user): return load_user("usr_008")

@pytest.fixture
def gold_safety_queries():
    path = FIXTURES_DIR / "test_queries" / "safety_pairs.json"
    with open(path) as f:
        return json.load(f)["queries"]

@pytest.fixture
def gold_classifier_queries():
    path = FIXTURES_DIR / "test_queries" / "intent_classification.json"
    with open(path) as f:
        return json.load(f)["queries"]

def entities_match(expected: dict, actual: dict) -> bool:
    for field, exp_val in expected.items():
        if field not in actual: continue
        
        act_val = actual[field]
        if field == "tickers":
            exp_set = {t.upper().split(".")[0] for t in exp_val}
            act_set = {t.upper().split(".")[0] for t in act_val}
            if not exp_set.issubset(act_set): return False
        elif field in ["amounts", "rates"]:
            for e_amt in exp_val:
                found = False
                for a_amt in act_val:
                    if abs(a_amt - e_amt) <= 0.05 * abs(e_amt):
                        found = True; break
                if not found: return False
        elif isinstance(exp_val, list):
            exp_set = {str(x).lower() for x in exp_val}
            act_set = {str(x).lower() for x in act_val}
            if not exp_set.issubset(act_set): return False
    return True
