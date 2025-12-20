"""
Tests for core services.
"""
from pathlib import Path
from unittest.mock import patch

from awesome_cli.core import services
from awesome_cli.core.models import JobResult


def test_initialize_app_state(tmp_path):
    # Mock get_config_dir and get_data_dir to return temporary directories
    with patch("awesome_cli.core.services.get_config_dir") as mock_get_config_dir, \
         patch("awesome_cli.core.services.get_data_dir") as mock_get_data_dir:

        mock_config_path = tmp_path / "test_config"
        mock_data_path = tmp_path / "test_data"

        mock_get_config_dir.return_value = mock_config_path
        mock_get_data_dir.return_value = mock_data_path

        result = services.initialize_app_state()

        # Verify calls
        mock_get_config_dir.assert_called_once_with("awesome_cli")
        mock_get_data_dir.assert_called_once_with("awesome_cli")

        # Verify directories were created
        assert mock_config_path.exists()
        assert mock_config_path.is_dir()
        assert mock_data_path.exists()
        assert mock_data_path.is_dir()

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
