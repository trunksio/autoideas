"""
AutoIdeas API - ElevenLabs Webhook Handler

This API receives webhook calls from ElevenLabs and submits jobs to RQ
for processing by the worker.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
import csv
import io

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
from rq import Queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QUEUE_NAME = os.getenv("QUEUE_NAME", "miro_card")
SURVEY_QUEUE_NAME = os.getenv("SURVEY_QUEUE_NAME", "survey_queue")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://survey:survey_dev@localhost:5432/survey")
API_KEY = os.getenv("AUTOIDEAS_API_KEY")

# Initialize FastAPI
app = FastAPI(
    title="AutoIdeas API",
    description="Webhook API for ElevenLabs to submit jobs to RQ",
    version="0.1.0",
)

# Add CORS middleware for direct container access (no reverse proxy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection (lazy initialization)
_redis_conn: Optional[Redis] = None
_queue: Optional[Queue] = None
_survey_queue: Optional[Queue] = None


def get_redis() -> Redis:
    """Get or create Redis connection."""
    global _redis_conn
    if _redis_conn is None:
        logger.info(f"Connecting to Redis at {REDIS_URL}")
        _redis_conn = Redis.from_url(REDIS_URL)
        _redis_conn.ping()
        logger.info("Successfully connected to Redis")
    return _redis_conn


def get_queue() -> Queue:
    """Get or create RQ queue."""
    global _queue
    if _queue is None:
        redis_conn = get_redis()
        _queue = Queue(QUEUE_NAME, connection=redis_conn)
        logger.info(f"Created queue: {QUEUE_NAME}")
    return _queue


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Verify the API key from the request header."""
    if not API_KEY:
        logger.warning("AUTOIDEAS_API_KEY not configured - API key validation disabled")
        return x_api_key
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


class WebhookPayload(BaseModel):
    """Payload from ElevenLabs webhook."""

    token: str = "miro_card"
    timestamp: Optional[str] = None
    parameters: Dict[str, Any]


class JobResponse(BaseModel):
    """Response after job submission."""

    success: bool
    job_id: str
    queue: str
    message: str


@app.get("/")
async def health_check():
    """Health check endpoint."""
    try:
        redis = get_redis()
        redis.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "AutoIdeas API",
        "redis": redis_status,
        "queue": QUEUE_NAME,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/webhook", response_model=JobResponse)
