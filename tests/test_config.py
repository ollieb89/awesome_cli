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


def test_deep_merge_dict_empty_source():
    """Test merging with empty source dictionary."""
    target = {"a": 1, "b": {"c": 2}}
    source = {}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 1, "b": {"c": 2}}
    assert result is target  # Verify it's the same object


def test_deep_merge_dict_empty_target():
    """Test merging into empty target dictionary."""
    target = {}
    source = {"a": 1, "b": {"c": 2}}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 1, "b": {"c": 2}}
    assert result is target


def test_deep_merge_dict_non_dict_values():
    """Test handling non-dict values in nested structures."""
    target = {"a": 1, "b": {"c": 2, "d": 3}}
    source = {"a": 10, "b": {"c": 20}}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 10, "b": {"c": 20, "d": 3}}


def test_deep_merge_dict_override_dict_with_non_dict():
    """Test that non-dict values override dict values."""
    target = {"a": {"b": 1}}
    source = {"a": "string_value"}
    result = _deep_merge_dict(target, source)
    assert result == {"a": "string_value"}


def test_deep_merge_dict_override_non_dict_with_dict():
    """Test that dict values override non-dict values."""
    target = {"a": "string_value"}
    source = {"a": {"b": 1}}
    result = _deep_merge_dict(target, source)
    assert result == {"a": {"b": 1}}


def test_deep_merge_dict_multiple_levels():
    """Test merging multiple nested levels (4 levels deep)."""
    target = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": "original",
                    "keep": "me"
                },
                "also_keep": "this"
            }
        }
    }
    source = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": "updated"
                }
            }
        }
    }
    result = _deep_merge_dict(target, source)
    assert result["level1"]["level2"]["level3"]["level4"] == "updated"
    assert result["level1"]["level2"]["level3"]["keep"] == "me"
    assert result["level1"]["level2"]["also_keep"] == "this"


def test_deep_merge_dict_new_keys():
    """Test that new keys are added from source."""
    target = {"a": 1, "b": {"c": 2}}
    source = {"d": 3, "b": {"e": 4}}
    result = _deep_merge_dict(target, source)
    assert result == {"a": 1, "b": {"c": 2, "e": 4}, "d": 3}


def test_deep_merge_dict_lists():
    """Test that list values are replaced, not merged."""
    target = {"a": [1, 2, 3]}
    source = {"a": [4, 5]}
    result = _deep_merge_dict(target, source)
    assert result == {"a": [4, 5]}
