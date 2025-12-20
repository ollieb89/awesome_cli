"""
Core services and business logic for Awesome CLI.
"""
import logging
from typing import Dict

from pathlib import Path
from awesome_cli.core import io
from awesome_cli.core.models import JobResult
from awesome_cli.utils.paths import get_app_dir
from awesome_cli.config import load_settings

logger = logging.getLogger(__name__)

def initialize_app_state() -> Dict[str, str]:
    """
    Perform initialization tasks (e.g., creating directories, DB init).
    """
    logger.info("Initializing application state...")

    # Ensure config directory exists
    config_path = get_app_dir("awesome_cli")
    io.ensure_directory(config_path)
    logger.info(f"Ensured configuration directory exists at {config_path}")

    # Ensure storage directory exists
    settings = load_settings()
    storage_path = Path(settings.crypto.storage_path)
    io.ensure_directory(storage_path.parent)
    logger.info(f"Ensured storage directory exists at {storage_path.parent}")

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
