"""
Path helpers for Awesome CLI.
"""
from pathlib import Path


def get_project_root() -> Path:
    """Return the root directory of the project."""
    return Path(__file__).parent.parent.parent.parent

def get_app_dir(app_name: str) -> Path:
    """Return the application data directory (e.g. ~/.config/app_name)."""
    # This is a simple implementation. In a real app, use platformdirs or similar.
    home = Path.home()
    return home / ".config" / app_name
