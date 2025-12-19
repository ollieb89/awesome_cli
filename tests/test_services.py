"""
Tests for core services.
"""
from awesome_cli.core import services
from awesome_cli.core.models import JobResult


def test_initialize_app_state():
    result = services.initialize_app_state()
    assert isinstance(result, dict)
    assert result["status"] == "initialized"

def test_run_job():
    name = "test_job"
    result = services.run_job(name)
    assert isinstance(result, JobResult)
    assert result.job_name == name
    assert result.status == "success"
    assert "completed successfully" in result.message
