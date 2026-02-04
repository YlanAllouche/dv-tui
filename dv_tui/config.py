import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union


DEFAULT_CONFIG = {
    "columns": ["type", "status", "summary"],
    "column_widths": {"type": 8, "status": 12},
    "keybinds": {
        "leader": ord(';'),
        "quit": [ord('q'), ord('Q')],
        "down": [ord('j'), ord('J'), 258],
        "up": [ord('k'), ord('K'), 259],
        "left": [ord('h'), ord('H'), 260],
        "right": [ord('l'), ord('L'), 261],
        "search": ord('/'),
        "enter": [ord('\n'), 10],
        "escape": 27,
        "backspace": [263, 127],
    },
    "colors": {
        "type": {"work": (5, True), "study": (6, True)},
        "status": {
            "focus": (2, True),
            "active": (3, True),
        },
        "date": {"prefix": "2025-", "color": 4},
    },
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file, or return defaults."""
    config = DEFAULT_CONFIG.copy()
    
    if not config_path:
        config_path = os.path.expanduser("~/.config/dv/config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            config = merge_configs(config, user_config)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    
    return config


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two config dictionaries."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def get_column_widths(config: Dict[str, Any], terminal_width: int) -> List[int]:
    """
    Calculate column widths based on config and terminal size.
    The last column gets remaining space.
    """
    columns = config.get("columns", ["type", "status", "summary"])
    column_widths = config.get("column_widths", {})
    
    widths = []
    remaining_width = terminal_width - (len(columns) - 1) - 2  # Subtract separators and margins
    
    for i, col in enumerate(columns[:-1]):
        width = column_widths.get(col, 10)
        widths.append(width)
        remaining_width -= width
    
    widths.append(max(1, remaining_width))
    return widths
