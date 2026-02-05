import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Literal


CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "tab_name": {
            "type": "string"
        },
        "columns": {
            "type": "array",
            "items": {"type": "string"}
        },
        "column_widths": {
            "type": "object",
            "additionalProperties": {"type": "number"}
        },
        "keybinds": {
            "type": "object",
            "properties": {
                "normal": {
                    "type": "object",
                    "properties": {
                        "leader": {"type": ["integer", "string"]},
                        "quit": {"type": "array", "items": {"type": ["integer", "string"]}},
                        "down": {"type": "array", "items": {"type": ["integer", "string"]}},
                        "up": {"type": "array", "items": {"type": ["integer", "string"]}},
                        "left": {"type": "array", "items": {"type": ["integer", "string"]}},
                        "right": {"type": "array", "items": {"type": ["integer", "string"]}},
                        "search": {"type": ["integer", "string"]},
                        "enter": {"type": "array", "items": {"type": ["integer", "string"]}},
                        "escape": {"type": ["integer", "string"]},
                        "backspace": {"type": "array", "items": {"type": ["integer", "string"]}},
                    }
                },
                "search": {
                    "type": "object"
                },
                "cell": {
                    "type": "object"
                }
            }
        },
        "colors": {
            "type": "object",
            "properties": {
                "type": {"type": "object"},
                "status": {"type": "object"},
                "date": {"type": "object"},
            }
        },
        "triggers": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "object",
                    "properties": {
                        "on_enter": {"type": "string"},
                        "on_select": {"type": "string"},
                        "on_change": {"type": "string"},
                        "data": {"type": "string", "enum": ["row", "cell", "table"]},
                        "async_": {"type": "boolean"},
                    }
                },
                "rows": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "on_enter": {"type": "string"},
                            "on_select": {"type": "string"},
                            "on_change": {"type": "string"},
                            "data": {"type": "string", "enum": ["row", "cell", "table"]},
                            "async_": {"type": "boolean"},
                        }
                    }
                },
                "cells": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "on_enter": {"type": "string"},
                            "on_select": {"type": "string"},
                            "on_change": {"type": "string"},
                            "data": {"type": "string", "enum": ["row", "cell", "table"]},
                            "async_": {"type": "boolean"},
                        }
                    }
                },
            }
        },
        "enum": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "enum": ["inline", "inferred", "external"]},
                    "values": {"type": "array", "items": {"type": "string"}},
                    "command": {"type": "string"},
                }
            }
        },
        "drill_down": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "field": {"type": "string"},
                "field_name": {"type": "string"},
                "inherit_flags": {"type": "boolean"},
                "extra_flags": {"type": "array", "items": {"type": "string"}},
                "new_tab": {"type": "boolean"},
            }
        },
        "refresh": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "on_trigger": {"type": "boolean"},
                "interval": {"type": "number"},
                "command": {"type": "string"},
            }
        },
        "tabs": {
            "type": "array",
            "items": {"type": "string"}
        },
    }
}


def validate_config(config: Dict[str, Any]) -> Optional[str]:
    """
    Validate config against schema.
    
    Returns:
        Error message if invalid, None if valid
    """
    def validate_path(data: Any, schema: Any, path: str = "") -> Optional[str]:
        """Recursively validate data against schema."""
        if isinstance(schema, str):
            # String schema: "array", "object", "string", "number", "boolean", "integer"
            if schema == "array":
                if not isinstance(data, list):
                    return f"{path}: Expected array, got {type(data).__name__}"
            elif schema == "object":
                if not isinstance(data, dict):
                    return f"{path}: Expected object, got {type(data).__name__}"
            elif schema == "string":
                if not isinstance(data, str):
                    return f"{path}: Expected string, got {type(data).__name__}"
            elif schema == "number":
                if not isinstance(data, (int, float)):
                    return f"{path}: Expected number, got {type(data).__name__}"
            elif schema == "boolean":
                if not isinstance(data, bool):
                    return f"{path}: Expected boolean, got {type(data).__name__}"
            elif schema == "integer":
                if not isinstance(data, int):
                    return f"{path}: Expected integer, got {type(data).__name__}"
            return None
        elif isinstance(schema, list):
            # List schema: try each item schema
            for item_schema in schema:
                if validate_path(data, item_schema, path) is None:
                    return None
            return f"{path}: No valid type found"
        elif isinstance(schema, dict):
            # Object schema: check properties, items, additionalProperties, enum
            if "enum" in schema:
                if data not in schema["enum"]:
                    return f"{path}: Expected one of {schema['enum']}, got {data}"
            if "properties" in schema:
                if not isinstance(data, dict):
                    return f"{path}: Expected object with properties, got {type(data).__name__}"
                for key, value in data.items():
                    if key in schema["properties"]:
                        result = validate_path(value, schema["properties"][key], f"{path}.{key}")
                        if result:
                            return result
            if "items" in schema and isinstance(data, list):
                for i, item in enumerate(data):
                    result = validate_path(item, schema["items"], f"{path}[{i}]")
                    if result:
                        return result
            if "additionalProperties" in schema and isinstance(data, dict):
                for key, value in data.items():
                    result = validate_path(value, schema["additionalProperties"], f"{path}.{key}")
                    if result:
                        return result
            if "type" in schema:
                return validate_path(data, schema["type"], path)
        
        return None
    
    return validate_path(config, CONFIG_SCHEMA, "_config")


