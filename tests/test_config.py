"""
Tests for configuration loading, including deep merge logic.
"""
import json
from pathlib import Path
from awesome_cli.config import load_settings, Settings, CryptoSettings

def test_deep_merge_config(tmp_path):
    # Create a dummy config file
    config_content = {
        "log_level": "DEBUG",
        "crypto": {
            "coingecko_request_timeout": 999
        }
    }
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(config_content, f)

    settings = load_settings(str(config_path))

    # Check updated fields
    assert settings.log_level == "DEBUG"
    assert settings.crypto.coingecko_request_timeout == 999

    # Check default fields are preserved (deep merge)
    assert settings.crypto.coingecko_api_base_url == "https://api.coingecko.com/api/v3"
