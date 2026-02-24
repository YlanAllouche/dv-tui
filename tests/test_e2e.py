import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

from dv_tui.config import Config, load_config, load_defaults, DrillDownConfig
from dv_tui.data_loaders import JsonDataLoader, CsvDataLoader, create_loader
from dv_tui.table import Table
from dv_tui.handlers import KeyHandler


@pytest.fixture
def sample_json_data():
    return [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"},
        {"name": "Charlie", "age": 35, "city": "SF"}
    ]


@pytest.fixture
def sample_config():
    return Config(
        columns=["name", "age", "city"],
        column_widths={"name": 15, "age": 10, "city": 15}
    )


def test_e2e_basic_table_display(sample_json_data, sample_config):
    """Test basic table display with mocked curses."""
    with patch('curses.wrapper') as mock_wrapper:
        mock_window = Mock()
        mock_window.getmaxyx.return_value = (24, 80)
        mock_window.addstr = Mock()
        mock_window.refresh = Mock()
        
        table = Table(sample_json_data, sample_config.columns, sample_config.column_widths)
        
        assert table.data == sample_json_data
        assert table.columns == sample_config.columns
        assert len(table.data) == 3


def test_e2e_multi_tab_navigation():
    """Test multi-tab navigation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.json"
        file2 = Path(tmpdir) / "file2.json"
        file3 = Path(tmpdir) / "file3.json"
        
        json.dump([{"name": "Alice"}, {"name": "Bob"}], file1.open('w'))
        json.dump([{"task": "Task1"}, {"task": "Task2"}], file2.open('w'))
        json.dump([{"id": 1}, {"id": 2}], file3.open('w'))
        
        loader1 = JsonDataLoader(str(file1))
        loader2 = JsonDataLoader(str(file2))
        loader3 = JsonDataLoader(str(file3))
        
        data1 = loader1.load()
        data2 = loader2.load()
        data3 = loader3.load()
        
        assert data1[0]["name"] == "Alice"
        assert data2[0]["task"] == "Task1"
        assert data3[0]["id"] == 1


def test_e2e_search_and_filter():
    """Test search and filter functionality."""
    data = [
        {"name": "Alice", "summary": "Fix bug"},
        {"name": "Bob", "summary": "Add feature"},
        {"name": "Charlie", "summary": "Fix another bug"}
    ]
    
    config = Config(columns=["name", "summary"])
    table = Table(data, config.columns, config.column_widths)
    
    handler = KeyHandler(table)
    
    handler.enter_search_mode(table)
    handler.search_query = "bug"
    handler.filtered_indices = [0, 2]
    
    assert len(handler.filtered_indices) == 2
    assert handler.filtered_indices[0] == 0
    assert handler.filtered_indices[1] == 2


def test_e2e_cell_row_selection_modes():
    """Test cell and row selection modes."""
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    
    config = Config(columns=["name", "age"])
    table = Table(data, config.columns, config.column_widths)
    
    assert table.selection_mode == 'row'
    
    table.selection_mode = 'cell'
    assert table.selection_mode == 'cell'
    
    table.selection_mode = 'row'
    assert table.selection_mode == 'row'


def test_e2e_drill_down_nested_arrays():
    """Test drill-down into nested arrays."""
    data = [
        {
            "name": "Project1",
            "tags": ["bug", "feature"],
            "tasks": [
                {"title": "Task1", "status": "done"},
                {"title": "Task2", "status": "todo"}
            ]
        }
    ]
    
    drill_config = Config(
        columns=["name", "tags", "tasks"],
        drill_down=DrillDownConfig(
            enabled=True,
            field_name="tasks",
            inherit_flags=True
        )
    )
    
    assert drill_config.drill_down is not None
    assert drill_config.drill_down.enabled is True
    assert drill_config.drill_down.field_name == "tasks"
    
    drill_data = data[0]["tasks"]
    assert len(drill_data) == 2
    assert drill_data[0]["title"] == "Task1"


def test_e2e_trigger_execution():
    """Test trigger execution with mocked subprocess."""
    from dv_tui.triggers import TriggerExecutor
    
    with patch('subprocess.Popen') as mock_popen:
        executor = TriggerExecutor()
        
        trigger = {
            "command": "echo {selected_cell}",
            "async_": True
        }
        context = {"selected_cell": "value123"}
        
        result = executor.execute_trigger(trigger, context, async_exec=True)
        
        assert result is None
        mock_popen.assert_called_once()


def test_e2e_csv_parsing():
    """Test CSV file parsing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,age,city\n")
        f.write("Alice,30,NYC\n")
        f.write("Bob,25,LA\n")
        temp_path = f.name
    
    try:
        loader = CsvDataLoader(temp_path)
        data = loader.load()
        
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == "30"
        assert data[1]["city"] == "LA"
    finally:
        Path(temp_path).unlink()


