"""
Utilities package.
"""
# We do not import setup_logging here to avoid circular imports if logging imports config.
# If setup_logging is needed, import it from awesome_cli.utils.logging directly.
from awesome_cli.utils.paths import get_config_dir, get_data_dir, get_project_root

__all__ = ["get_project_root", "get_config_dir", "get_data_dir"]
