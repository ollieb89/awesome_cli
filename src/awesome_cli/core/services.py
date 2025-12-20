"""
Core services and business logic for Awesome CLI.
"""
import logging
from pathlib import Path
from typing import Dict

from awesome_cli import config
from awesome_cli.core import io
from awesome_cli.core.models import JobResult
from awesome_cli.utils.paths import get_config_dir, get_data_dir

logger = logging.getLogger(__name__)

def initialize_app_state(settings: Optional[config.Settings] = None) -> Dict[str, str]:
    """
    Perform initialization tasks (e.g., creating directories, DB init).
    """
    logger.info("Initializing application state...")

    # Load settings to ensure we have the correct paths
    settings = config.load_settings()

    # Ensure config directory exists
    config_path = get_config_dir("awesome_cli")
    io.ensure_directory(config_path)

    # Ensure crypto storage directory exists
    crypto_storage_path = Path(settings.crypto.storage_path)
    # The storage_path includes the filename, so we want the parent directory
    io.ensure_directory(crypto_storage_path.parent)

    return {
        "status": "initialized",
        # Kept for backward compatibility
        "path": str(config_path.absolute()),
        "config_path": str(config_path.absolute()),
        "crypto_storage_path": str(crypto_storage_path.parent.absolute())
    }
    # Ensure data directory exists
    data_path = get_data_dir("awesome_cli")
    io.ensure_directory(data_path)

    return {"status": "initialized", "path": str(config_path.absolute())}

def run_job(name: str) -> JobResult:
    """
    Execute the main job logic.
    
    Args:
        name: The name of the job to run.
    """
    logger.info(f"Running job: {name}")
    
    # Simulate some work
    message = f"Job '{name}' completed successfully."

    return JobResult(
        job_name=name,
        status="success",
        message=message
    )
