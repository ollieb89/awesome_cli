
import json
from pathlib import Path
from awesome_cli import config

def test_load_settings_from_file(tmp_path):
    """Test loading settings from a JSON file."""
    config_file = tmp_path / "config.json"
    config_data = {
        "app_name": "TestApp",
        "env": "test",
        "max_retries": 5,
        "crypto": {
            "coingecko_api_base_url": "https://test.coingecko.com"
        }
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    settings = config.load_settings(str(config_file))

    assert settings.app_name == "TestApp"
    assert settings.env == "test"
    assert settings.max_retries == 5
    assert settings.crypto.coingecko_api_base_url == "https://test.coingecko.com"

def test_load_settings_env_override(tmp_path, monkeypatch):
    """Test environment variables overriding file settings."""
    config_file = tmp_path / "config.json"
    config_data = {
        "app_name": "TestApp",
        "max_retries": 5
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    monkeypatch.setenv("AWESOME_CLI_APP_NAME", "EnvApp")

    monkeypatch.setenv("AWESOME_CLI_ENV", "staging")
    monkeypatch.setenv("AWESOME_CLI_COINGECKO_API_BASE_URL", "https://env.coingecko.com")

    settings = config.load_settings(str(config_file))

    assert settings.env == "staging"
    assert settings.max_retries == 5 # From file
    assert settings.crypto.coingecko_api_base_url == "https://env.coingecko.com"
