"""
Main processor for AutoIdeas worker
Handles idea processing and Miro card creation
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import redis
from .miro_client import MiroClient
from .ai_processor import AIProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Initialize processors
miro_client = MiroClient()
ai_processor = AIProcessor()


def process_idea(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main worker function to process submitted ideas
    
    Args:
        task_data: Task data from queue containing:
            - workshop_id: Workshop identifier
            - session_id: Session identifier
            - user_nickname: User's nickname
            - question_id: Question identifier
            - transcript: Voice transcript
            - metadata: Additional metadata
            
    Returns:
        Processing result
    """
    try:
        logger.info(f"Processing idea for workshop: {task_data['workshop_id']}")
        
        # Extract data
        workshop_id = task_data["workshop_id"]
        session_id = task_data["session_id"]
        user_nickname = task_data["user_nickname"]
        question_id = task_data["question_id"]
        transcript = task_data["transcript"]
        
        # Load workshop configuration
        workshop_config = load_workshop_config(workshop_id)
        if not workshop_config:
            raise ValueError(f"Workshop configuration not found: {workshop_id}")
        
        # Process transcript with AI
        processed_idea = ai_processor.process_transcript(
            transcript=transcript,
            question_id=question_id,
            workshop_config=workshop_config
        )
        
        # Enrich with metadata
        processed_idea.update({
            "user_nickname": user_nickname,
            "session_id": session_id,
            "workshop_id": workshop_id,
            "timestamp": task_data.get("timestamp", datetime.utcnow().isoformat())
        })
        
        # Create Miro card
        miro_board_id = workshop_config["miro"]["board_id"]
        card_result = miro_client.create_idea_card(
            board_id=miro_board_id,
            idea_data=processed_idea,
            template=workshop_config["miro"].get("card_template")
        )
        
        # Update session statistics
        update_session_stats(session_id, workshop_id)
        
        # Publish success event
        publish_event({
            "event": "idea_processed",
            "workshop_id": workshop_id,
            "session_id": session_id,
            "card_id": card_result.get("card_id"),
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Successfully processed idea: {card_result.get('card_id')}")
        
        return {
            "success": True,
            "card_id": card_result.get("card_id"),
            "processed_idea": processed_idea,
            "miro_result": card_result
        }
        
    except Exception as e:
        logger.error(f"Error processing idea: {e}")
        
        # Publish error event
        publish_event({
            "event": "processing_error",
            "workshop_id": task_data.get("workshop_id"),
            "session_id": task_data.get("session_id"),
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": False,
            "error": str(e)
        }


def load_workshop_config(workshop_id: str) -> Optional[Dict[str, Any]]:
    """
    Load workshop configuration from Redis or filesystem
    
    Args:
        workshop_id: Workshop identifier
        
    Returns:
        Workshop configuration or None
    """
    try:
        # Try to get from Redis cache first
        cache_key = f"workshop:config:{workshop_id}"
        cached_config = redis_client.get(cache_key)
        
        if cached_config:
            return json.loads(cached_config)
        
        # Load from filesystem
        config_path = f"/configs/workshops/{workshop_id}"
        
        config = {
            "workshop_id": workshop_id,
            "elevenlabs": {},
            "miro": {}
        }
        
        # Load ElevenLabs configuration
        elevenlabs_config_path = f"{config_path}/elevenlabs/agent_config.json"
        if os.path.exists(elevenlabs_config_path):
            with open(elevenlabs_config_path, "r") as f:
                config["elevenlabs"] = json.load(f)
        
        # Load questions
        questions_path = f"{config_path}/elevenlabs/questions.json"
        if os.path.exists(questions_path):
            with open(questions_path, "r") as f:
                config["elevenlabs"]["questions"] = json.load(f)
        
        # Load Miro configuration
        miro_config_path = f"{config_path}/miro/board_template.json"
        if os.path.exists(miro_config_path):
            with open(miro_config_path, "r") as f:
                config["miro"] = json.load(f)
        
        # Load card template
        card_template_path = f"{config_path}/miro/card_template.json"
        if os.path.exists(card_template_path):
            with open(card_template_path, "r") as f:
                config["miro"]["card_template"] = json.load(f)
        
        # Cache configuration (expire in 1 hour)
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(config)
        )
        
        return config
        
    except Exception as e:
        logger.error(f"Error loading workshop config: {e}")
        return None


def update_session_stats(session_id: str, workshop_id: str) -> None:
    """
    Update session statistics in Redis
    
    Args:
        session_id: Session identifier
        workshop_id: Workshop identifier
    """
    try:
        # Increment idea count
        idea_count_key = f"session:{session_id}:idea_count"
        redis_client.incr(idea_count_key)
        
        # Update last activity
        session_key = f"session:{session_id}"
        redis_client.hset(session_key, mapping={
            "last_activity": datetime.utcnow().isoformat(),
            "workshop_id": workshop_id
        })
        
        # Set expiry (24 hours)
        redis_client.expire(session_key, 86400)
        redis_client.expire(idea_count_key, 86400)
        
    except Exception as e:
        logger.error(f"Error updating session stats: {e}")


def publish_event(event_data: Dict[str, Any]) -> None:
    """
    Publish event to Redis pub/sub for SSE subscribers
    
    Args:
        event_data: Event data to publish
    """
    try:
        redis_client.publish(
            "autoideas:events",
            json.dumps(event_data)
        )
    except Exception as e:
        logger.error(f"Error publishing event: {e}")


def cluster_ideas(workshop_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Cluster and theme ideas for a workshop or session
    
    Args:
        workshop_id: Workshop identifier
        session_id: Optional session identifier
        
    Returns:
        Clustered ideas with themes
    """
    try:
        # Get all ideas for workshop/session
        pattern = f"idea:{workshop_id}:*"
        if session_id:
            pattern = f"idea:{workshop_id}:{session_id}:*"
        
        idea_keys = redis_client.keys(pattern)
        ideas = []
        
        for key in idea_keys:
            idea_data = redis_client.get(key)
            if idea_data:
                ideas.append(json.loads(idea_data))
        
        if not ideas:
            return {"clusters": [], "themes": []}
        
        # Use AI processor to cluster ideas
        clusters = ai_processor.cluster_ideas(ideas)
        
        # Generate themes
        themes = ai_processor.generate_themes(clusters)
        
        return {
            "clusters": clusters,
            "themes": themes,
            "total_ideas": len(ideas),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clustering ideas: {e}")
        return {
            "error": str(e),
            "clusters": [],
            "themes": []
        }