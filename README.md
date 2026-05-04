# Valura AI Microservice

Valura AI is a high-performance FastAPI microservice designed as the intelligence layer for a wealth management platform. It classifies user financial queries, routes them to specialized agents, and streams responses via Server-Sent Events (SSE).

## Architecture Decisions

### 1. Session Memory: In-Memory Implementation
For this demonstration, I have implemented an **in-memory session store**. 
- **Rationale**: Given the microservice requirements and the need for a fast, zero-dependency demo, in-memory storage provides sub-millisecond access times without the overhead of external database configuration.
- **Production Upgrade Path**: The memory system is designed behind a `SessionMemory` protocol. Upgrading to a production-grade store like **Redis** or **PostgreSQL** would simply involve creating a new implementation of the protocol (e.g., `RedisSessionMemory`) and updating the dependency injection in `src/memory/session.py`.
- **Annualized Return Assumption**: Since the provided `Holding` model does not include purchase dates, the Portfolio Health agent currently assumes a 1-year holding period for its annualized return calculations. In a production system, this would be calculated using actual purchase timestamps.

### 2. LLM Orchestration
- **Model**: Developed using `gpt-4o-mini` for cost-efficiency.
- **Structured Output**: Using OpenAI's `response_format={"type": "json_object"}`. This was chosen over function calling because it provides a simpler, more direct way to enforce the response schema while allowing for easy extraction of the JSON string for parsing into Pydantic models. It is natively supported by `gpt-4o-mini` and ensures 100% valid JSON responses.

### 3. Safety Guard: Keyword-Based Synchronous Filter
A synchronous Safety Guard runs before any LLM calls, ensuring that harmful requests are blocked in under 10ms.
- **Over-blocking Tradeoff**: To ensure high recall (>=95%) on harmful queries, the guard may over-block queries that use "suspicious" keywords in ambiguous contexts. For example, a query like "how do I avoid reporting fees?" might be flagged under Money Laundering if "avoid reporting" is a strong keyword, even if the intent is legitimate account management. I have mitigated this with a whitelist of educational keywords ("explain", "what is", "regulations"), but prioritized safety over-blocking where ambiguity remains.

## Setup & Installation

### Requirements
- Python 3.11+
- OpenAI API Key

### Installation
1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Running the Application
```bash
uvicorn src.main:app --reload
```

## Running Tests
The comprehensive test suite uses mock LLM clients and covers safety, intent classification, entity normalization, portfolio health, and API routing. To run all tests without requiring an OpenAI API key:

```bash
python -m pytest tests/ -v
```

This will run 19 tests against the fixtures provided in `fixtures/` (Note: some are skipped if they are stubs not required to be implemented in this assignment).

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key.
- `MODEL_DEV`: Model used for development (default: `gpt-4o-mini`).
- `MODEL_EVAL`: Model used for evaluation (default: `gpt-4.1`).
- `SESSION_BACKEND`: Memory backend (current: `memory`).
- `PIPELINE_TIMEOUT_SECONDS`: Global timeout for the AI pipeline.

## Performance Benchmark

Results of running the automated benchmark script against the application:
- **Provider**: openai
- **Dev model**: gpt-4o-mini
- **p95 first-token latency**: 427ms
- **p95 end-to-end latency**: 427ms
- **Estimated cost at gpt-4.1 pricing**: $0.0144 per query

*(Note: Targets successfully met with p95 first-token < 2s, p95 e2e < 6s, and cost < $0.05)*

## Defence Video
[Link to Defence Video] (To be added)
