"""
Path helpers for Awesome CLI.
"""
from pathlib import Path
from platformdirs import user_config_dir


def get_project_root() -> Path:
    """Return the root directory of the project."""
    return Path(__file__).parent.parent.parent.parent


def get_app_dir(app_name: str) -> Path:
    """Return the application configuration directory."""
    return Path(user_config_dir(app_name))
