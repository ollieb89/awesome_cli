import json
import logging
from src.awesome_cli.config import load_settings

def test_load_settings_invalid_config_file(caplog, tmp_path):
    """Verify that load_settings logs a warning when a bad config file is provided."""
    config_path = tmp_path / "bad_config.json"
    config_path.write_text("{invalid json", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        load_settings(str(config_path))

    assert "Failed to load config file" in caplog.text
    assert str(config_path) in caplog.text

def test_load_settings_valid_config_file(tmp_path):
    """Verify that load_settings works with a valid config file."""
    config_path = tmp_path / "good_config.json"
    data = {"log_level": "DEBUG", "crypto": {"cache_ttl_minutes": 99}}
    config_path.write_text(json.dumps(data), encoding="utf-8")

    settings = load_settings(str(config_path))
    assert settings.log_level == "DEBUG"
    assert settings.crypto.cache_ttl_minutes == 99
