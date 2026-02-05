"""
dv-tui: A curses-based TUI for viewing JSON/CSV data with nvim integration.
"""

__version__ = "0.1.0"
__author__ = "Ylan Allouche"

from .core import TUI
from .table import Table
from .config import load_config, load_config_from_inline_json, DEFAULT_CONFIG, validate_config, get_column_widths, Config
from .data_loaders import load_file

def main():
    """Import and run CLI main function lazily to avoid circular import."""
    from .cli import main as cli_main
    return cli_main()

__all__ = [
    "TUI",
    "Table",
    "Config",
    "load_config",
    "load_config_from_inline_json",
    "validate_config",
    "get_column_widths",
    "DEFAULT_CONFIG",
    "load_file",
    "main",
]
