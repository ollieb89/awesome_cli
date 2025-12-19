"""
Configuration management for Awesome CLI.
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

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

@dataclass
class CryptoSettings:
    """Settings for Crypto Data Fetching."""
    coingecko_api_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_request_timeout: int = 10
    coingecko_rate_limit_requests: int = 50
    cache_ttl_minutes: int = 5
    cache_ttl_metadata_hours: int = 24
    scheduler_interval_minutes: int = 5
    storage_path: str = "data/crypto_assets.json"
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
    1. Config file (if provided)
    2. Environment variables (prefixed with AWESOME_CLI_)
    3. Defaults
    """
    # Defaults are handled by the Settings dataclass defaults
    defaults: Dict[str, Any] = {}
    crypto_defaults: Dict[str, Any] = {}
    
    # 2. Config file overrides (if implemented in future)
    if config_path:
        path = Path(config_path)
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    if isinstance(file_data, dict):
                        # Extract top level settings
                        for k, v in file_data.items():
                            if k != "crypto":
                                defaults[k] = v
                        # Extract crypto settings
                        if "crypto" in file_data:
                            crypto_defaults.update(file_data["crypto"])
            except Exception:
                pass

    # 1. Environment variables override everything
    env = os.getenv("AWESOME_CLI_ENV", defaults.get("env", "production"))
    log_level = os.getenv("AWESOME_CLI_LOG_LEVEL", defaults.get("log_level", "INFO"))

    # Crypto environment variables
    crypto_settings = CryptoSettings(
        coingecko_api_base_url=os.getenv("AWESOME_CLI_COINGECKO_API_BASE_URL", crypto_defaults.get("coingecko_api_base_url", "https://api.coingecko.com/api/v3")),
        coingecko_request_timeout=get_env_safe("AWESOME_CLI_COINGECKO_REQUEST_TIMEOUT", crypto_defaults.get("coingecko_request_timeout", 10), int),
        coingecko_rate_limit_requests=get_env_safe("AWESOME_CLI_COINGECKO_RATE_LIMIT_REQUESTS", crypto_defaults.get("coingecko_rate_limit_requests", 50), int),
        cache_ttl_minutes=get_env_safe("AWESOME_CLI_CACHE_TTL_MINUTES", crypto_defaults.get("cache_ttl_minutes", 5), int),
        cache_ttl_metadata_hours=get_env_safe("AWESOME_CLI_CACHE_TTL_METADATA_HOURS", crypto_defaults.get("cache_ttl_metadata_hours", 24), int),
        scheduler_interval_minutes=get_env_safe("AWESOME_CLI_SCHEDULER_INTERVAL_MINUTES", crypto_defaults.get("scheduler_interval_minutes", 5), int),
        storage_path=os.getenv("AWESOME_CLI_STORAGE_PATH", crypto_defaults.get("storage_path", "data/crypto_assets.json")),
        redis_url=os.getenv("AWESOME_CLI_REDIS_URL", crypto_defaults.get("redis_url", None)),
        use_redis=get_env_safe("AWESOME_CLI_USE_REDIS", crypto_defaults.get("use_redis", False), bool),
    )

    return Settings(
        env=env,
        log_level=log_level,
        config_path=Path(config_path) if config_path else None,
        crypto=crypto_settings
    )