@dataclass
class KeybindConfig:
    """Keybind configuration for a specific mode."""
    j: str = "down"
    k: str = "up"
    h: str = "left"
    l: str = "right"
    enter: str = "select"
    q: str = "quit"
    slash: str = "search"
    escape: str = "exit_search"
    backspace: str = "delete_char"
    tab: str = "down"
    shift_tab: str = "up"
    leader: int = ord(';')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "leader": self.leader,
            "quit": [ord('q'), ord('Q')],
            "down": [ord('j'), ord('J'), 258],
            "up": [ord('k'), ord('K'), 259],
            "left": [ord('h'), ord('H'), 260],
            "right": [ord('l'), ord('L'), 261],
            "search": ord('/'),
            "enter": [ord('\n'), 10],
            "escape": 27,
            "backspace": [263, 127],
        }


@dataclass
class ModeKeybinds:
    """Keybinds for different modes."""
    normal: Dict[str, Any] = field(default_factory=lambda: KeybindConfig().to_dict())
    search: Dict[str, Any] = field(default_factory=lambda: ({
        "enter": [ord('\n'), 10],
        "escape": 27,
        "backspace": [263, 127],
        "tab": 9,
        "shift_tab": 353,
    }))
    cell: Optional[Dict[str, Any]] = None


@dataclass
class ColorsConfig:
    """Color configuration."""
    type: Dict[str, Any] = field(default_factory=lambda: {"work": (5, True), "study": (6, True)})
    status: Dict[str, Any] = field(default_factory=lambda: {
        "focus": (2, True),
        "active": (3, True),
    })
    date: Dict[str, Any] = field(default_factory=lambda: {"prefix": "2025-", "color": 4})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "status": self.status,
            "date": self.date,
        }


