"""
Triage Agent Worker for processing messages and creating Miro cards
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any
import requests
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Miro API configuration
MIRO_API_KEY = os.getenv("MIRO_API_KEY")
MIRO_BOARD_ID = os.getenv("MIRO_BOARD_ID", "uXjVJLEWVa8=")
MIRO_BASE_URL = "https://api.miro.com/v2"

# Theme color mapping - Miro accepts specific color names only
THEME_COLORS = {
    "process_improvement": "red",                                  # Red for process improvement
    "member_experience": "light_blue",                            # Blue for member experience
    "team_experience": "yellow",                                  # Yellow for team experience
    "information_gaps_and_ai_wishlist": "light_green",           # Green for information gaps and AI wishlist
    # Alternative formats and variations
    "process improvement": "red",
    "team experience": "yellow",
    "information gaps and ai wishlist": "light_green",
    "information_gaps": "light_green",
    "ai_wishlist": "light_green",
    "default": "gray"                                            # Gray for uncategorized
}

# Position tracking (simple grid layout)
current_position = {"x": 0, "y": 0}
CARD_SPACING = 250
CARDS_PER_ROW = 5


def process_message(message_json: str) -> Dict[str, Any]:
    """
    Process a message from the queue and create a Miro card
    
    Args:
        message_json: JSON string containing the message data
        
    Returns:
        Result dictionary with success status and details
    """
    try:
        logger.info(f"Processing message: {message_json[:200]}...")
        
        # Parse the message
        message = json.loads(message_json)
        
        # Extract parameters
        token = message.get("token", "")
        timestamp = message.get("timestamp", datetime.utcnow().isoformat())
        parameters = message.get("parameters", {})
        
        # Validate we have a miro_card token
        if token != "miro_card":
            logger.warning(f"Skipping non-miro_card message with token: {token}")
            return {
                "success": False,
                "error": f"Invalid token: {token}",
                "skipped": True
            }
        
        # Extract card details
        item = parameters.get("Item", "Untitled Item")
        name = parameters.get("Name", "Anonymous")
        theme = parameters.get("Theme", "default")
        
        # Create Miro card
        result = create_miro_card(
            item=item,
            name=name,
            theme=theme,
            timestamp=timestamp
        )
        
        logger.info(f"Successfully created Miro card: {result.get('id')}")
        
        return {
            "success": True,
            "card_id": result.get("id"),
            "board_id": MIRO_BOARD_ID,
            "item": item,
            "name": name,
            "theme": theme,
            "timestamp": timestamp
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse message JSON: {e}")
        return {
            "success": False,
            "error": f"Invalid JSON: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def create_miro_card(item: str, name: str, theme: str, timestamp: str) -> Dict[str, Any]:
    """
    Create a card on the Miro board
    
    Args:
        item: The item/idea text
        name: The person's name
        theme: The theme category
        timestamp: When the item was submitted
        
    Returns:
        Miro API response
    """
    if not MIRO_API_KEY:
        logger.error("MIRO_API_KEY environment variable not set!")
        raise ValueError("MIRO_API_KEY environment variable not set")
    
    # Log API key info (safely)
    logger.info(f"Using Miro API Key: {MIRO_API_KEY[:10]}...{MIRO_API_KEY[-4:] if len(MIRO_API_KEY) > 14 else '****'}")
    
    # Get color for theme
    theme_lower = theme.lower().replace(" ", "_")
    color = THEME_COLORS.get(theme_lower, THEME_COLORS["default"])
    
    # Calculate position for the card
    position = get_next_card_position()
    
    # Format the card content
    content = format_card_content(item, name, theme, timestamp)
    
    # Create sticky note via Miro API
    headers = {
        "Authorization": f"Bearer {MIRO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Sticky note data - using only supported Miro fields
    card_data = {
        "data": {
            "content": content,
            "shape": "square"
        },
        "style": {
            "fillColor": color,
            "textAlign": "center",
            "textAlignVertical": "middle"
        },
        "position": position,
        "geometry": {
            "width": 220  # Only width for sticky notes (height is automatic)
        }
    }
    
    # Make API request
    endpoint = f"{MIRO_BASE_URL}/boards/{MIRO_BOARD_ID}/sticky_notes"
    
    logger.info(f"Creating Miro card at position {position}")
    logger.info(f"Miro API Endpoint: {endpoint}")
    logger.info(f"Card color: {color} for theme: {theme}")
    logger.info(f"Card content preview: {content[:100]}...")
    
    # Log full request details
    logger.debug(f"Request headers: {json.dumps({k: v[:20] + '...' if k == 'Authorization' else v for k, v in headers.items()}, indent=2)}")
    logger.debug(f"Request body: {json.dumps(card_data, indent=2)}")
    
    response = requests.post(
        endpoint,
        headers=headers,
        json=card_data
    )
    
    # Log response details
    logger.info(f"Miro API Response Status: {response.status_code}")
    logger.info(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code not in [200, 201]:
        logger.error(f"Miro API error: {response.status_code}")
        logger.error(f"Response body: {response.text}")
        logger.error(f"Request was: {json.dumps(card_data, indent=2)}")
        raise Exception(f"Failed to create Miro card: {response.status_code} - {response.text}")
    
    response_data = response.json()
    logger.info(f"✓ Successfully created Miro card!")
    logger.info(f"  Card ID: {response_data.get('id', 'unknown')}")
    logger.info(f"  Card Type: {response_data.get('type', 'unknown')}")
    logger.info(f"  Position: {response_data.get('position', {})}")
    logger.debug(f"Full response: {json.dumps(response_data, indent=2)}")
    
    return response_data


def format_card_content(item: str, name: str, theme: str, timestamp: str) -> str:
    """
    Format the content for the Miro card
    
    Args:
        item: The item/idea text
        name: The person's name
        theme: The theme category
        timestamp: When submitted
        
    Returns:
        HTML-formatted content for the card
    """
    # Parse timestamp to make it more readable
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M")
    except:
        time_str = "now"
    
    # Create formatted content (Miro supports basic HTML)
    content = f"""<p><strong>{theme.upper()}</strong></p>
