#!/usr/bin/env python
"""
RQ Worker for AutoIdeas
Monitors Redis queue and processes messages to create Miro cards
"""

import os
import sys
import logging
from redis import Redis
from rq import Worker, Queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our triage agent
from triage_agent import process_message, health_check

def main():
    """Main worker entry point"""
    
    # Get Redis configuration from environment
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    queue_name = os.getenv('QUEUE_NAME', 'default')
    
    logger.info(f"Starting worker...")
    logger.info(f"Redis URL: {redis_url}")
    logger.info(f"Queue name: {queue_name}")
    logger.info(f"Miro Board ID: {os.getenv('MIRO_BOARD_ID', 'Not set')}")
    
    # Check health
    if not health_check():
        logger.error("Health check failed! Please check your configuration.")
        logger.info("Continuing anyway - will retry on each message...")
    
    # Connect to Redis
    try:
        redis_conn = Redis.from_url(redis_url)
        redis_conn.ping()
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)
    
    # Create queue
    queue = Queue(queue_name, connection=redis_conn)
    
    # Log queue status
    logger.info(f"Queue '{queue_name}' status:")
    logger.info(f"  - Jobs in queue: {len(queue)}")
    try:
        logger.info(f"  - Failed jobs: {queue.failed_job_registry.count}")
    except:
        logger.info(f"  - Failed jobs: Unable to get count")
    
    # Register the function that RQ should call
    # RQ expects 'triage_agent.process_message' so we need to make it available
    import triage_agent
    sys.modules['triage_agent'] = triage_agent
    
    # Start worker
    worker = Worker([queue], connection=redis_conn)
    
    logger.info(f"Worker started, listening on queue '{queue_name}'...")
    logger.info("Waiting for jobs... Press Ctrl+C to exit")
    
    # Work
    worker.work(
        with_scheduler=False,
        logging_level='INFO'
    )


if __name__ == '__main__':
    main()