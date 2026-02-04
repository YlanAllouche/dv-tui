"""
dv-tui: A curses-based TUI for viewing JSON/CSV data with nvim integration.
"""

__version__ = "0.1.0"
__author__ = "Ylan Allouche"

from .core import TUI
from .table import Table
from .config import load_config, DEFAULT_CONFIG
from .data_loaders import load_file, load_json, load_csv
from .cli import main

__all__ = [
    "TUI",
    "Table",
    "load_config",
    "DEFAULT_CONFIG",
    "load_file",
    "load_json",
    "load_csv",
    "main",
]
