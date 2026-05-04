import subprocess
import time
import sys
import os

def main():
    print("Starting simulated uvicorn server...")
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "mock_key_for_benchmarking"
    env["MODEL_DEV"] = "gpt-4o-mini"
    
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "tests.bench_app:app", "--port", "8000"],
        env=env
    )
    
    # Wait for server to start
    time.sleep(3)
    
    print("Running benchmarking script...")
    subprocess.run([sys.executable, "tests/bench_latency.py"])
    
    print("Shutting down server...")
    server.terminate()
    server.wait()
    
if __name__ == "__main__":
    main()