def test_e2e_config_merging():
    """Test configuration merging with precedence."""
    inline_config = {
        "columns": ["inline_col1", "inline_col2"],
        "keybinds": {"normal": {"leader": ord(',')}}
    }
    
    cli_config = {
        "columns": ["cli_col1", "cli_col2"]
    }
    
    config = load_config(inline_config=inline_config, cli_config=cli_config)
    
    assert config.columns == ["cli_col1", "cli_col2"]


def test_e2e_large_table_performance():
    """Test handling large tables (100 rows)."""
    data = [{"id": i, "name": f"Item{i}", "value": i * 10} for i in range(100)]
    
    config = Config(columns=["id", "name", "value"])
    table = Table(data, config.columns, config.column_widths)
    
    assert len(table.data) == 100
    assert table.data[50]["id"] == 50
    assert table.data[99]["value"] == 990


def test_e2e_json_with_config():
    """Test JSON file with inline config."""
    data = [
        {
            "_config": {
                "columns": ["name", "status"]
            }
        },
        {"name": "Task1", "status": "done"},
        {"name": "Task2", "status": "todo"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name
    
    try:
        loader = JsonDataLoader(temp_path)
        loaded_data = loader.load()
        
        assert len(loaded_data) == 2
        assert loaded_data[0]["name"] == "Task1"
        assert "_config" not in loaded_data[0]
    finally:
        Path(temp_path).unlink()


def test_e2e_csv_with_different_delimiters():
    """Test CSV parsing with different delimiters."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name;age;city\n")
        f.write("Alice;30;NYC\n")
        f.write("Bob;25;LA\n")
        temp_path = f.name
    
    try:
        loader = CsvDataLoader(temp_path, delimiter=';')
        data = loader.load()
        
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[1]["city"] == "LA"
    finally:
        Path(temp_path).unlink()


def test_e2e_stdin_data_loading():
    """Test loading data from stdin with command."""
    from dv_tui.data_loaders import StdinDataLoader
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps([{"test": "data"}]))
        
        loader = StdinDataLoader(command="echo 'test'")
        data = loader.load()
        
        assert len(data) == 1
        assert data[0]["test"] == "data"


def test_e2e_table_navigation():
    """Test table navigation (up/down)."""
    data = [
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"}
    ]
    
    config = Config(columns=["name"])
    table = Table(data, config.columns, config.column_widths)
    
    assert table.selected_index == 0
    
    table.scroll_down()
    assert table.selected_index == 1
    
    table.scroll_up()
    assert table.selected_index == 0
    
    table.scroll_down()
    table.scroll_down()
    assert table.selected_index == 2
    
    table.scroll_down()
    assert table.selected_index == 2


def test_e2e_color_configuration():
    """Test color configuration application."""
    config = Config(
        columns=["name", "type"],
        colors={
            "type": {"work": (5, True), "study": (6, True)},
            "status": {"focus": (2, True)}
        }
    )
    
    assert config.colors is not None
    assert config.colors["type"]["work"] == (5, True)
    assert config.colors["status"]["focus"] == (2, True)


def test_e2e_keybind_configuration():
    """Test keybind configuration."""
    config = Config(
        keybinds={
            "normal": {
                "leader": ord(','),
                "quit": [ord('q'), ord('Q')],
                "down": [ord('j'), 258]
            }
        }
    )
    
    assert config.keybinds is not None
    assert config.keybinds["normal"]["leader"] == ord(',')
    assert ord('q') in config.keybinds["normal"]["quit"]


def test_e2e_refresh_functionality():
    """Test data refresh functionality."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([{"version": 1}], f)
        temp_path = f.name
    
    try:
        loader = JsonDataLoader(temp_path)
        data1 = loader.load()
        assert data1[0]["version"] == 1
        
        json.dump([{"version": 2}], Path(temp_path).open('w'))
        
        data2 = loader.refresh()
        assert data2[0]["version"] == 2
    finally:
        Path(temp_path).unlink()
