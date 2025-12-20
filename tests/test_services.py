
from pathlib import Path
from unittest.mock import patch
from awesome_cli.core.services import initialize_app_state, run_job
from awesome_cli.config import load_settings
from awesome_cli.core.models import JobResult

def test_initialize_app_state_creates_directories(tmp_path: Path):
    # Setup
    # Use tmp_path for isolation
    test_storage_file = tmp_path / "data" / "crypto_assets.json"
    fake_config_dir = tmp_path / "config"

    # Mock settings
    settings = load_settings()
    settings.crypto.storage_path = str(test_storage_file)

    # Mock get_app_dir to return a temp path
    with patch("awesome_cli.core.services.get_app_dir", return_value=fake_config_dir):
        # Act
        result = initialize_app_state(settings=settings)

    # Assert
    assert result["status"] == "initialized"
    assert "config_path" in result
    assert "crypto_storage_path" in result
    # Backward compatibility
    assert "path" in result
    assert result["path"] == str(fake_config_dir.absolute())
    assert result["config_path"] == str(fake_config_dir.absolute())

    # Verify config dir created
    assert fake_config_dir.exists()
    assert fake_config_dir.is_dir()

def test_initialize_app_state(tmp_path):
    # Mock get_config_dir and get_data_dir to return temporary directories
    with patch("awesome_cli.core.services.get_config_dir") as mock_get_config_dir, \
         patch("awesome_cli.core.services.get_data_dir") as mock_get_data_dir:

        mock_config_path = tmp_path / "test_config"
        mock_data_path = tmp_path / "test_data"

        mock_get_config_dir.return_value = mock_config_path
        mock_get_data_dir.return_value = mock_data_path

        # Mock settings
        mock_settings = Mock()
        mock_settings.crypto.storage_path = str(mock_storage_file)
        mock_load_settings.return_value = mock_settings


        # Verify calls
        mock_get_config_dir.assert_called_once_with("awesome_cli")
        mock_get_data_dir.assert_called_once_with("awesome_cli")

        # Verify directories were created
        assert mock_config_path.exists()
        assert mock_config_path.is_dir()
        assert mock_data_path.exists()
        assert mock_data_path.is_dir()

        # Verify storage directory was created
        assert mock_storage_file.parent.exists()
        assert mock_storage_file.parent.is_dir()

        # Verify result
        assert isinstance(result, dict)
        assert result["status"] == "initialized"
        assert result["path"] == str(mock_config_path.absolute())
        assert result["storage_path"] == str(mock_storage_file.parent.absolute())

def test_run_job():
    """Test the run_job function."""
    job_name = "test_job"
    result = run_job(job_name)

    assert isinstance(result, JobResult)
    assert result.job_name == job_name
    assert result.status == "success"
    assert "completed successfully" in result.message
