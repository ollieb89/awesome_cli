"""
Configuration management for Awesome CLI.
"""
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

from awesome_cli.utils.paths import get_data_dir

logger = logging.getLogger(__name__)

T = TypeVar('T')

def get_env_safe(key: str, default: T, cast: Type[T]) -> T:
    """Get environment variable with safe casting."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        if cast == bool:
            return str(value).lower() in ("true", "1", "yes")  # type: ignore
        return cast(value)
    except (ValueError, TypeError):
        return default

def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursive dict merge.
    Merged dict is returned (target is modified in place).
    """
    for k, v in source.items():
        if isinstance(v, dict) and k in target and isinstance(target[k], dict):
            deep_merge(target[k], v)
        else:
            target[k] = v
    return target

@dataclass
class CryptoSettings:
    """Settings for Crypto Data Fetching."""
    coingecko_api_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_request_timeout: int = 10
    coingecko_rate_limit_requests: int = 50
    cache_ttl_minutes: int = 5
    cache_ttl_metadata_hours: int = 24
    scheduler_interval_minutes: int = 5
    # Default to user data directory, avoid relative paths
    storage_path: str = str(get_data_dir("awesome_cli") / "crypto_assets.json")
    redis_url: Optional[str] = None
    use_redis: bool = False


@dataclass
class Settings:
    """Application settings."""
    env: str = "production"
    log_level: str = "INFO"
    config_path: Optional[Path] = None
    app_name: str = "AwesomeCLI"
    crypto: CryptoSettings = field(default_factory=CryptoSettings)

def load_settings(config_path: Optional[str] = None) -> Settings:
    """
    Load settings from defaults, environment variables, and optional config file.
    
    Priority:
    1. Environment variables (prefixed with AWESOME_CLI_)
    2. Config file (if provided)
    3. Defaults
    """
    # 1. Start with defaults from Dataclasses
    base_settings = Settings()
    # Convert to dict for easier merging
    settings_dict = asdict(base_settings)
    
    # 2. Config file overrides
    if config_path:
        path = Path(config_path)
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    if isinstance(file_data, dict):
                        deep_merge(settings_dict, file_data)
            except Exception as e:
                logger.warning(f"Failed to load config file {path}: {e}", exc_info=True)

    # 3. Environment variables override everything

    # Top level settings
    settings_dict["env"] = os.getenv("AWESOME_CLI_ENV", settings_dict["env"])
    settings_dict["log_level"] = os.getenv("AWESOME_CLI_LOG_LEVEL", settings_dict["log_level"])
    settings_dict["config_path"] = Path(config_path) if config_path else None

    # Crypto settings
    crypto_dict = settings_dict.get("crypto", {})

    # Apply env vars to crypto settings, using current value (from default or file) as default
    crypto_dict["coingecko_api_base_url"] = os.getenv(
        "AWESOME_CLI_COINGECKO_API_BASE_URL", crypto_dict["coingecko_api_base_url"]
    )
    crypto_dict["coingecko_request_timeout"] = get_env_safe(
        "AWESOME_CLI_COINGECKO_REQUEST_TIMEOUT", crypto_dict["coingecko_request_timeout"], int
    )
    crypto_dict["coingecko_rate_limit_requests"] = get_env_safe(
        "AWESOME_CLI_COINGECKO_RATE_LIMIT_REQUESTS", crypto_dict["coingecko_rate_limit_requests"], int
    )
    crypto_dict["cache_ttl_minutes"] = get_env_safe(
        "AWESOME_CLI_CACHE_TTL_MINUTES", crypto_dict["cache_ttl_minutes"], int
    )
    crypto_dict["cache_ttl_metadata_hours"] = get_env_safe(
        "AWESOME_CLI_CACHE_TTL_METADATA_HOURS", crypto_dict["cache_ttl_metadata_hours"], int
    )
    crypto_dict["scheduler_interval_minutes"] = get_env_safe(
        "AWESOME_CLI_SCHEDULER_INTERVAL_MINUTES", crypto_dict["scheduler_interval_minutes"], int
    )
    crypto_dict["storage_path"] = os.getenv(
        "AWESOME_CLI_STORAGE_PATH", crypto_dict["storage_path"]
    )
    crypto_dict["redis_url"] = os.getenv(
        "AWESOME_CLI_REDIS_URL", crypto_dict["redis_url"]
    )
    crypto_dict["use_redis"] = get_env_safe(
        "AWESOME_CLI_USE_REDIS", crypto_dict["use_redis"], bool
    )

    # Reconstruct objects
    # We must convert the dictionary back to CryptoSettings object
    settings_dict["crypto"] = CryptoSettings(**crypto_dict)

    return Settings(**settings_dict)
