import json
import csv
import sys
import select
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import subprocess


def filter_config_items(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out items that only contain _config key from data.
    
    Returns data with config-only items removed.
    """
    filtered = []
    for item in data:
        if "_config" in item and len(item) == 1:
            continue
        if "_config" in item:
            filtered.append({k: v for k, v in item.items() if k != "_config"})
        else:
            filtered.append(item)
    return filtered


class DataLoader(ABC):
    """Abstract base class for data loaders."""
    
    def __init__(self, source: str):
        self.source = source
    
    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        """Load data from source."""
        pass
    
    def get_source_info(self) -> str:
        """Get human-readable source information."""
        return self.source
    
    def can_refresh(self) -> bool:
        """Check if this data source supports refresh."""
        return False
    
    def refresh(self) -> List[Dict[str, Any]]:
        """Refresh data from source. Raises NotImplementedError if not supported."""
        raise NotImplementedError(f"Refresh not supported for {self.__class__.__name__}")


def union_keys(data: List[Dict[str, Any]]) -> List[str]:
    """Get union of all keys from all dictionaries in data."""
    keys = set()
    for item in data:
        keys.update(item.keys())
    return sorted(keys)


def fill_missing_keys(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fill missing keys with empty strings, converting None to empty string."""
    if not data:
        return data
    
    all_keys = union_keys(data)
    result = []
    
    for item in data:
        filled = {}
        for key in all_keys:
            value = item.get(key)
            if value is None:
                value = ""
            filled[key] = value
        result.append(filled)
    
    return result


class JsonDataLoader(DataLoader):
    """Load JSON data from file or inline string."""
    
    def __init__(self, source: str):
        super().__init__(source)
        # File descriptors from process substitution are always files
        # even if Path.exists() returns False at initialization time
        # Linux uses /dev/fd/ or /proc/self/fd/ or /proc/<pid>/fd/
        if (source.startswith('/dev/fd/') or
            source.startswith('/proc/self/fd/') or
            (source.startswith('/proc/') and '/fd/' in source)):
            self._is_file = True
        else:
            self._is_file = (
                Path(source).exists()
                if not (source.startswith('[') or source.startswith('{'))
                else False
            )
    
    def load(self) -> List[Dict[str, Any]]:
        """Load JSON data from file or inline string."""
        if self._is_file:
            return self._load_file()
        else:
            return self._load_inline()
    
    def get_source_info(self) -> str:
        """Get source info with type information."""
        if self._is_file:
            return f"JSON file: {self.source}"
        else:
            return f"Inline JSON"
    
    def can_refresh(self) -> bool:
        """JSON files can be refreshed."""
        return self._is_file
    
    def refresh(self) -> List[Dict[str, Any]]:
        """Reload data from file."""
        if not self.can_refresh():
            raise NotImplementedError("Cannot refresh inline JSON")
        return self._load_file()
    
    def _load_file(self) -> List[Dict[str, Any]]:
        """Load JSON from file."""
        try:
            with open(self.source, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise Exception(f"JSON must be a list of objects, got {type(data).__name__}")
            
            # Filter out _config items
            data = filter_config_items(data)
            return fill_missing_keys(data)
        except FileNotFoundError:
            raise Exception(f"{self.source} not found")
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON in {self.source}"
            if hasattr(e, 'lineno'):
                msg += f" at line {e.lineno}"
            if hasattr(e, 'colno') and e.colno is not None:
                msg += f", column {e.colno}"
            msg += f": {e.msg}"
            raise Exception(msg)
    
    def _load_inline(self) -> List[Dict[str, Any]]:
        """Load JSON from inline string."""
        try:
            data = json.loads(self.source)
            
            if not isinstance(data, list):
                raise Exception(f"JSON must be a list of objects, got {type(data).__name__}")
            
            # Filter out _config items
            data = filter_config_items(data)
            return fill_missing_keys(data)
        except json.JSONDecodeError as e:
            msg = "Invalid JSON"
            if hasattr(e, 'lineno'):
                msg += f" at position {e.pos}"
            msg += f": {e.msg}"
            raise Exception(msg)


class CsvDataLoader(DataLoader):
    """Load CSV data from file."""
    
    def __init__(self, source: str, delimiter: str = ','):
        super().__init__(source)
        self.delimiter = delimiter
    
    def load(self) -> List[Dict[str, Any]]:
        """Load CSV data from file."""
        try:
            with open(self.source, 'r', newline='') as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                data = list(reader)
            
            return fill_missing_keys(data)
        except FileNotFoundError:
            raise Exception(f"{self.source} not found")
        except csv.Error as e:
            raise Exception(f"CSV error in {self.source}: {e}")
        except Exception as e:
            raise Exception(f"Error reading CSV {self.source}: {e}")
    
    def get_source_info(self) -> str:
        """Get source info with delimiter."""
        delim_repr = "'" + self.delimiter + "'" if self.delimiter == ',' else f"'{self.delimiter}'"
        return f"CSV file: {self.source} (delimiter: {delim_repr})"
    
    def can_refresh(self) -> bool:
        """CSV files can be refreshed."""
        return True
    
    def refresh(self) -> List[Dict[str, Any]]:
        """Reload data from file."""
        return self.load()


class StdinDataLoader(DataLoader):
    """Load JSON data from stdin with timeout."""
    
    def __init__(self, timeout: Optional[float] = 30, command: Optional[str] = None):
        super().__init__("stdin")
        self.timeout = timeout
        self.command = command
        self._stdin_data = None
    
    def _capture_stdin(self) -> None:
        """Capture all data from stdin before curses initialization."""
        if self._stdin_data is not None:
            return  # Already captured
        
        if self.timeout is None or self.timeout > 0:
            if not self._wait_for_stdin_data(self.timeout):
                raise Exception(f"Timeout waiting for stdin data after {self.timeout} seconds")
        
        self._stdin_data = sys.stdin.read()
        
        if not self._stdin_data.strip():
            raise Exception("No data provided via stdin")
    
    def load(self) -> List[Dict[str, Any]]:
        """Load JSON data from stdin with timeout."""
        # Capture stdin data first
        self._capture_stdin()
        
        try:
            data = json.loads(self._stdin_data)
            
            if not isinstance(data, list):
                raise Exception(f"JSON from stdin must be a list of objects, got {type(data).__name__}")
            
            return fill_missing_keys(data)
        except json.JSONDecodeError as e:
            msg = "Invalid JSON from stdin"
            if hasattr(e, 'lineno'):
                msg += f" at line {e.lineno}"
            if hasattr(e, 'colno') and e.colno is not None:
                msg += f", column {e.colno}"
            msg += f": {e.msg}"
            raise Exception(msg)
    
    def get_source_info(self) -> str:
        """Get source info with timeout."""
        if self.timeout is None or self.timeout == 0:
            return "Stdin (no timeout)"
        else:
            return f"Stdin (timeout: {self.timeout}s)"
    
    def _wait_for_stdin_data(self, timeout: float) -> bool:
        """Wait for data to be available on stdin with timeout."""
        import select
        
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        return len(ready) > 0
    
    def can_refresh(self) -> bool:
        """Check if this data source supports refresh."""
        return self.command is not None
    
    def refresh(self) -> List[Dict[str, Any]]:
        """Refresh data by re-running the command."""
        if not self.can_refresh():
            raise NotImplementedError("Cannot refresh stdin without command")
        
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            data_str = result.stdout
            
            try:
                data = json.loads(data_str)
                
                if not isinstance(data, list):
                    raise Exception(f"JSON from command must be a list of objects, got {type(data).__name__}")
                
                return fill_missing_keys(data)
            except json.JSONDecodeError as e:
                msg = "Invalid JSON from command output"
                if hasattr(e, 'lineno'):
                    msg += f" at line {e.lineno}"
                if hasattr(e, 'colno') and e.colno is not None:
                    msg += f", column {e.colno}"
                msg += f": {e.msg}"
                raise Exception(msg)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed: {e}")


def get_file_mtime(file_path: str) -> Optional[float]:
    """Get the modification time of a file."""
    try:
        return Path(file_path).stat().st_mtime
    except (FileNotFoundError, OSError):
        return None


def load_file(file_path: str, delimiter: str = ',') -> List[Dict[str, Any]]:
    """
    Load data from a file (JSON or CSV).
    Detects format based on file extension.
    
    Args:
        file_path: Path to the file
        delimiter: Delimiter for CSV files (default: ',')
    
    Returns:
        List of dictionaries
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    # Check if it's a file descriptor from process substitution
    # These are created by bash's <(...) syntax and should be read as JSON
    is_fd_path = (file_path.startswith('/dev/fd/') or
                  file_path.startswith('/proc/self/fd/') or
                  (file_path.startswith('/proc/') and '/fd/' in file_path))
    
    if ext == '.json' or is_fd_path:
        loader = JsonDataLoader(file_path)
        return loader.load()
    elif ext == '.csv':
        loader = CsvDataLoader(file_path, delimiter=delimiter)
        return loader.load()
    else:
        raise Exception(f"Unsupported file format: {ext}")


def create_loader(source: str, stdin_timeout: Optional[float] = None,
                  delimiter: str = ',', command: Optional[str] = None) -> DataLoader:
    """
    Create appropriate DataLoader based on source type.

    Args:
        source: Source string (file path, inline JSON, or 'stdin')
        stdin_timeout: Timeout for stdin in seconds (None = no timeout)
        delimiter: Delimiter for CSV files
        command: Command to regenerate data (for stdin refresh)

    Returns:
        DataLoader instance
    """
    if source == 'stdin':
        return StdinDataLoader(stdin_timeout, command)

    # Check if it's a file descriptor from process substitution
    # These are created by bash's <(...) syntax and should be read as JSON
    # Linux uses /dev/fd/ or /proc/self/fd/ or /proc/<pid>/fd/
    if (source.startswith('/dev/fd/') or 
        source.startswith('/proc/self/fd/') or
        (source.startswith('/proc/') and '/fd/' in source)):
        return JsonDataLoader(source)

    if Path(source).exists():
        path = Path(source)
        if path.suffix.lower() == '.json':
            return JsonDataLoader(source)
        elif path.suffix.lower() == '.csv':
            return CsvDataLoader(source, delimiter=delimiter)
        else:
            raise Exception(f"Unsupported file format: {path.suffix}")

    if source.startswith('[') or source.startswith('{'):
        return JsonDataLoader(source)

    raise Exception(f"Cannot load from source: {source}")


def is_stdin_available() -> bool:
    """Check if stdin has actual data available (piped, not TTY or /dev/null)."""
    import select
    
    # If stdin is a TTY (interactive terminal), no data
    try:
        if sys.stdin.isatty():
            return False
    except (ValueError, OSError):
        # Stdin is closed or invalid
        return False
    
    # Check if there's actual readable data on stdin
    try:
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)
        return len(ready) > 0
    except (ValueError, OSError, IOError):
        # Can't check (e.g., stdin is closed), assume no data
        return False


def detect_source(files: List[str]) -> str:
    """
    Detect data source from command-line arguments.
    
    Returns:
        'file', 'stdin', or 'inline'
    """
    if not files:
        if is_stdin_available():
            return 'stdin'
        return 'file'
    
    if len(files) == 1 and (files[0].startswith('[') or files[0].startswith('{')):
        return 'inline'
    
    return 'file'
