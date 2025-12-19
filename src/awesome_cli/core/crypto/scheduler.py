"""
Crypto Data Scheduler
=====================

Handles background refreshing of crypto data.
"""

import logging
import threading

from awesome_cli.config import CryptoSettings
from awesome_cli.core.crypto.fetcher import CryptoDataFetcher
from awesome_cli.core.crypto.repository import CryptoAssetRepository

logger = logging.getLogger(__name__)

class CryptoDataScheduler:
    """
    Scheduler to periodically fetch and update crypto data.
    """

    def __init__(
        self,
        settings: CryptoSettings,
        fetcher: CryptoDataFetcher,
        repository: CryptoAssetRepository
    ):
        self.interval = settings.scheduler_interval_minutes * 60
        self.fetcher = fetcher
        self.repository = repository
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the background scheduler thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Scheduler is already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info(f"Crypto data scheduler started (interval: {self.interval}s)")

    def stop(self) -> None:
        """Stop the background scheduler."""
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            logger.info("Crypto data scheduler stopped.")

    def _run_loop(self) -> None:
        """Main loop for the scheduler thread."""
        while not self._stop_event.is_set():
            try:
                self.refresh_now()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")

            # Wait for interval or stop signal
            if self._stop_event.wait(self.interval):
                break

    def refresh_now(self) -> None:
        """
        Trigger an immediate refresh of data.
        Fetches from API and updates repository.
        """
        logger.info("Starting scheduled data refresh...")
        try:
            data = self.fetcher.fetch_top_coins(limit=50)
            if data:
                self.repository.upsert(data)
                logger.info(f"Successfully refreshed {len(data)} assets.")
            else:
                logger.warning("No data fetched.")
        except Exception as e:
            logger.error(f"Failed to refresh data: {e}")
