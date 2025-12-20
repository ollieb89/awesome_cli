from pathlib import Path
from unittest.mock import patch
import pytest
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

    # Verify crypto dir created
    assert test_storage_file.parent.exists()
    assert test_storage_file.parent.is_dir()
    assert result["crypto_storage_path"] == str(test_storage_file.parent.absolute())


def test_initialize_app_state_defaults(monkeypatch, tmp_path):
    # Setup env var to point to tmp_path for crypto path
    test_storage_file = tmp_path / "env_data" / "crypto_assets.json"
    monkeypatch.setenv("AWESOME_CLI_STORAGE_PATH", str(test_storage_file))

    fake_config_dir = tmp_path / "config"

    # Mock get_app_dir using unittest.mock.patch for consistency with other tests
    with patch("awesome_cli.core.services.get_app_dir", return_value=fake_config_dir):
        # Act
        # initialize_app_state loads settings internally if not passed
        result = initialize_app_state()

    # Assert
    # Verify config dir created
    assert fake_config_dir.exists()

    # Verify crypto dir created
    assert test_storage_file.parent.exists()
    assert result["crypto_storage_path"] == str(test_storage_file.parent.absolute())


def test_initialize_app_state_handles_directory_creation_error(tmp_path):
    """Test that errors during directory creation are properly propagated."""
    # Setup
    fake_config_dir = tmp_path / "config"
    test_storage_file = tmp_path / "data" / "crypto_assets.json"
    
    settings = load_settings()
    settings.crypto.storage_path = str(test_storage_file)
    
    # Mock ensure_directory to raise an exception
    with patch("awesome_cli.core.services.get_app_dir", return_value=fake_config_dir):
        with patch("awesome_cli.core.services.io.ensure_directory") as mock_ensure:
            mock_ensure.side_effect = PermissionError("Cannot create directory")
            
            # Act & Assert
            with pytest.raises(PermissionError, match="Cannot create directory"):
                initialize_app_state(settings=settings)


def test_run_job():
    """Test the run_job function."""
    job_name = "test_job"
    result = run_job(job_name)

    assert isinstance(result, JobResult)
    assert result.job_name == job_name
    assert result.status == "success"
    assert "completed successfully" in result.message
