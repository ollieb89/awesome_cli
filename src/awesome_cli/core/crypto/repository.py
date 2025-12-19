"""
Crypto Asset Repository
=======================

Abstracts data storage and retrieval for crypto assets.
Currently supports in-memory storage backed by a JSON file for persistence.
"""

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

from awesome_cli.config import CryptoSettings

logger = logging.getLogger(__name__)

class CryptoAssetRepository:
    """
    Repository for managing crypto asset data.
    """

    def __init__(self, settings: CryptoSettings):
        self.storage_path = Path(settings.storage_path)
        self.assets: Dict[str, Dict] = {}  # Map symbol -> asset data
        self._lock = Lock()
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """Load assets from JSON file if it exists."""
        if not self.storage_path.exists():
            return

        try:
            with self._lock:
                with self.storage_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert list to dict keyed by symbol for fast lookup
                    if isinstance(data, list):
                        assets: Dict[str, Dict] = {}
                        for index, item in enumerate(data):
                            if not isinstance(item, dict):
                                logger.warning(
                                    "Skipping non-dict asset at index %s in %s",
                                    index,
                                    self.storage_path,
                                )
                                continue
                            symbol = item.get("symbol")
                            if not symbol:
                                logger.warning(
                                    'Skipping asset without "symbol" at index %s in %s',
                                    index,
                                    self.storage_path,
                                )
                                continue
                            assets[symbol] = item
                        self.assets = assets
                    elif isinstance(data, dict):
                        self.assets = data
                    else:
                        logger.warning(
                            "Unexpected data format in %s: %s",
                            self.storage_path,
                            type(data).__name__,
                        )
            logger.info(f"Loaded {len(self.assets)} assets from {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to load assets from storage: {e}")

    def save(self) -> None:
        """Persist assets to JSON file."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            with self._lock:
                # Create a snapshot of the assets inside the lock
                assets_snapshot = list(self.assets.values())
            
            # Write to file outside the lock to avoid holding it during I/O
            with self.storage_path.open("w", encoding="utf-8") as f:
                json.dump(assets_snapshot, f, indent=2)
            logger.info(f"Saved {len(assets_snapshot)} assets to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save assets to storage: {e}")

    def upsert(self, assets: List[Dict]) -> None:
        """Update or insert a list of assets."""
        with self._lock:
            for asset in assets:
                symbol = asset.get("symbol")
                if symbol:
                    self.assets[symbol] = asset
        # Auto-save after updates (lock is released before save)
        self.save()

    def get_all(self) -> List[Dict]:
        """Get all assets."""
        with self._lock:
            return list(self.assets.values())

    def get_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Get a specific asset by symbol."""
        with self._lock:
            return self.assets.get(symbol.upper())

    def get_top_by_volume(self, limit: int = 50) -> List[Dict]:
        """
        Get top assets sorted by total volume.
        """
        with self._lock:
            all_assets = list(self.assets.values())

        # Sort by volume descending. Handle None values safely.
        sorted_assets = sorted(
            all_assets,
            key=lambda x: x.get("total_volume") or 0.0,
            reverse=True
        )
        return sorted_assets[:limit]
