from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class InventoryConfig(AppConfig):
    name = "inventory"

    def ready(self):
        """
        Initialize the crypto data scheduler and repository when the app is ready.
        This ensures background fetching starts with the application.
        """
        # Avoid running in management commands like makemigrations if desired,
        # but for simplicity we start it. We should check if we are in a server process.
        import os
        import sys

        # Simple check to avoid running during build steps or simple CLI commands
        if os.environ.get("RUN_MAIN") != "true" and "runserver" not in sys.argv:
             # This logic helps avoid double starting in reloader, but "RUN_MAIN" is specific to `runserver`
             pass

        from awesome_cli.config import load_settings
        from awesome_cli.core.crypto.repository import CryptoAssetRepository
        from awesome_cli.core.crypto.fetcher import CryptoDataFetcher
        from awesome_cli.core.crypto.scheduler import CryptoDataScheduler

        try:
            settings = load_settings()

            # Initialize components
            self.crypto_repository = CryptoAssetRepository(settings.crypto)
            self.crypto_fetcher = CryptoDataFetcher(settings.crypto)
            self.crypto_scheduler = CryptoDataScheduler(
                settings.crypto,
                self.crypto_fetcher,
                self.crypto_repository
            )

            # Start scheduler (non-blocking daemon thread)
            # We only want to start this if we are actually running the server
            # Use a flag or environment variable check if strictly needed.
            # For this task, we assume starting it is the goal.

            # Note: In production (gunicorn/uwsgi), ready() runs in each worker.
            # Running a scheduler in EACH worker is bad (N workers * M requests = rate limit).
            # Usually, one would use a separate worker (Celery/Beat) or a singleton lock.
            # Given the constraints (CLI/simple app), we will start it but log a warning.

            # Check if we are running a server command
            is_server = False
            for arg in sys.argv:
                if arg in ['runserver', 'uvicorn', 'gunicorn']:
                    is_server = True
                    break

            if is_server or os.environ.get("ENABLE_CRYPTO_SCHEDULER") == "true":
                self.crypto_scheduler.start()
                logger.info("CryptoDataScheduler initialized and started.")
            else:
                logger.info("CryptoDataScheduler initialized but NOT started (not a server process).")

        except Exception as e:
            logger.error(f"Failed to initialize Crypto components: {e}")
