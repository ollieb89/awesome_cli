"""
Configuration management for Awesome CLI.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class Settings:
    """Application settings."""
    env: str = "production"
    log_level: str = "INFO"
    config_path: Optional[Path] = None
    app_name: str = "AwesomeCLI"
    
    # Example specific setting
    max_retries: int = 3

def load_settings(config_path: Optional[str] = None) -> Settings:
    """
    Load settings from defaults, environment variables, and optional config file.
    
    Priority:
    1. Config file (if provided and implemented)
    2. Environment variables (prefixed with AWESOME_CLI_)
    3. Defaults
    """
    # 1. Start with defaults
    env = os.getenv("AWESOME_CLI_ENV", "production")
    log_level = os.getenv("AWESOME_CLI_LOG_LEVEL", "INFO")
    
    # 2. In a real app, you might load from a JSON/YAML/TOML file here
    if config_path:
        # Placeholder for file loading logic
        # e.g., data = json.load(open(config_path))
        pass

    return Settings(
        env=env,
        log_level=log_level,
        config_path=Path(config_path) if config_path else None
    )
