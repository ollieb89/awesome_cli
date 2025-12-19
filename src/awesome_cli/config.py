"""
Configuration management for Awesome CLI.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    """Application settings."""
    env: str = "production"
    log_level: str = "INFO"
    config_path: Optional[Path] = None
    app_name: str = "AwesomeCLI"

def load_settings(config_path: Optional[str] = None) -> Settings:
    """
    Load settings from defaults, environment variables, and optional config file.
    
    Priority:
    1. Config file (if provided)
    2. Environment variables (prefixed with AWESOME_CLI_)
    3. Defaults
    """
    # Defaults are handled by the Settings dataclass defaults

    # 1. Environment variables override defaults
    env = os.getenv("AWESOME_CLI_ENV", "production")
    log_level = os.getenv("AWESOME_CLI_LOG_LEVEL", "INFO")
    
    # 2. Config file overrides (if implemented in future)
    # For now, we just acknowledge the path exists if provided

    return Settings(
        env=env,
        log_level=log_level,
        config_path=Path(config_path) if config_path else None
    )
