"""
Cache Manager
=============

Handles caching of crypto data to minimize API calls and improve performance.
Supports in-memory caching with TTL (Time-To-Live).
"""

import logging
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Simple in-memory cache manager with TTL support.
    Can be extended to support Redis or other backends.
    Thread-safe for concurrent access.
    """

    def __init__(self, ttl_minutes: int = 5):
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self.default_ttl = timedelta(minutes=ttl_minutes)
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        Returns None if key doesn't exist or is expired.
        """
        with self._lock:
            if key not in self._cache:
                logger.debug(f"Cache miss for key: {key}")
                return None

            value, expiry = self._cache[key]
            if datetime.now() > expiry:
                logger.debug(f"Cache expired for key: {key}")
                del self._cache[key]
                return None

            logger.debug(f"Cache hit for key: {key}")
            return value

    def set(self, key: str, value: Any, ttl_minutes: Optional[int] = None) -> None:
        """
        Store a value in the cache with an optional TTL override.
        """
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes is not None else self.default_ttl
        expiry = datetime.now() + ttl
        with self._lock:
            self._cache[key] = (value, expiry)
        logger.debug(f"Cached key: {key} (expires in {ttl})")

    def invalidate(self, key: str) -> None:
        """Remove a key from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()
