"""
Core module for Awesome CLI.
"""
from awesome_cli.core.models import JobResult
from awesome_cli.core.services import initialize_app_state, run_job

__all__ = ["initialize_app_state", "run_job", "JobResult"]