@dataclass
class ColumnWidthsConfig:
    """Column widths configuration."""
    type: int = 8
    status: int = 12
    summary: Optional[int] = None
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary, excluding None values."""
        result = {"type": self.type, "status": self.status}
        if self.summary is not None:
            result["summary"] = self.summary
        return result


@dataclass
class TriggerConfig:
    """Trigger configuration."""
    on_enter: Optional[str] = None
    on_select: Optional[str] = None
    on_change: Optional[str] = None
    data: Literal["row", "cell", "table"] = "row"
    async_: bool = True


@dataclass
class TriggersConfig:
    """Triggers configuration."""
    table: Optional[TriggerConfig] = None
    rows: Optional[Dict[str, TriggerConfig]] = None
    cells: Optional[Dict[str, TriggerConfig]] = None


@dataclass
class EnumSourceConfig:
    """Enum source configuration."""
    source: Literal["inline", "inferred", "external"] = "inferred"
    values: Optional[List[str]] = None
    command: Optional[str] = None


@dataclass
class EnumConfig:
    """Enum configuration per field."""
    status: EnumSourceConfig = field(default_factory=EnumSourceConfig)
    priority: Optional[EnumSourceConfig] = None
    type: Optional[EnumSourceConfig] = None


@dataclass
class DrillDownConfig:
    """Drill-down configuration."""
    enabled: bool = False
    field_name: Optional[str] = None
    inherit_flags: bool = True
    extra_flags: List[str] = field(default_factory=lambda: [])
    new_tab: bool = False


@dataclass
class RefreshConfig:
    """Refresh configuration."""
    enabled: bool = True
    on_trigger: bool = False
    interval: float = 1.0
    command: Optional[str] = None


@dataclass
class Config:
    """Main configuration dataclass."""
    
    columns: List[str] = field(default_factory=lambda: ["type", "status", "summary"])
    column_widths: Dict[str, int] = field(default_factory=lambda: ColumnWidthsConfig().to_dict())
    keybinds: Dict[str, Any] = field(default_factory=lambda: ModeKeybinds().normal)
    colors: Dict[str, Any] = field(default_factory=lambda: ColorsConfig().to_dict())
    triggers: Optional[TriggersConfig] = None
    enum: Optional[EnumConfig] = None
    drill_down: Optional[DrillDownConfig] = None
    refresh: Optional[RefreshConfig] = None
    tabs: Optional[List[str]] = None
    
    config_file: Optional[str] = None
    single_select: bool = False
    stdin_timeout: Optional[float] = None
    delimiter: str = ','
    tab_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "columns": self.columns,
            "column_widths": self.column_widths,
            "keybinds": self.keybinds,
            "colors": self.colors,
        }
        
        if self.triggers:
            result["triggers"] = {
                "table": None if self.triggers.table is None else {
                    "on_enter": self.triggers.table.on_enter,
                    "on_select": self.triggers.table.on_select,
                    "on_change": self.triggers.table.on_change,
                    "data": self.triggers.table.data,
                    "async": self.triggers.table.async_,
                },
                "rows": None if self.triggers.rows is None else {
                    k: {
                        "on_enter": v.on_enter,
                        "on_select": v.on_select,
                        "on_change": v.on_change,
                        "data": v.data,
                        "async": v.async_,
                    } for k, v in self.triggers.rows.items()
                },
                "cells": None if self.triggers.cells is None else {
                    k: {
                        "on_enter": v.on_enter,
                        "on_select": v.on_select,
                        "on_change": v.on_change,
                        "data": v.data,
                        "async": v.async_,
                    } for k, v in self.triggers.cells.items()
                },
            }
        
        if self.enum:
            result["enum"] = {
                k: {
                    "source": v.source,
                    "values": v.values,
                    "command": v.command,
                } if v else None
                for k, v in {
                    "status": self.enum.status,
                    "priority": self.enum.priority,
                    "type": self.enum.type,
                }.items() if v is not None
            }
        
        if self.drill_down:
            result["drill_down"] = {
                "enabled": self.drill_down.enabled,
                "field": self.drill_down.field_name,
                "inherit_flags": self.drill_down.inherit_flags,
                "extra_flags": self.drill_down.extra_flags,
                "new_tab": self.drill_down.new_tab,
            }
        
        if self.refresh:
            result["refresh"] = {
                "enabled": self.refresh.enabled,
                "on_trigger": self.refresh.on_trigger,
                "interval": self.refresh.interval,
                "command": self.refresh.command,
            }
        
        if self.tabs:
            result["tabs"] = self.tabs
        
        return result


DEFAULT_CONFIG = Config().to_dict()


def load_defaults() -> Config:
    """Load default configuration."""
    return Config()


def load_config_from_file(path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    if not os.path.exists(path):
        return {}
    
    try:
        with open(path, 'r') as f:
            user_config = json.load(f)
        
        if "_config" in user_config:
            user_config = user_config["_config"]
        
        validation_error = validate_config(user_config)
        if validation_error:
            raise Exception(f"Config validation error in {path}: {validation_error}")
        
        return user_config
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in config file {path}: {e}")
    except Exception as e:
        raise Exception(f"Failed to load config from {path}: {e}")


def load_config_from_inline_json(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Load configuration from inline JSON (_config field in data)."""
    if not data or len(data) == 0:
        return {}
    
    first_item = data[0]
    if "_config" in first_item:
        inline_config = first_item["_config"]
        validation_error = validate_config(inline_config)
        if validation_error:
            raise Exception(f"Inline config validation error: {validation_error}")
        return inline_config
    
    return {}


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two config dictionaries."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def load_config(
    config_path: Optional[str] = None,
    inline_config: Optional[Dict[str, Any]] = None,
    cli_config: Optional[Dict[str, Any]] = None,
) -> Config:
    """
    Load configuration from multiple sources with priority: CLI > inline JSON > file > defaults.
    
    Args:
        config_path: Path to external config file
        inline_config: Config from inline JSON (_config field)
        cli_config: Config from CLI flags
        
    Returns:
        Merged Config object
    """
    defaults = load_defaults().to_dict()
    
    config = defaults.copy()
    
    if config_path:
        file_config = load_config_from_file(config_path)
        config = merge_configs(config, file_config)
    
    if inline_config:
        config = merge_configs(config, inline_config)
    
    if cli_config:
        config = merge_configs(config, cli_config)
    
    result = Config()
    
    if "columns" in config:
        result.columns = config["columns"]
    
    if "column_widths" in config:
        result.column_widths = config["column_widths"]
    
    if "keybinds" in config:
        result.keybinds = config["keybinds"]
    
    if "colors" in config:
        result.colors = config["colors"]
    
    if "triggers" in config and config["triggers"]:
        triggers_data = config["triggers"]
        result.triggers = TriggersConfig()
        
        if "table" in triggers_data and triggers_data["table"]:
            td = triggers_data["table"]
            result.triggers.table = TriggerConfig(
                on_enter=td.get("on_enter"),
                on_select=td.get("on_select"),
                on_change=td.get("on_change"),
                data=td.get("data", "row"),
                async_=td.get("async", True),
            )
        
        if "rows" in triggers_data and triggers_data["rows"]:
            result.triggers.rows = {}
            for key, rd in triggers_data["rows"].items():
                result.triggers.rows[key] = TriggerConfig(
                    on_enter=rd.get("on_enter"),
                    on_select=rd.get("on_select"),
                    on_change=rd.get("on_change"),
                    data=rd.get("data", "row"),
                    async_=rd.get("async", True),
                )
        
        if "cells" in triggers_data and triggers_data["cells"]:
            result.triggers.cells = {}
            for key, cd in triggers_data["cells"].items():
                result.triggers.cells[key] = TriggerConfig(
                    on_enter=cd.get("on_enter"),
                    on_select=cd.get("on_select"),
                    on_change=cd.get("on_change"),
                    data=cd.get("data", "cell"),
                    async_=cd.get("async", True),
                )
    
    if "enum" in config and config["enum"]:
        enum_data = config["enum"]
        result.enum = EnumConfig()
        
        if "status" in enum_data:
            sd = enum_data["status"]
            result.enum.status = EnumSourceConfig(
                source=sd.get("source", "inferred"),
                values=sd.get("values"),
                command=sd.get("command"),
            )
        
        if "priority" in enum_data:
            pd = enum_data["priority"]
            result.enum.priority = EnumSourceConfig(
                source=pd.get("source", "inferred"),
                values=pd.get("values"),
                command=pd.get("command"),
            )
        
        if "type" in enum_data:
            td = enum_data["type"]
            result.enum.type = EnumSourceConfig(
                source=td.get("source", "inferred"),
                values=td.get("values"),
                command=td.get("command"),
            )
    
    if "drill_down" in config and config["drill_down"]:
        dd = config["drill_down"]
        result.drill_down = DrillDownConfig(
            enabled=dd.get("enabled", False),
            field_name=dd.get("field_name") or dd.get("field"),
            inherit_flags=dd.get("inherit_flags", True),
            extra_flags=dd.get("extra_flags", []),
            new_tab=dd.get("new_tab", False),
        )
    
    if "refresh" in config and config["refresh"]:
        rd = config["refresh"]
        result.refresh = RefreshConfig(
            enabled=rd.get("enabled", True),
            on_trigger=rd.get("on_trigger", False),
            interval=rd.get("interval", 1.0),
            command=rd.get("command"),
        )
    
    if "tabs" in config:
        result.tabs = config["tabs"]
    
    if "delimiter" in config:
        result.delimiter = config["delimiter"]
    
    if "tab_name" in config:
        result.tab_name = config["tab_name"]
    
    if config_path:
        result.config_file = config_path
    
    return result


def get_column_widths(config: Config, terminal_width: int) -> List[int]:
    """
    Calculate column widths based on config and terminal size.
    The last column gets remaining space.
    """
    columns = config.columns
    column_widths = config.column_widths
    
    widths = []
    remaining_width = terminal_width - (len(columns) - 1) - 2
    
    for i, col in enumerate(columns[:-1]):
        width = column_widths.get(col, 10)
        widths.append(width)
        remaining_width -= width
    
    widths.append(max(1, remaining_width))
    return widths