<p>{item}</p>
<p><em>— {name}</em></p>
<p><small>{time_str}</small></p>"""
    
    return content


def get_next_card_position() -> Dict[str, float]:
    """
    Calculate the position for the next card in a grid layout
    
    Returns:
        Dictionary with x and y coordinates
    """
    global current_position
    
    # Get current position
    x = current_position["x"]
    y = current_position["y"]
    
    # Update for next card (move right, wrap to next row)
    current_position["x"] += CARD_SPACING
    
    # Wrap to next row if needed
    if current_position["x"] >= CARD_SPACING * CARDS_PER_ROW:
        current_position["x"] = 0
        current_position["y"] += CARD_SPACING
    
    # Add some random offset to avoid perfect grid
    x_offset = random.randint(-20, 20)
    y_offset = random.randint(-20, 20)
    
    return {
        "x": x + x_offset,
        "y": y + y_offset
    }


def reset_card_positions():
    """Reset the card position tracker"""
    global current_position
    current_position = {"x": 0, "y": 0}


# Health check function
def health_check() -> bool:
    """
    Check if the worker can connect to Miro API
    
    Returns:
        True if healthy, False otherwise
    """
    try:
        if not MIRO_API_KEY:
            logger.error("MIRO_API_KEY not configured")
            return False
        
        # Try to get board info
        headers = {
            "Authorization": f"Bearer {MIRO_API_KEY}",
        }
        
        endpoint = f"{MIRO_BASE_URL}/boards/{MIRO_BOARD_ID}"
        response = requests.get(endpoint, headers=headers, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"Successfully connected to Miro board: {MIRO_BOARD_ID}")
            return True
        else:
            logger.error(f"Failed to connect to Miro: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


if __name__ == "__main__":
    # Test the worker with a sample message
    test_message = json.dumps({
        "token": "miro_card",
        "timestamp": datetime.utcnow().isoformat(),
        "parameters": {
            "Item": "Test item from worker",
            "Name": "Test User",
            "Theme": "ideas"
        }
    })
    
    print("Testing worker with sample message...")
    result = process_message(test_message)
    print(f"Result: {json.dumps(result, indent=2)}")