"""
Miro API client for AutoIdeas
Handles card creation and board management
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class MiroClient:
    """Client for interacting with Miro API"""
    
    def __init__(self):
        self.api_key = os.getenv("MIRO_API_KEY")
        self.base_url = "https://api.miro.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_idea_card(
        self,
        board_id: str,
        idea_data: Dict[str, Any],
        template: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an idea card on a Miro board
        
        Args:
            board_id: Miro board identifier
            idea_data: Processed idea data
            template: Optional card template
            
        Returns:
            Created card information
        """
        try:
            # Prepare card data
            card_data = self._prepare_card_data(idea_data, template)
            
            # Create sticky note
            endpoint = f"{self.base_url}/boards/{board_id}/sticky_notes"
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=card_data
            )
            
            if response.status_code != 201:
                raise Exception(f"Failed to create card: {response.text}")
            
            card_info = response.json()
            
            logger.info(f"Created Miro card: {card_info.get('id')}")
            
            return {
                "card_id": card_info.get("id"),
                "board_id": board_id,
                "created_at": datetime.utcnow().isoformat(),
                "position": card_info.get("position"),
                "data": card_info
            }
            
        except Exception as e:
            logger.error(f"Error creating Miro card: {e}")
            raise
    
    def _prepare_card_data(
        self,
        idea_data: Dict[str, Any],
        template: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare card data for Miro API
        
        Args:
            idea_data: Processed idea data
            template: Optional card template
            
        Returns:
            Formatted card data
        """
        # Extract key information
        title = idea_data.get("title", "New Idea")
        description = idea_data.get("description", "")
        category = idea_data.get("category", "General")
        user_nickname = idea_data.get("user_nickname", "Anonymous")
        theme = idea_data.get("theme", "")
        
        # Build card content
        content = f"<p><strong>{title}</strong></p>"
        content += f"<p>{description}</p>"
        content += f"<p><em>By: {user_nickname}</em></p>"
        if theme:
            content += f"<p>Theme: {theme}</p>"
        
        # Use template if provided
        if template:
            color = template.get("color", self._get_color_for_category(category))
            shape = template.get("shape", "square")
            position = template.get("position")
        else:
            color = self._get_color_for_category(category)
            shape = "square"
            position = self._calculate_position(category)
        
        return {
            "data": {
                "content": content,
                "shape": shape
            },
            "style": {
                "fillColor": color,
                "textAlign": "center",
                "textAlignVertical": "middle"
            },
            "position": position or {"x": 0, "y": 0}
        }
    
    def _get_color_for_category(self, category: str) -> str:
        """
        Get color based on idea category
        
        Args:
            category: Idea category
            
        Returns:
            Hex color code
        """
        color_map = {
            "process_improvement": "#ff9999",              # Light red (formerly workflow_friction)
            "member_experience": "#99ccff",                # Light blue
            "caresuper_people_experience": "#ffcc99",      # Light orange
            "information_gaps_and_ai_wishlist": "#99ff99", # Light green
            "general": "#ffff99"                           # Light yellow
        }
        
        return color_map.get(category.lower().replace(" ", "_"), "#f0f0f0")
    
    def _calculate_position(self, category: str) -> Dict[str, float]:
        """
        Calculate card position based on category
        
        Args:
            category: Idea category
            
        Returns:
            Position coordinates
        """
        # Simple grid layout by category
        category_positions = {
            "process_improvement": {"x": 0, "y": 0},
            "member_experience": {"x": 300, "y": 0},
            "caresuper_people_experience": {"x": 600, "y": 0},
            "information_gaps_and_ai_wishlist": {"x": 900, "y": 0},
            "general": {"x": 1200, "y": 0}
        }
        
        base_position = category_positions.get(
            category.lower().replace(" ", "_"),
            {"x": 0, "y": 0}
        )
        
        # Add some randomness to avoid overlap
        import random
        return {
            "x": base_position["x"] + random.randint(-50, 50),
            "y": base_position["y"] + random.randint(0, 500)
        }
    
    def get_board_info(self, board_id: str) -> Dict[str, Any]:
        """
        Get information about a Miro board
        
        Args:
            board_id: Miro board identifier
            
        Returns:
            Board information
        """
        try:
            endpoint = f"{self.base_url}/boards/{board_id}"
            
            response = requests.get(endpoint, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get board info: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting board info: {e}")
            raise
    
    def create_frame(
        self,
        board_id: str,
        title: str,
        position: Dict[str, float],
        size: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Create a frame on a Miro board
        
        Args:
            board_id: Miro board identifier
            title: Frame title
            position: Frame position
            size: Frame size
            
        Returns:
            Created frame information
        """
        try:
            endpoint = f"{self.base_url}/boards/{board_id}/frames"
            
            frame_data = {
                "data": {
                    "title": title,
                    "type": "freeform"
                },
                "position": position,
                "geometry": {
                    "width": size.get("width", 800),
                    "height": size.get("height", 600)
                }
            }
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=frame_data
            )
            
            if response.status_code != 201:
                raise Exception(f"Failed to create frame: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating frame: {e}")
            raise
    
    def get_items_in_frame(
        self,
        board_id: str,
        frame_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all items within a frame
        
        Args:
            board_id: Miro board identifier
            frame_id: Frame identifier
            
        Returns:
            List of items in frame
        """
        try:
            endpoint = f"{self.base_url}/boards/{board_id}/items"
            params = {
                "parent": frame_id,
                "limit": 100
            }
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get items: {response.text}")
            
            return response.json().get("data", [])
            
        except Exception as e:
            logger.error(f"Error getting items in frame: {e}")
            return []