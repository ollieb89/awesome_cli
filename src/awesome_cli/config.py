"""
Configuration management for Awesome CLI.
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


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
    defaults: Dict[str, Any] = {}
    
    # 2. Config file overrides (if implemented in future)
    if config_path:
        path = Path(config_path)
        if path.exists():
            try:
                # Basic JSON loader stub
                with path.open("r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    # In a real app, merge deeply. Here we just update top-level keys
                    # that match our Settings fields.
                    if isinstance(file_data, dict):
                        defaults.update(file_data)
            except Exception:
                # Log error or warn in real app
                pass

    # 1. Environment variables override everything
    env = os.getenv("AWESOME_CLI_ENV", defaults.get("env", "production"))
    log_level = os.getenv("AWESOME_CLI_LOG_LEVEL", defaults.get("log_level", "INFO"))

    return Settings(
        env=env,
        log_level=log_level,
        config_path=Path(config_path) if config_path else None
    )
