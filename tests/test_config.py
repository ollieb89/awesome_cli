"""
Tests for configuration loading, including deep merge logic.
"""
import json
from awesome_cli.config import load_settings, _deep_merge_dict

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

def test_deep_merge_utility_edge_cases():
    # Empty dicts
    target = {"a": 1}
    source = {}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 1}

    target = {}
    source = {"a": 1}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 1}

    # Non-dict values overwriting
    target = {"a": {"b": 1}}
    source = {"a": 2}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 2}

    # Deeper nesting
    target = {"l1": {"l2": {"l3": 1, "keep": 2}}}
    source = {"l1": {"l2": {"l3": 99}}}
    result = _deep_merge_dict(target, source)
    assert result["l1"]["l2"]["l3"] == 99
    assert result["l1"]["l2"]["keep"] == 2

    # New keys in source
    target = {"a": 1}
    source = {"b": 2}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 1, "b": 2}
