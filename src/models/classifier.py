# Classifier output schema
"""
Agent Taxonomy:
- portfolio_health: structured assessment of the user's portfolio (concentration, performance, benchmarking, observations)
- market_research: factual/recent info about an instrument, sector, or market event
- investment_strategy: advice/strategy questions: should I buy/sell/rebalance, allocation guidance
- financial_planning: long-term planning: retirement, goals, savings rate
- financial_calculator: deterministic numerical computation: DCA returns, mortgage, tax, future value, FX conversion
- risk_assessment: risk metrics, exposure analysis, what-if scenarios
- product_recommendation: recommend specific products/funds matching user profile
- predictive_analysis: forward-looking analysis: forecasts, trend extrapolation
- customer_support: platform issues, account questions, how-to-use-app
- general_query: educational, conversational, definitions, greetings

Entity Normalization Rules:
- tickers: Case-folded; exchange-suffix optional (AAPL matches aapl and AAPL.US)
- topics / sectors: Case-folded; exact substring match per element
- amount / rate: Within ±5%
- period_years: Exact integer match
- currency: ISO 4217, exact
- index: Exact match against canonical names (S&P 500, FTSE 100, NIKKEI 225, MSCI World)
- action, goal, frequency, horizon, time_period: Exact match against vocabulary tokens
"""
