import json
import csv
import sys
from pathlib import Path
from typing import List, Dict, Any, Union, Optional


def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise Exception(f"JSON must be a list of objects")
        return data
    except FileNotFoundError:
        raise Exception(f"{file_path} not found")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in {file_path}: {e}")


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """Load data from a CSV file."""
    try:
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return data
    except FileNotFoundError:
        raise Exception(f"{file_path} not found")
    except Exception as e:
        raise Exception(f"Error reading CSV {file_path}: {e}")


def load_stdin() -> List[Dict[str, Any]]:
    """Load data from stdin (expects JSON)."""
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, list):
            raise Exception("JSON from stdin must be a list of objects")
        return data
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON from stdin: {e}")


def load_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load data from a file (JSON or CSV).
    Detects format based on file extension.
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == '.json':
        return load_json(file_path)
    elif ext == '.csv':
        return load_csv(file_path)
    else:
        raise Exception(f"Unsupported file format: {ext}")


def get_file_mtime(file_path: str) -> Optional[float]:
    """Get the modification time of a file."""
    try:
        return Path(file_path).stat().st_mtime
    except (FileNotFoundError, OSError):
        return None
