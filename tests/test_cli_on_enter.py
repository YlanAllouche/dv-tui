import json
import tempfile
from pathlib import Path


from dv_tui.cli import parse_args, get_cli_config
from dv_tui.config import load_config
from dv_tui.core import TUI


def test_cli_on_enter_string_sets_table_trigger():
    args = parse_args(["--on-enter", "echo hi", "file.json"])
    cli_config = get_cli_config(args)
    assert cli_config["triggers"]["table"]["on_enter"] == "echo hi"


def test_cli_on_enter_json_sets_table_trigger_object():
    trigger_obj = {"command": "echo hi", "async_": False, "env": {"X": "1"}}
    args = parse_args(["--on-enter-json", json.dumps(trigger_obj), "file.json"])
    cli_config = get_cli_config(args)
    assert cli_config["triggers"]["table"]["on_enter"] == trigger_obj


def test_cli_on_enter_overrides_inline_config_per_tab():
    data = [
        {"_config": {"triggers": {"table": {"on_enter": "inline"}}}},
        {"name": "a"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        temp_path = f.name

    try:
        args = parse_args(["--on-enter", "cli", temp_path])
        cli_config = get_cli_config(args)
        config = load_config(cli_config=cli_config)

        tui = TUI([temp_path], config=config, cli_config=cli_config)
        tui.load_data()

        assert tui.current_tab is not None
        assert tui.current_tab.config is not None
        assert tui.current_tab.config.triggers is not None
        assert tui.current_tab.config.triggers.table is not None
        assert tui.current_tab.config.triggers.table.on_enter == "cli"
    finally:
        Path(temp_path).unlink()
