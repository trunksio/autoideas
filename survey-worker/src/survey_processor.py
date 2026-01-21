"""
Survey Answer Processor - Stores survey responses in PostgreSQL
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://survey:survey_dev@localhost:5432/survey"
)


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def ensure_session_exists(conn, conversation_id: str, survey_id: str = "healthcare_ai_2025") -> str:
    """
    Ensure a survey session exists, create if not.
    Returns the internal UUID.
    """
    with conn.cursor() as cur:
        # Check if session exists
        cur.execute(
            "SELECT id FROM survey_sessions WHERE conversation_id = %s",
            (conversation_id,)
        )
        result = cur.fetchone()

        if result:
            return result['id']

        # Create new session
        cur.execute(
            """
            INSERT INTO survey_sessions (conversation_id, survey_id, started_at)
            VALUES (%s, %s, NOW())
            RETURNING id
            """,
            (conversation_id, survey_id)
        )
        result = cur.fetchone()
        conn.commit()
        logger.info(f"Created new survey session: {conversation_id}")
        return result['id']


def process_answer(message_json: str) -> Dict[str, Any]:
    """
    Process a survey answer from the queue and store in PostgreSQL.

    Args:
        message_json: JSON string containing the message data

    Returns:
        Result dictionary with success status
    """
    try:
        logger.info(f"Processing survey answer: {message_json[:200]}...")

        # Parse the message
        message = json.loads(message_json)
        params = message.get("parameters", {})

        # Extract required fields
        conversation_id = params.get("conversation_id")
        question_id = params.get("question_id")

        if not conversation_id or not question_id:
            logger.error("Missing required fields: conversation_id or question_id")
            return {
                "success": False,
                "error": "Missing required fields: conversation_id or question_id"
            }

        # Extract optional fields
        survey_id = params.get("survey_id", "healthcare_ai_2025")
        section_name = params.get("section_name")
        question_text = params.get("question_text")
        answer_type = params.get("answer_type", "free_text")
        answer_text = params.get("answer_text")
        answer_rating = params.get("answer_rating")
        answer_choices = params.get("answer_choices")
        raw_transcript = params.get("raw_transcript")

        # Store in database
        conn = get_db_connection()
        try:
            # Ensure session exists
            session_id = ensure_session_exists(conn, conversation_id, survey_id)

            with conn.cursor() as cur:
                # Upsert answer (allows updating if same question answered again)
                cur.execute(
                    """
                    INSERT INTO survey_answers
                        (session_id, question_id, section_name, question_text,
                         answer_type, answer_text, answer_rating, answer_choices,
                         raw_transcript, answered_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (session_id, question_id)
                    DO UPDATE SET
                        answer_text = EXCLUDED.answer_text,
                        answer_rating = EXCLUDED.answer_rating,
                        answer_choices = EXCLUDED.answer_choices,
                        raw_transcript = EXCLUDED.raw_transcript,
                        answered_at = NOW()
                    RETURNING id
                    """,
                    (
                        session_id,
                        question_id,
                        section_name,
                        question_text,
                        answer_type,
                        answer_text,
                        answer_rating,
                        json.dumps(answer_choices) if answer_choices else None,
                        raw_transcript
                    )
                )
                result = cur.fetchone()
                conn.commit()

                logger.info(
                    f"Stored answer: session={conversation_id}, "
                    f"question={question_id}, answer_id={result['id']}"
                )

                # Auto-complete session when final question is answered
                if question_id == "final_thoughts":
                    cur.execute(
                        """
                        UPDATE survey_sessions
                        SET completed_at = NOW()
                        WHERE id = %s AND completed_at IS NULL
                        """,
                        (session_id,)
                    )
                    conn.commit()
                    logger.info(f"Auto-completed session: {conversation_id}")

                return {
                    "success": True,
                    "answer_id": result['id'],
                    "session_id": str(session_id),
                    "question_id": question_id
                }

        finally:
            conn.close()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse message JSON: {e}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        logger.error(f"Error processing survey answer: {e}")
        return {"success": False, "error": str(e)}


def mark_session_complete(conversation_id: str) -> Dict[str, Any]:
    """Mark a survey session as complete."""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE survey_sessions
                    SET completed_at = NOW()
                    WHERE conversation_id = %s
                    RETURNING id
                    """,
                    (conversation_id,)
                )
                result = cur.fetchone()
                conn.commit()

                if result:
                    logger.info(f"Marked session complete: {conversation_id}")
                    return {"success": True, "session_id": str(result['id'])}
                else:
                    return {"success": False, "error": "Session not found"}
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error marking session complete: {e}")
        return {"success": False, "error": str(e)}


def health_check() -> bool:
    """Check database connectivity."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        logger.info("Database health check passed")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


if __name__ == "__main__":
    # Test the processor with a sample message
    test_message = json.dumps({
        "token": "survey_answer",
        "timestamp": datetime.utcnow().isoformat(),
        "parameters": {
            "conversation_id": "test_conv_123",
            "question_id": "warmup_org_type",
            "section_name": "Warm-up",
            "question_text": "What type of healthcare organisation do you work in?",
            "answer_type": "free_text",
            "answer_text": "Regional hospital network",
            "raw_transcript": "I work at a regional hospital network in Victoria"
        }
    })

    print("Testing processor with sample message...")
    result = process_answer(test_message)
    print(f"Result: {json.dumps(result, indent=2)}")
