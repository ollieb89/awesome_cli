"""
Domain models and types for Awesome CLI.
"""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class JobResult:
    """Result of a job execution."""
    job_name: str
    status: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
