import os
import json
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from src.models.request import QueryRequest
from src.safety.guard import check as safety_check
from src.classifier.intent import classify, ClassifierOutput
from src.router import route
from src.memory.session import get_session_memory

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    required_vars = ["OPENAI_API_KEY", "MODEL_DEV"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
    
    model = os.getenv("MODEL_DEV", "gpt-4o-mini")
    logger.info(f"Valura AI starting up. Using model: {model}")
    
    yield
    # Shutdown logic (if any)

app = FastAPI(title="Valura AI Microservice", lifespan=lifespan)

PIPELINE_TIMEOUT = int(os.getenv("PIPELINE_TIMEOUT_SECONDS", 10))


async def stream_pipeline(request: QueryRequest):
    """
    Main pipeline generator for SSE streaming.
    """
    session_id = request.session_id
    memory = get_session_memory()

    try:
        # 1. Safety Guard
        safety_verdict = safety_check(request.query)
        if safety_verdict.blocked:
            yield {
                "event": "error",
                "data": json.dumps({
                    "code": "SAFETY_BLOCK",
                    "message": safety_verdict.message
                })
            }
            yield {"event": "done", "data": "{}"}
            return

        # 2. Intent Classifier
        # Check cache first (Identical-query dedupe - Stretch goal)
        cached_data = memory.get_cache(session_id, request.query)
        if cached_data:
            logger.info(f"Cache hit for session {session_id}")
            classifier_output = ClassifierOutput(**cached_data)
        else:
            # Get history from memory
            history = memory.get_history(session_id, last_n=5)
            
            try:
                classifier_output = await asyncio.wait_for(
                    classify(request.query, request.user, history),
                    timeout=PIPELINE_TIMEOUT
                )
                # Store in cache
                memory.set_cache(session_id, request.query, classifier_output.model_dump())
            except asyncio.TimeoutError:
                yield {
                    "event": "error",
                    "data": json.dumps({"code": "TIMEOUT", "message": "Classifier timed out"})
                }
                yield {"event": "done", "data": "{}"}
                return


        # 3. Metadata Event
        yield {
            "event": "metadata",
            "data": json.dumps({
                "agent": classifier_output.agent,
                "intent": classifier_output.intent,
                "safety_verdict": classifier_output.safety_verdict
            })
        }

        # 4. Agent Routing & Execution
        try:
            agent_response = await asyncio.wait_for(
                route(classifier_output, request.user),
                timeout=PIPELINE_TIMEOUT
            )
        except asyncio.TimeoutError:
            yield {
                "event": "error",
                "data": json.dumps({"code": "TIMEOUT", "message": "Agent execution timed out"})
            }
            yield {"event": "done", "data": "{}"}
            return

        # 5. Save to Memory
        memory.add_turn(session_id, {
            "turn_number": request.turn_number,
            "query": request.query,
            "agent": classifier_output.agent,
            "response_summary": "Agent execution completed"
        })

        # 6. Stream Response
        # For simplicity in this demo, we emit the structured response.
        # In a real streaming agent, the 'token' events would come from the agent's run method.
        # Here we simulate a summary token before the structured data.
        
        yield {
            "event": "token",
            "data": json.dumps({"text": f"Analyzing your request with the {classifier_output.agent} specialist..."})
        }
        
        yield {
            "event": "structured",
            "data": json.dumps(agent_response, default=lambda x: x.model_dump() if hasattr(x, 'model_dump') else x)
        }

        yield {"event": "done", "data": "{}"}

    except Exception as e:
        logger.exception("Pipeline error")
        yield {
            "event": "error",
            "data": json.dumps({"code": "INTERNAL_ERROR", "message": str(e)})
        }
        yield {"event": "done", "data": "{}"}

@app.post("/chat")
async def chat(request: QueryRequest):
    return EventSourceResponse(stream_pipeline(request))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
