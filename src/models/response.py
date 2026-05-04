from pydantic import BaseModel

class ConcentrationRisk(BaseModel):
    top_position_pct: float
    top_3_positions_pct: float
    flag: str                  # "low" | "medium" | "high"

class Performance(BaseModel):
    total_return_pct: float
    annualized_return_pct: float

class BenchmarkComparison(BaseModel):
    benchmark: str
    portfolio_return_pct: float
    benchmark_return_pct: float
    alpha_pct: float

class Observation(BaseModel):
    severity: str              # "warning" | "info" | "positive"
    text: str

class PortfolioHealthOutput(BaseModel):
    concentration_risk: ConcentrationRisk
    performance: Performance
    benchmark_comparison: BenchmarkComparison
    observations: list[Observation]
    disclaimer: str
