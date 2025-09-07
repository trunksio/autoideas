"""
Configuration management for AutoIdeas MCP Server
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Redis configuration
    redis_url: str = Field(
        default="redis://localhost:6379",
        env="REDIS_URL"
    )
    
    # Server configuration
    server_host: str = Field(default="0.0.0.0", env="SERVER_HOST")
    server_port: int = Field(default=8000, env="SERVER_PORT")
    
    # Paths
    config_path: Path = Field(
        default=Path("/configs"),
        env="CONFIG_PATH"
    )
    
    # ElevenLabs configuration
    elevenlabs_api_key: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    
    # Miro configuration
    miro_api_key: Optional[str] = Field(default=None, env="MIRO_API_KEY")
    
    # Application settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_workshop_config(workshop_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Load workshop configuration from filesystem
    
    Args:
        workshop_id: Optional specific workshop to load
        
    Returns:
        Workshop configuration dictionary
    """
    settings = Settings()
    config_base = settings.config_path / "workshops"
    
    if workshop_id:
        # Load specific workshop
        workshop_path = config_base / workshop_id
        if not workshop_path.exists():
            raise ValueError(f"Workshop configuration not found: {workshop_id}")
        
        return load_single_workshop(workshop_path, workshop_id)
    
    # Load all workshops
    workshops = {}
    if config_base.exists():
        for workshop_dir in config_base.iterdir():
            if workshop_dir.is_dir():
                try:
                    workshop_data = load_single_workshop(workshop_dir, workshop_dir.name)
                    workshops[workshop_dir.name] = workshop_data
                except Exception as e:
                    print(f"Error loading workshop {workshop_dir.name}: {e}")
    
    return workshops


def load_single_workshop(workshop_path: Path, workshop_id: str) -> Dict[str, Any]:
    """
    Load a single workshop configuration
    
    Args:
        workshop_path: Path to workshop directory
        workshop_id: Workshop identifier
        
    Returns:
        Workshop configuration
    """
    config = {
        "id": workshop_id,
        "elevenlabs": {},
        "miro": {},
        "metadata": {}
    }
    
    # Load ElevenLabs configuration
    elevenlabs_path = workshop_path / "elevenlabs"
    if elevenlabs_path.exists():
        agent_config_path = elevenlabs_path / "agent_config.json"
        if agent_config_path.exists():
            with open(agent_config_path, "r") as f:
                config["elevenlabs"]["agent_config"] = json.load(f)
        
        system_prompt_path = elevenlabs_path / "system_prompt.txt"
        if system_prompt_path.exists():
            with open(system_prompt_path, "r") as f:
                config["elevenlabs"]["system_prompt"] = f.read()
        
        questions_path = elevenlabs_path / "questions.json"
        if questions_path.exists():
            with open(questions_path, "r") as f:
                config["elevenlabs"]["questions"] = json.load(f)
    
    # Load Miro configuration
    miro_path = workshop_path / "miro"
    if miro_path.exists():
        board_template_path = miro_path / "board_template.json"
        if board_template_path.exists():
            with open(board_template_path, "r") as f:
                config["miro"]["board_template"] = json.load(f)
        
        card_template_path = miro_path / "card_template.json"
        if card_template_path.exists():
            with open(card_template_path, "r") as f:
                config["miro"]["card_template"] = json.load(f)
    
    # Load metadata
    metadata_path = workshop_path / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            config["metadata"] = json.load(f)
    
    return config


def save_workshop_config(workshop_id: str, config: Dict[str, Any]) -> None:
    """
    Save workshop configuration to filesystem
    
    Args:
        workshop_id: Workshop identifier
        config: Configuration to save
    """
    settings = Settings()
    workshop_path = settings.config_path / "workshops" / workshop_id
    
    # Create directories
    workshop_path.mkdir(parents=True, exist_ok=True)
    (workshop_path / "elevenlabs").mkdir(exist_ok=True)
    (workshop_path / "miro").mkdir(exist_ok=True)
    
    # Save ElevenLabs configuration
    if "elevenlabs" in config:
        elevenlabs_config = config["elevenlabs"]
        
        if "agent_config" in elevenlabs_config:
            with open(workshop_path / "elevenlabs" / "agent_config.json", "w") as f:
                json.dump(elevenlabs_config["agent_config"], f, indent=2)
        
        if "system_prompt" in elevenlabs_config:
            with open(workshop_path / "elevenlabs" / "system_prompt.txt", "w") as f:
                f.write(elevenlabs_config["system_prompt"])
        
        if "questions" in elevenlabs_config:
            with open(workshop_path / "elevenlabs" / "questions.json", "w") as f:
                json.dump(elevenlabs_config["questions"], f, indent=2)
    
    # Save Miro configuration
    if "miro" in config:
        miro_config = config["miro"]
        
        if "board_template" in miro_config:
            with open(workshop_path / "miro" / "board_template.json", "w") as f:
                json.dump(miro_config["board_template"], f, indent=2)
        
        if "card_template" in miro_config:
            with open(workshop_path / "miro" / "card_template.json", "w") as f:
                json.dump(miro_config["card_template"], f, indent=2)
    
    # Save metadata
    if "metadata" in config:
        with open(workshop_path / "metadata.json", "w") as f:
            json.dump(config["metadata"], f, indent=2)