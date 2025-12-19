"""
I/O operations and external integrations for Awesome CLI.
"""
from pathlib import Path


def read_file(path: Path) -> str:
    """Read content from a file."""
    return path.read_text(encoding="utf-8")

def write_file(path: Path, content: str) -> None:
    """Write content to a file."""
    path.write_text(content, encoding="utf-8")

def ensure_directory(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
