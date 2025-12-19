"""
Logging configuration for Awesome CLI.
"""
import logging
import sys

from awesome_cli.config import Settings


def setup_logging(settings: Settings) -> None:
    """
    Configure the root logger based on settings.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Example: Lower level for some noisy libraries if needed
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
