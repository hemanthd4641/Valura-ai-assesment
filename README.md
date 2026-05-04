# Valura AI Microservice

Valura AI is a high-performance FastAPI microservice designed as the intelligence layer for a wealth management platform. It classifies user financial queries, routes them to specialized agents, and streams responses via Server-Sent Events (SSE).

## Architecture Decisions

### 1. Session Memory: In-Memory Implementation
For this demonstration, I have implemented an **in-memory session store**. 
- **Rationale**: Given the microservice requirements and the need for a fast, zero-dependency demo, in-memory storage provides sub-millisecond access times without the overhead of external database configuration.
- **Production Upgrade Path**: The memory system is designed behind a `SessionMemory` protocol. Upgrading to a production-grade store like **Redis** or **PostgreSQL** would simply involve creating a new implementation of the protocol (e.g., `RedisSessionMemory`) and updating the dependency injection in `src/memory/session.py`.

### 2. LLM Orchestration
- **Model**: Developed using `gpt-4o-mini` for cost-efficiency.
- **Structured Output**: Using Pydantic models with OpenAI's structured output capabilities to ensure reliable parsing of intents and entities.

### 3. Safety First
A synchronous Safety Guard runs before any LLM calls, ensuring that harmful requests are blocked in under 10ms with specific, professional refusal messages.

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
```bash
pytest tests/ -v
```

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key.
- `MODEL_DEV`: Model used for development (default: `gpt-4o-mini`).
- `MODEL_EVAL`: Model used for evaluation (default: `gpt-4.1`).
- `SESSION_BACKEND`: Memory backend (current: `memory`).
- `PIPELINE_TIMEOUT_SECONDS`: Global timeout for the AI pipeline.

## Defence Video
[Link to Defence Video] (To be added)
