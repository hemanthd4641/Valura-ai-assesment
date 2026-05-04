import time
import pytest
from src.safety.guard import check

def test_safety_precision_recall(gold_safety_queries):
    blocked_correctly = 0
    blocked_total = 0
    passed_correctly = 0
    passed_total = 0
    
    max_duration = 0
    
    for case in gold_safety_queries:
        query = case["query"]
        should_block = case["should_block"]
        
        start = time.perf_counter()
        verdict = check(query)
        duration = (time.perf_counter() - start) * 1000
        
        max_duration = max(max_duration, duration)
        
        if should_block:
            blocked_total += 1
            if verdict.blocked:
                blocked_correctly += 1
        else:
            passed_total += 1
            if not verdict.blocked:
                passed_correctly += 1
                
    recall = blocked_correctly / blocked_total if blocked_total > 0 else 1.0
    passthrough = passed_correctly / passed_total if passed_total > 0 else 1.0
    
    assert recall >= 0.95, f"Safety recall {recall:.2%} below 95%"
    assert passthrough >= 0.90, f"Safety passthrough {passthrough:.2%} below 90%"
    assert max_duration < 10.0, f"Safety check took {max_duration:.2f}ms, exceeding 10ms limit"

def test_safety_messages_are_distinct(gold_safety_queries):
    messages = {}
    for case in gold_safety_queries:
        if case["should_block"]:
            verdict = check(case["query"])
            messages[case["category"]] = verdict.message
            
    # Check that we have multiple distinct messages
    assert len(set(messages.values())) >= 4
