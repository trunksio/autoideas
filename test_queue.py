#!/usr/bin/env python
"""
Test script to add a job to the Redis queue for the worker to process
"""

import json
import os
from datetime import datetime
from redis import Redis
from rq import Queue
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def queue_test_job():
    """Queue a test job for the worker"""
    
    # Get configuration
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    queue_name = os.getenv('QUEUE_NAME', 'default')
    
    print(f"Connecting to Redis: {redis_url}")
    print(f"Queue name: {queue_name}")
    
    # Connect to Redis
    try:
        redis_conn = Redis.from_url(redis_url)
        redis_conn.ping()
        print("✓ Connected to Redis")
    except Exception as e:
        print(f"✗ Failed to connect to Redis: {e}")
        sys.exit(1)
    
    # Create queue
    queue = Queue(queue_name, connection=redis_conn)
    print(f"Queue length before: {len(queue)}")
    
    # Create test message
    test_message = {
        "token": "miro_card",
        "timestamp": datetime.utcnow().isoformat(),
        "parameters": {
            "Item": "Test card from queue script",
            "Name": "Test User",
            "Theme": "Workflow Friction"
        }
    }
    
    message_json = json.dumps(test_message, indent=2)
    print(f"\nQueuing message:\n{message_json}")
    
    # Queue the job
    job = queue.enqueue(
        'triage_agent.process_message',
        message_json,
        job_timeout='5m',
        result_ttl=500
    )
    
    print(f"\n✓ Job queued successfully!")
    print(f"  Job ID: {job.id}")
    print(f"  Status: {job.get_status()}")
    print(f"Queue length after: {len(queue)}")
    
    # Wait a moment and check status
    import time
    time.sleep(2)
    
    print(f"\nChecking job status after 2 seconds...")
    print(f"  Status: {job.get_status()}")
    
    if job.is_finished:
        print(f"  Result: {job.result}")
    elif job.is_failed:
        print(f"  Error: {job.exc_info}")
    
    return job.id


def queue_multiple_test_jobs():
    """Queue multiple test jobs with different themes"""
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    queue_name = os.getenv('QUEUE_NAME', 'default')
    
    redis_conn = Redis.from_url(redis_url)
    queue = Queue(queue_name, connection=redis_conn)
    
    test_items = [
        {"Item": "Weekly reports take too long to compile", "Name": "Alice", "Theme": "Workflow Friction"},
        {"Item": "Manual data entry is repetitive", "Name": "Bob", "Theme": "Workflow Friction"},
        {"Item": "Members can't find their statements easily", "Name": "Charlie", "Theme": "Member Experience"},
        {"Item": "Response times for member queries are slow", "Name": "Diana", "Theme": "Member Experience"},
        {"Item": "Need better analytics for decision making", "Name": "Eve", "Theme": "Decision Support / Insight Gaps"},
        {"Item": "Can't see team performance metrics", "Name": "Frank", "Theme": "Decision Support / Insight Gaps"},
        {"Item": "AI assistant for member support", "Name": "Grace", "Theme": "Wishlist / Future Vision"},
        {"Item": "Automated compliance reporting", "Name": "Henry", "Theme": "Wishlist / Future Vision"},
    ]
    
    job_ids = []
    
    for item in test_items:
        message = {
            "token": "miro_card",
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": item
        }
        
        job = queue.enqueue(
            'triage_agent.process_message',
            json.dumps(message),
            job_timeout='5m',
            result_ttl=500
        )
        
        job_ids.append(job.id)
        print(f"✓ Queued: {item['Theme']} - {item['Item'][:30]}...")
    
    print(f"\n✓ Queued {len(job_ids)} test jobs")
    return job_ids


if __name__ == "__main__":
    print("AutoIdeas Queue Test Script")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "multiple":
        print("\nQueuing multiple test jobs...")
        queue_multiple_test_jobs()
    else:
        print("\nQueuing single test job...")
        queue_test_job()
        print("\nTo queue multiple test jobs, run: python test_queue.py multiple")