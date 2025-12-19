"""
Tests for core logic.
"""
from awesome_cli import core

def test_initialize_app_state():
    result = core.initialize_app_state()
    assert isinstance(result, dict)
    assert result["status"] == "initialized"

def test_run_job():
    name = "test_job"
    result = core.run_job(name)
    assert "completed successfully" in result
    assert name in result
