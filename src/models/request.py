from pydantic import BaseModel

class Holding(BaseModel):
    ticker: str
    quantity: float
    purchase_price: float
    current_price: float
    currency: str = "USD"

class UserProfile(BaseModel):
    user_id: str
    kyc_status: str
    risk_profile: str          # e.g. "aggressive", "conservative", "moderate"
    portfolio: list[Holding]
    base_currency: str = "USD"

class QueryRequest(BaseModel):
    query: str
    user: UserProfile
    session_id: str
    turn_number: int = 1
