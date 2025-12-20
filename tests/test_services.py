"""
Tests for core services.
"""
from pathlib import Path
from unittest.mock import patch

from awesome_cli.core import services
from awesome_cli.core.models import JobResult


def test_initialize_app_state(tmp_path):
    # Mock get_app_dir to return a temporary directory
    with patch("awesome_cli.core.services.get_app_dir") as mock_get_app_dir:
        mock_config_path = tmp_path / "test_config"
        mock_get_app_dir.return_value = mock_config_path

        result = services.initialize_app_state()

        # Verify get_app_dir was called with correct app name
        mock_get_app_dir.assert_called_once_with("awesome_cli")

        # Verify directory was created
        assert mock_config_path.exists()
        assert mock_config_path.is_dir()

        # Verify result
        assert isinstance(result, dict)
        assert result["status"] == "initialized"
        assert result["path"] == str(mock_config_path.absolute())

def test_run_job():
    name = "test_job"
    result = services.run_job(name)
    assert isinstance(result, JobResult)
    assert result.job_name == name
    assert result.status == "success"
    assert "completed successfully" in result.message
