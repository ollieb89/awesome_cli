"""
Tests for core services.
"""
from pathlib import Path
from unittest.mock import patch, Mock

from awesome_cli.core import services
from awesome_cli.core.models import JobResult


def test_initialize_app_state(tmp_path):
    # Mock get_app_dir to return a temporary directory
    mock_config_path = tmp_path / "test_config"
    mock_storage_file = tmp_path / "data" / "crypto_assets.json"

    with patch("awesome_cli.core.services.get_app_dir") as mock_get_app_dir, \
         patch("awesome_cli.core.services.config.load_settings") as mock_load_settings:

        mock_get_app_dir.return_value = mock_config_path

        # Mock settings
        mock_settings = Mock()
        mock_settings.crypto.storage_path = str(mock_storage_file)
        mock_load_settings.return_value = mock_settings

        result = services.initialize_app_state()

        # Verify get_app_dir was called with correct app name
        mock_get_app_dir.assert_called_once_with("awesome_cli")

        # Verify config directory was created
        assert mock_config_path.exists()
        assert mock_config_path.is_dir()

        # Verify storage directory was created
        assert mock_storage_file.parent.exists()
        assert mock_storage_file.parent.is_dir()

        # Verify result
        assert isinstance(result, dict)
        assert result["status"] == "initialized"
        assert result["path"] == str(mock_config_path.absolute())
        assert result["storage_path"] == str(mock_storage_file.parent.absolute())

def test_run_job():
    name = "test_job"
    result = services.run_job(name)
    assert isinstance(result, JobResult)
    assert result.job_name == name
    assert result.status == "success"
    assert "completed successfully" in result.message
