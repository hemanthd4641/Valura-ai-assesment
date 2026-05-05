import asyncio
import time
import json
import statistics
import httpx
import tiktoken

# Pricing assumption for "gpt-4.1" (using gpt-4-turbo pricing as a placeholder if not specified, 
# but targets say < $0.05. Let's assume $10/M input, $30/M output).
INPUT_PRICE_PER_TOKEN = 10.0 / 1_000_000
OUTPUT_PRICE_PER_TOKEN = 30.0 / 1_000_000

NUM_REQUESTS = 20
URL = "http://127.0.0.1:8001/chat"

payload = {
    "query": "how is my portfolio doing? i have some apple and microsoft.",
    "user": {
        "user_id": "bench_user",
        "kyc_status": "verified",
        "risk_profile": "moderate",
        "base_currency": "USD",
        "preferences": {"preferred_benchmark": "SPY"},
        "portfolio": [
            {"ticker": "AAPL", "quantity": 10, "purchase_price": 150.0, "current_price": 180.0, "currency": "USD"},
            {"ticker": "MSFT", "quantity": 5, "purchase_price": 300.0, "current_price": 400.0, "currency": "USD"}
        ]
    },
    "session_id": "bench_session"
}

async def run_single_request(client, req_id):
    start_time = time.perf_counter()
    first_token_time = None
    end_time = None
    
    input_text = json.dumps(payload)
    output_text = ""
    
    try:
        async with client.stream("POST", URL, json=payload, timeout=20.0) as response:
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                
                if line.startswith("event: token") and first_token_time is None:
                    first_token_time = time.perf_counter()
                    
                if line.startswith("data: "):
                    data_str = line[6:]
                    output_text += data_str
                    
                if line.startswith("event: done"):
                    end_time = time.perf_counter()
                    break
    except Exception as e:
        print(f"Request {req_id} failed: {e}")
        return None
        
    if first_token_time is None or end_time is None:
        return None
        
    ttft = (first_token_time - start_time) * 1000
    e2e = (end_time - start_time) * 1000
    
    # Estimate tokens
    encoding = tiktoken.encoding_for_model("gpt-4")
    input_tokens = len(encoding.encode(input_text))
    # Roughly add 500 tokens for system prompt and taxonomy context
    input_tokens += 500 
    output_tokens = len(encoding.encode(output_text))
    
    cost = (input_tokens * INPUT_PRICE_PER_TOKEN) + (output_tokens * OUTPUT_PRICE_PER_TOKEN)
    
    return {
        "ttft": ttft,
        "e2e": e2e,
        "cost": cost
    }

async def main():
    print(f"Starting benchmark: {NUM_REQUESTS} requests...")
    
    results = []
    # Run sequentially to not overload and get clean individual latencies, 
    # or concurrently? The prompt doesn't specify. Real world P95 is usually measured under some load or sequentially.
    # Let's run sequentially to get stable TTFT from the LLM API.
    async with httpx.AsyncClient() as client:
        for i in range(NUM_REQUESTS):
            res = await run_single_request(client, i)
            if res:
                results.append(res)
                print(f"Req {i+1}/{NUM_REQUESTS}: TTFT={res['ttft']:.0f}ms, E2E={res['e2e']:.0f}ms")
            else:
                print(f"Req {i+1}/{NUM_REQUESTS}: FAILED")
            await asyncio.sleep(0.5) # small delay between requests
            
    if not results:
        print("All requests failed.")
        return
        
    ttfts = sorted([r["ttft"] for r in results])
    e2es = sorted([r["e2e"] for r in results])
    costs = [r["cost"] for r in results]
    
    def p(data, percentile):
        idx = int(len(data) * percentile)
        return data[idx]
        
    p50_ttft = p(ttfts, 0.50)
    p95_ttft = p(ttfts, 0.95)
    p50_e2e = p(e2es, 0.50)
    p95_e2e = p(e2es, 0.95)
    avg_cost = sum(costs) / len(costs)
    
    print("\n=== Benchmark Results ===")
    print(f"Provider: openai")
    print(f"Dev model: gpt-4o-mini")
    print(f"p50 first-token latency: {p50_ttft:.0f}ms")
    print(f"p95 first-token latency: {p95_ttft:.0f}ms")
    print(f"p50 end-to-end latency: {p50_e2e:.0f}ms")
    print(f"p95 end-to-end latency: {p95_e2e:.0f}ms")
    print(f"Estimated cost at gpt-4.1 pricing: ${avg_cost:.4f} per query")

if __name__ == "__main__":
    asyncio.run(main())
