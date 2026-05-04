import yfinance as yf
import pandas as pd
from typing import Optional
from src.models.request import UserProfile, Holding
from src.models.response import (
    PortfolioHealthOutput, 
    ConcentrationRisk, 
    Performance, 
    BenchmarkComparison, 
    Observation
)

DISCLAIMER = (
    "This analysis is for informational purposes only and does not constitute investment advice. "
    "Past performance is not indicative of future results. Please consult a qualified financial "
    "advisor before making investment decisions."
)

BENCHMARKS = {
    "USD": "^GSPC",    # S&P 500
    "GBP": "^FTSE",    # FTSE 100
    "EUR": "^STOXX50E", # Euro Stoxx 50
    "JPY": "^N225",    # Nikkei 225
    "SGD": "^STI",     # Straits Times Index
}

class PortfolioHealthAgent:
    async def run(self, classifier_output, user: UserProfile, llm=None) -> PortfolioHealthOutput:
        """
        Runs the Portfolio Health Agent logic.
        """
        return await run_logic(user, llm)

async def run_logic(user: UserProfile, llm=None) -> PortfolioHealthOutput:
    if not user.portfolio:
        return handle_empty_portfolio(user)

    # Calculate portfolio values
    holdings_values = []
    total_value = 0.0
    total_cost = 0.0

    for holding in user.portfolio:
        current_value = holding.quantity * holding.current_price
        cost_basis = holding.quantity * holding.purchase_price
        holdings_values.append({
            "ticker": holding.ticker,
            "value": current_value,
            "cost": cost_basis
        })
        total_value += current_value
        total_cost += cost_basis

    # 1. Concentration Risk
    sorted_holdings = sorted(holdings_values, key=lambda x: x["value"], reverse=True)
    top_position_pct = (sorted_holdings[0]["value"] / total_value * 100) if total_value > 0 else 0
    top_3_positions_pct = (sum(h["value"] for h in sorted_holdings[:3]) / total_value * 100) if total_value > 0 else 0

    flag = "low"
    if top_position_pct > 40:
        flag = "high"
    elif top_position_pct > 20:
        flag = "medium"

    concentration = ConcentrationRisk(
        top_position_pct=round(top_position_pct, 2),
        top_3_positions_pct=round(top_3_positions_pct, 2),
        flag=flag
    )

    # 2. Performance
    total_return_pct = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
    # Annualized return - Assuming 1 year period as dates are missing
    annualized_return_pct = total_return_pct 

    performance = Performance(
        total_return_pct=round(total_return_pct, 2),
        annualized_return_pct=round(annualized_return_pct, 2)
    )

    # 3. Benchmark Comparison
    base_curr = user.base_currency
    benchmark_ticker = BENCHMARKS.get(base_curr, "^GSPC")
    
    benchmark_return_pct = 0.0
    try:
        # Fetch 1 year return for benchmark
        ticker = yf.Ticker(benchmark_ticker)
        hist = ticker.history(period="1y")
        if not hist.empty:
            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            benchmark_return_pct = ((end_price - start_price) / start_price) * 100
    except Exception:
        # Fallback to a static estimate if yfinance fails
        benchmark_return_pct = 10.0

    alpha_pct = total_return_pct - benchmark_return_pct

    benchmark_comp = BenchmarkComparison(
        benchmark=benchmark_ticker,
        portfolio_return_pct=round(total_return_pct, 2),
        benchmark_return_pct=round(benchmark_return_pct, 2),
        alpha_pct=round(alpha_pct, 2)
    )

    # 4. Observations
    observations = []
    if flag == "high":
        observations.append(Observation(
            severity="warning",
            text=f"High concentration detected: Your top position ({sorted_holdings[0]['ticker']}) represents {round(top_position_pct, 1)}% of your portfolio."
        ))
    
    if alpha_pct > 0:
        observations.append(Observation(
            severity="positive",
            text=f"Your portfolio is outperforming the {benchmark_ticker} by {round(alpha_pct, 1)}%."
        ))
    else:
        observations.append(Observation(
            severity="info",
            text=f"Your portfolio is trailing the {benchmark_ticker} benchmark. Consider reviewing your allocation."
        ))

    if total_return_pct > 15:
        observations.append(Observation(
            severity="positive",
            text="Strong overall performance with a total return of over 15%."
        ))

    return PortfolioHealthOutput(
        concentration_risk=concentration,
        performance=performance,
        benchmark_comparison=benchmark_comp,
        observations=observations,
        disclaimer=DISCLAIMER
    )

def handle_empty_portfolio(user: UserProfile) -> PortfolioHealthOutput:
    """Returns a BUILD-oriented response for empty portfolios."""
    return PortfolioHealthOutput(
        concentration_risk=ConcentrationRisk(top_position_pct=0, top_3_positions_pct=0, flag="low"),
        performance=Performance(total_return_pct=0, annualized_return_pct=0),
        benchmark_comparison=BenchmarkComparison(
            benchmark=BENCHMARKS.get(user.base_currency, "^GSPC"),
            portfolio_return_pct=0,
            benchmark_return_pct=0,
            alpha_pct=0
        ),
        observations=[
            Observation(
                severity="info",
                text="Your portfolio is currently empty. To get started, consider diversifying across different asset classes like stocks and bonds based on your risk profile."
            ),
            Observation(
                severity="info",
                text=f"With a {user.risk_profile} risk profile, you might look at instruments that align with your long-term financial goals."
            )
        ],
        disclaimer=DISCLAIMER
    )
