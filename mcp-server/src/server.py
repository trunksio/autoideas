"""
MCP SSE Server for AutoIdeas
Receives voice transcriptions from ElevenLabs and queues them for processing
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
import redis
from rq import Queue
import mcp

from .handlers import process_voice_message
from .config import Settings, load_workshop_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="AutoIdeas MCP Server",
    description="Voice collection and processing server for workshop ideation",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis and RQ
redis_client = redis.from_url(settings.redis_url)
task_queue = Queue("autoideas", connection=redis_client)

# Initialize MCP server
mcp_server = mcp.Server("autoideas-mcp")


class VoiceMessage(BaseModel):
    """Voice message from ElevenLabs"""
    workshop_id: str = Field(..., description="Workshop identifier")
    session_id: str = Field(..., description="Session identifier")
    user_nickname: str = Field(..., description="User's nickname")
    question_id: str = Field(..., description="Current question identifier")
    transcript: str = Field(..., description="Voice transcript")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkshopSession(BaseModel):
    """Workshop session configuration"""
    workshop_id: str
    customer_name: str
    miro_board_id: str
    elevenlabs_agent_id: str
    active: bool = True


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    logger.info("Starting AutoIdeas MCP Server")
    
    # Test Redis connection
    try:
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AutoIdeas MCP Server",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/workshops")
async def list_workshops():
    """List available workshop configurations"""
    workshops = load_workshop_config()
    return {"workshops": workshops}


@app.get("/workshops/{workshop_id}")
async def get_workshop(workshop_id: str):
    """Get specific workshop configuration"""
    workshops = load_workshop_config()
    workshop = workshops.get(workshop_id)
    
    if not workshop:
        raise HTTPException(status_code=404, detail="Workshop not found")
    
    return workshop


@app.post("/voice/message")
async def receive_voice_message(message: VoiceMessage):
    """
    Receive voice message from ElevenLabs
    Queue for asynchronous processing
    """
    try:
        # Validate workshop exists
        workshops = load_workshop_config()
        if message.workshop_id not in workshops:
            raise HTTPException(status_code=400, detail="Invalid workshop ID")
        
        # Prepare message for queue
        queue_message = {
            "type": "voice_response",
            "workshop_id": message.workshop_id,
            "session_id": message.session_id,
            "user_nickname": message.user_nickname,
            "question_id": message.question_id,
            "transcript": message.transcript,
            "metadata": message.metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Queue for processing
        job = task_queue.enqueue(
            "workers.process_idea",
            queue_message,
            job_timeout="5m"
        )
        
        logger.info(f"Queued voice message: job_id={job.id}, workshop={message.workshop_id}")
        
        return {
            "status": "queued",
            "job_id": job.id,
            "workshop_id": message.workshop_id,
            "session_id": message.session_id
        }
        
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sse/events")
async def sse_events(request: Request):
    """
    SSE endpoint for real-time updates
    Clients can subscribe to receive processing status updates
    """
    async def event_generator():
        try:
            pubsub = redis_client.pubsub()
            pubsub.subscribe("autoideas:events")
            
            # Send initial connection message
            yield {
                "event": "connected",
                "data": json.dumps({"status": "connected", "timestamp": datetime.utcnow().isoformat()})
            }
            
            # Listen for messages
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    yield {
                        "event": data.get("event", "update"),
                        "data": json.dumps(data)
                    }
                    
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                    
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
        finally:
            pubsub.close()
    
    return EventSourceResponse(event_generator())


@app.post("/mcp/tools/{tool_name}")
async def handle_mcp_tool(tool_name: str, request: Request):
    """
    Handle MCP tool invocations from ElevenLabs
    """
    try:
        body = await request.json()
        
        # Route to appropriate handler based on tool name
        if tool_name == "submit_idea":
            result = await process_voice_message(body, redis_client, task_queue)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"MCP tool error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get server status and statistics"""
    try:
        queue_size = len(task_queue)
        redis_info = redis_client.info()
        
        return {
            "status": "operational",
            "queue_size": queue_size,
            "redis_connected": True,
            "redis_version": redis_info.get("redis_version"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)