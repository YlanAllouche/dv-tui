import pytest
import os
import json
import tempfile
from pathlib import Path
from dv_tui.config import (
    load_config,
    load_config_from_file,
    load_config_from_inline_json,
    filter_config_items,
    load_defaults,
    Config,
    TriggersConfig,
    TriggerConfig,
    validate_config,
)


def test_load_defaults():
    config = load_defaults()
    assert isinstance(config, Config)
    assert config.columns is None
    assert config.keybinds is not None
    assert config.colors is not None


def test_load_config_from_file_valid():
    config_data = {
        "columns": ["name", "age"],
        "keybinds": {"normal": {"leader": ord(',')}},
        "colors": {"type": {"work": (5, True)}}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    try:
        result = load_config_from_file(temp_path)
        assert result["columns"] == ["name", "age"]
        assert result["keybinds"]["normal"]["leader"] == ord(',')
    finally:
        os.unlink(temp_path)


def test_load_config_from_file_not_found():
    result = load_config_from_file("/nonexistent/path.json")
    assert result == {}


def test_load_config_from_file_with_config_wrapper():
    config_data = {
        "_config": {
            "columns": ["name", "age"],
            "keybinds": {"normal": {"leader": ord(',')}}
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    try:
        result = load_config_from_file(temp_path)
        assert result["columns"] == ["name", "age"]
    finally:
        os.unlink(temp_path)


def test_load_config_from_file_invalid_json():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_path = f.name
    
    try:
        with pytest.raises(Exception) as exc_info:
            load_config_from_file(temp_path)
        assert "Invalid JSON" in str(exc_info.value)
    finally:
        os.unlink(temp_path)


def test_load_config_from_inline_json():
    data = [
        {"_config": {"columns": ["name", "age"]}},
        {"name": "Alice", "age": 30}
    ]
    result = load_config_from_inline_json(data)
    assert result["columns"] == ["name", "age"]


def test_load_config_from_inline_json_empty():
    result = load_config_from_inline_json([])
    assert result == {}


def test_load_config_from_inline_json_no_config():
    data = [
        {"name": "Alice", "age": 30}
    ]
    result = load_config_from_inline_json(data)
    assert result == {}


def test_filter_config_items():
    data = [
        {"_config": {"columns": ["name", "age"]}},
        {"name": "Alice", "age": 30},
        {"_config": {"colors": {}}, "name": "Bob"}
    ]
    result = filter_config_items(data)
    assert len(result) == 2
    assert result[0] == {"name": "Alice", "age": 30}
    assert result[1] == {"name": "Bob"}


def test_validate_config_valid():
    config = {
        "columns": ["name", "age"],
        "keybinds": {
            "normal": {
                "leader": ord(','),
                "quit": [ord('q')]
            }
        }
    }
    error = validate_config(config)
    assert error is None


def test_validate_config_invalid():
    config = {
        "columns": "not a list",
    }
    error = validate_config(config)
    assert error is not None
    assert "Expected array" in error


def test_load_config_with_all_sources():
    defaults = {"columns": ["type", "status", "summary"]}
    inline_config = {"columns": ["name", "age"]}
    cli_config = {"columns": ["priority"]}
    
    config = load_config(cli_config=cli_config, inline_config=inline_config)
    assert config.columns == ["priority"]


def test_load_config_precedence():
    defaults = load_defaults().to_dict()
    inline_config = {"columns": ["inline", "columns"]}
    cli_config = {"columns": ["cli", "columns"]}
    
    config = load_config(cli_config=cli_config, inline_config=inline_config)
    assert config.columns == ["cli", "columns"]


def test_load_config_triggers():
    inline_config = {
        "triggers": {
            "table": {
                "on_select": "echo selected",
                "data": "row"
            },
            "rows": {
                "0": {
                    "on_enter": "echo enter row 0"
                }
            },
            "cells": {
                "name": {
                    "on_enter": "echo enter name cell"
                }
            }
        }
    }
    
    config = load_config(inline_config=inline_config)
    assert config.triggers is not None
    assert config.triggers.table is not None
    assert config.triggers.table.on_select == "echo selected"
    assert config.triggers.rows is not None
    assert "0" in config.triggers.rows
    assert config.triggers.rows["0"].on_enter == "echo enter row 0"
    assert config.triggers.cells is not None
    assert "name" in config.triggers.cells


def test_load_config_enum():
    inline_config = {
        "enum": {
            "status": {
                "source": "inline",
                "values": ["todo", "done"]
            },
            "priority": {
                "source": "external",
                "command": "echo 'high medium low'"
            }
        }
    }
    
    config = load_config(inline_config=inline_config)
    assert config.enum is not None
    assert config.enum.status.source == "inline"
    assert config.enum.status.values == ["todo", "done"]
    assert config.enum.priority.source == "external"
    assert config.enum.priority.command == "echo 'high medium low'"


def test_load_config_drill_down():
    inline_config = {
        "drill_down": {
            "enabled": True,
            "field_name": "tags",
            "inherit_flags": False,
            "extra_flags": ["--verbose"],
            "new_tab": True
        }
    }
    
    config = load_config(inline_config=inline_config)
    assert config.drill_down is not None
    assert config.drill_down.enabled is True
    assert config.drill_down.field_name == "tags"
    assert config.drill_down.inherit_flags is False
    assert config.drill_down.extra_flags == ["--verbose"]
    assert config.drill_down.new_tab is True


def test_load_config_refresh():
    inline_config = {
        "refresh": {
            "enabled": True,
            "on_trigger": True,
            "interval": 5.0,
            "command": "ls -la"
        }
    }
    
    config = load_config(inline_config=inline_config)
    assert config.refresh.enabled is True
    assert config.refresh.on_trigger is True
    assert config.refresh.interval == 5.0
    assert config.refresh.command == "ls -la"


def test_load_config_tabs():
    inline_config = {
        "tabs": ["file1.json", "file2.json", "file3.json"]
    }
    
    config = load_config(inline_config=inline_config)
    assert config.tabs == ["file1.json", "file2.json", "file3.json"]


def test_config_to_dict():
    config = Config(
        columns=["name", "age"],
        tab_name="Test Tab"
    )
    
    result = config.to_dict()
    assert result["columns"] == ["name", "age"]
    assert result.get("tab_name") is None


def test_trigger_config_dataclass():
    trigger = TriggerConfig(
        on_select="echo selected",
        on_enter={"command": "echo enter", "async_": False},
        data="cell"
    )
    
    assert trigger.on_select == "echo selected"
    assert trigger.on_enter == {"command": "echo enter", "async_": False}
    assert trigger.data == "cell"
    assert trigger.async_ is True


def test_color_config():
    from dv_tui.config import ColorsConfig, ColumnWidthsConfig
    
    colors = ColorsConfig()
    # Colors are now empty by default (no hardcoded mappings)
    assert colors.type == {}
    assert colors.status == {}
    
    # Can still set custom colors
    custom_colors = ColorsConfig(type={"work": (5, True)})
    assert custom_colors.type["work"] == (5, True)
    
    widths = ColumnWidthsConfig(type=15, status=20)
    result = widths.to_dict()
    assert result["type"] == 15
    assert result["status"] == 20
