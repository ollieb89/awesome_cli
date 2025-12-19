"""
Tests for core models.
"""
from awesome_cli.core.models import JobResult


def test_job_result_creation():
    result = JobResult(job_name="test", status="success", message="done")
    assert result.job_name == "test"
    assert result.status == "success"
    assert result.data == {}