async def receive_webhook(
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    """
    Receive webhook from ElevenLabs and submit job to RQ.

    Expects X-API-Key header for authentication.
    Accepts flexible payload formats from ElevenLabs.
    """
    try:
        # Get raw body and log it
        body = await request.body()
        body_str = body.decode()
        logger.info(f"Received webhook body: {body_str}")
        logger.info(f"Request headers: {dict(request.headers)}")

        # Parse JSON
        try:
            data = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

        logger.info(f"Parsed data: {json.dumps(data, indent=2)}")

        # Handle different payload formats
        # Format 1: Already has "parameters" key
        if "parameters" in data:
            parameters = data["parameters"]
        # Format 2: ElevenLabs format with direct fields
        else:
            parameters = data

        # Build the message for the worker
        message = {
            "token": "miro_card",
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": parameters,
        }
        message_json = json.dumps(message)

        logger.info(f"Prepared message: {message_json[:500]}...")

        # Get queue and enqueue the job
        queue = get_queue()
        job = queue.enqueue(
            "triage_agent.process_message",
            message_json,
            job_timeout=300,  # 5 minute timeout
        )

        logger.info(f"Job enqueued: {job.id}")

        return JobResponse(
            success=True,
            job_id=job.id,
            queue=QUEUE_NAME,
            message="Job submitted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/raw")
async def receive_raw_webhook(
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    """
    Receive raw webhook payload for debugging.

    Logs the raw payload and attempts to process it.
    """
    try:
        body = await request.body()
        logger.info(f"Raw webhook body: {body.decode()}")

        # Try to parse as JSON
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # If it's already in our expected format, use it
        if "parameters" in data:
            payload = WebhookPayload(**data)
        else:
            # Wrap the entire payload as parameters
            payload = WebhookPayload(
                token="miro_card",
                timestamp=datetime.utcnow().isoformat(),
                parameters=data,
            )

        # Prepare the message for the worker
        message = {
            "token": payload.token,
            "timestamp": payload.timestamp,
            "parameters": payload.parameters,
        }
        message_json = json.dumps(message)

        # Get queue and enqueue the job
        queue = get_queue()
        job = queue.enqueue(
            "triage_agent.process_message",
            message_json,
            job_timeout=300,
        )

        logger.info(f"Job enqueued from raw webhook: {job.id}")

        return JobResponse(
            success=True,
            job_id=job.id,
            queue=QUEUE_NAME,
            message="Job submitted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing raw webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/queue/status")
async def queue_status(api_key: str = Depends(verify_api_key)):
    """Get the current queue status."""
    try:
        queue = get_queue()
        return {
            "queue": QUEUE_NAME,
            "jobs_pending": len(queue),
            "failed_jobs": queue.failed_job_registry.count,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Survey Endpoints
# =============================================================================

def get_survey_queue() -> Queue:
    """Get or create survey RQ queue."""
    global _survey_queue
    if _survey_queue is None:
        redis_conn = get_redis()
        _survey_queue = Queue(SURVEY_QUEUE_NAME, connection=redis_conn)
        logger.info(f"Created survey queue: {SURVEY_QUEUE_NAME}")
    return _survey_queue


def get_db_connection():
    """Get database connection for admin queries."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@app.post("/webhook/survey")
async def receive_survey_answer(
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    """
    Receive per-question survey answers from ElevenLabs.

    Queues to survey_queue for processing by survey-worker.
    """
    try:
        body = await request.body()
        body_str = body.decode()
        logger.info(f"Received survey webhook: {body_str[:500]}...")

        try:
            data = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in survey webhook: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

        # Build message for worker
        message = {
            "token": "survey_answer",
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": data,
        }
        message_json = json.dumps(message)

        # Queue to survey queue
        queue = get_survey_queue()
        job = queue.enqueue(
            "survey_processor.process_answer",
            message_json,
            job_timeout=60,
        )

        logger.info(f"Survey answer job enqueued: {job.id}")

        return {
            "success": True,
            "job_id": job.id,
            "queue": SURVEY_QUEUE_NAME,
            "message": "Survey answer queued",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing survey webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/survey/sessions")
async def list_survey_sessions(
    limit: int = 100,
    offset: int = 0,
):
    """List all survey sessions with answer counts. No auth required (behind Apache basic auth)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id,
                    s.conversation_id,
                    s.survey_id,
                    s.started_at,
                    s.completed_at,
                    COUNT(a.id) as answer_count
                FROM survey_sessions s
                LEFT JOIN survey_answers a ON s.id = a.session_id
                GROUP BY s.id
                ORDER BY s.started_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            sessions = cur.fetchall()

            # Get total count and stats
            cur.execute("SELECT COUNT(*) as total FROM survey_sessions")
            total = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) as completed FROM survey_sessions WHERE completed_at IS NOT NULL")
            completed = cur.fetchone()["completed"]

            cur.execute("SELECT COUNT(*) as total FROM survey_answers")
            total_answers = cur.fetchone()["total"]

        conn.close()

        return {
            "sessions": [dict(s) for s in sessions],
            "total": total,
            "limit": limit,
            "offset": offset,
            "stats": {
                "total_sessions": total,
                "completed_sessions": completed,
                "in_progress_sessions": total - completed,
                "total_answers": total_answers,
            }
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/survey/sessions/{session_id}")
async def get_survey_session(
    session_id: str,
):
    """Get a single session with all its answers."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get session
            cur.execute("""
                SELECT * FROM survey_sessions WHERE id = %s OR conversation_id = %s
            """, (session_id, session_id))
            session = cur.fetchone()

            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

            # Get answers
            cur.execute("""
                SELECT * FROM survey_answers
                WHERE session_id = %s
                ORDER BY answered_at
            """, (session["id"],))
            answers = cur.fetchall()

        conn.close()

        return {
            "session": dict(session),
            "answers": [dict(a) for a in answers],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/survey/export")
async def export_survey_data(
    format: str = "json",
):
    """Export all survey responses as JSON or CSV."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    s.conversation_id,
                    s.survey_id,
                    s.started_at,
                    s.completed_at,
                    a.question_id,
                    a.section_name,
                    a.question_text,
                    a.answer_type,
                    a.answer_text,
                    a.answer_rating,
                    a.answer_choices,
                    a.answered_at
                FROM survey_sessions s
                JOIN survey_answers a ON s.id = a.session_id
                ORDER BY s.started_at, a.answered_at
            """)
            rows = cur.fetchall()
        conn.close()

        if format == "csv":
            output = io.StringIO()
            if rows:
                writer = csv.DictWriter(output, fieldnames=rows[0].keys())
                writer.writeheader()
                for row in rows:
                    # Convert datetime and jsonb fields to strings
                    row_dict = dict(row)
                    for k, v in row_dict.items():
                        if hasattr(v, 'isoformat'):
                            row_dict[k] = v.isoformat()
                        elif isinstance(v, (dict, list)):
                            row_dict[k] = json.dumps(v)
                    writer.writerow(row_dict)

            from fastapi.responses import Response
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=survey_export.csv"}
            )
        else:
            # JSON format
            result = []
            for row in rows:
                row_dict = dict(row)
                for k, v in row_dict.items():
                    if hasattr(v, 'isoformat'):
                        row_dict[k] = v.isoformat()
                result.append(row_dict)
            return {"data": result, "count": len(result)}

    except Exception as e:
        logger.error(f"Error exporting survey data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
