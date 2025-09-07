"""
Message handlers for AutoIdeas MCP Server
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime
import redis
from rq import Queue


logger = logging.getLogger(__name__)


async def process_voice_message(
    message: Dict[str, Any],
    redis_client: redis.Redis,
    task_queue: Queue
) -> Dict[str, Any]:
    """
    Process incoming voice message and queue for worker processing
    
    Args:
        message: Voice message data
        redis_client: Redis connection
        task_queue: RQ queue for tasks
        
    Returns:
        Processing result
    """
    try:
        # Extract message components
        workshop_id = message.get("workshop_id")
        session_id = message.get("session_id")
        user_nickname = message.get("user_nickname")
        question_id = message.get("question_id")
        transcript = message.get("transcript")
        
        # Validate required fields
        if not all([workshop_id, session_id, transcript]):
            raise ValueError("Missing required fields in voice message")
        
        # Prepare task data
        task_data = {
            "type": "process_idea",
            "workshop_id": workshop_id,
            "session_id": session_id,
            "user_nickname": user_nickname or "Anonymous",
            "question_id": question_id,
            "transcript": transcript,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": message.get("metadata", {})
        }
        
        # Queue task for processing
        job = task_queue.enqueue(
            "workers.processor:process_idea",
            task_data,
            job_timeout="5m",
            result_ttl=3600  # Keep result for 1 hour
        )
        
        # Publish event for SSE subscribers
        event_data = {
            "event": "idea_submitted",
            "job_id": job.id,
            "workshop_id": workshop_id,
            "session_id": session_id,
            "user_nickname": user_nickname,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        redis_client.publish(
            "autoideas:events",
            json.dumps(event_data)
        )
        
        logger.info(f"Queued idea for processing: job_id={job.id}")
        
        return {
            "success": True,
            "job_id": job.id,
            "status": "queued",
            "message": "Idea submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        
        # Publish error event
        error_event = {
            "event": "processing_error",
            "error": str(e),
            "workshop_id": message.get("workshop_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        redis_client.publish(
            "autoideas:events",
            json.dumps(error_event)
        )
        
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process idea"
        }


async def get_session_status(
    session_id: str,
    redis_client: redis.Redis
) -> Dict[str, Any]:
    """
    Get status of a workshop session
    
    Args:
        session_id: Session identifier
        redis_client: Redis connection
        
    Returns:
        Session status information
    """
    try:
        # Get session data from Redis
        session_key = f"session:{session_id}"
        session_data = redis_client.hgetall(session_key)
        
        if not session_data:
            return {
                "exists": False,
                "session_id": session_id
            }
        
        # Decode bytes to strings
        session_info = {
            k.decode(): v.decode() if isinstance(v, bytes) else v
            for k, v in session_data.items()
        }
        
        # Get idea count for session
        idea_count = redis_client.get(f"session:{session_id}:idea_count")
        if idea_count:
            session_info["idea_count"] = int(idea_count)
        
        return {
            "exists": True,
            "session_id": session_id,
            "data": session_info
        }
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        return {
            "exists": False,
            "error": str(e)
        }


async def update_session_data(
    session_id: str,
    data: Dict[str, Any],
    redis_client: redis.Redis
) -> bool:
    """
    Update session data in Redis
    
    Args:
        session_id: Session identifier
        data: Data to update
        redis_client: Redis connection
        
    Returns:
        Success status
    """
    try:
        session_key = f"session:{session_id}"
        
        # Update session data
        redis_client.hset(session_key, mapping=data)
        
        # Set expiry (24 hours)
        redis_client.expire(session_key, 86400)
        
        # Publish update event
        event_data = {
            "event": "session_updated",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        redis_client.publish(
            "autoideas:events",
            json.dumps(event_data)
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating session data: {e}")
        return False