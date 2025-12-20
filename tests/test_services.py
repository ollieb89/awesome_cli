
from pathlib import Path
from unittest.mock import Mock, patch
from awesome_cli.core.services import initialize_app_state, run_job
from awesome_cli.config import Settings
from awesome_cli.core.models import JobResult

def test_initialize_app_state_creates_directories(tmp_path):
    # Setup
    fake_config_dir = tmp_path / "config"
    fake_data_dir = tmp_path / "data"
    fake_storage_path = fake_data_dir / "crypto_assets.json"

    # Mock settings
    settings = Settings()
    settings.crypto.storage_path = str(fake_storage_path)

    # Patch get_config_dir and get_data_dir
    with patch("awesome_cli.core.services.get_config_dir", return_value=fake_config_dir) as mock_config, \
         patch("awesome_cli.core.services.get_data_dir", return_value=fake_data_dir) as mock_data:

        # Act
        result = initialize_app_state(settings=settings)

    # Assert
    assert result["status"] == "initialized"
    assert result["config_path"] == str(fake_config_dir.absolute())
    assert result["crypto_storage_path"] == str(fake_data_dir.absolute())

    # Check directories created
    assert fake_config_dir.exists()
    assert fake_data_dir.exists()

def test_run_job():
    """Test the run_job function."""
    job_name = "test_job"
    result = run_job(job_name)

    assert isinstance(result, JobResult)
    assert result.job_name == job_name
    assert result.status == "success"
    assert "completed successfully" in result.message
