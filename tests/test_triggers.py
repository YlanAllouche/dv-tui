import pytest
from unittest.mock import Mock, patch, MagicMock
from dv_tui.triggers import (
    TriggerExecutor,
    TriggerManager,
    execute_trigger,
    format_string,
    execute_trigger_chain,
    get_triggers_for_item,
    matches_condition
)


def test_trigger_executor_register_python_function():
    executor = TriggerExecutor()
    
    def dummy_func(context):
        return "result"
    
    executor.register_python_function("dummy", dummy_func)
    assert "dummy" in executor.python_functions


def test_trigger_executor_execute_shell_command_async():
    executor = TriggerExecutor()
    
    with patch('subprocess.Popen') as mock_popen:
        trigger = {"command": "echo test", "async_": True}
        context = {"selected_cell": "value"}
        
        result = executor._execute_shell_command(trigger, context, async_exec=True)
        
        assert result is None
        mock_popen.assert_called_once()


def test_trigger_executor_execute_shell_command_sync():
    executor = TriggerExecutor()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="output")
        
        trigger = {"command": "echo test", "async_": False}
        context = {"selected_cell": "value"}
        
        result = executor._execute_shell_command(trigger, context, async_exec=False)
        
        assert result == "output"
        mock_run.assert_called_once()


def test_trigger_executor_execute_shell_command_with_cwd():
    executor = TriggerExecutor()
    
    with patch('subprocess.Popen') as mock_popen:
        trigger = {
            "command": "echo test",
            "cwd": "/tmp"
        }
        context = {}
        
        executor._execute_shell_command(trigger, context, async_exec=True)
        
        call_kwargs = mock_popen.call_args[1]
        assert call_kwargs["cwd"] == "/tmp"


def test_trigger_executor_execute_shell_command_with_env():
    executor = TriggerExecutor()
    
    with patch('subprocess.Popen') as mock_popen:
        with patch.dict('os.environ', {'EXISTING': 'value'}, clear=False):
            trigger = {
                "command": "echo test",
                "env": {"CUSTOM_VAR": "custom_value"}
            }
            context = {"selected_cell": "cell_value"}
            
            executor._execute_shell_command(trigger, context, async_exec=True)
            
            call_kwargs = mock_popen.call_args[1]
            env = call_kwargs["env"]
            assert env["DV_SELECTED_CELL"] == "cell_value"
            assert env["CUSTOM_VAR"] == "custom_value"


def test_trigger_executor_execute_shell_command_with_input():
    executor = TriggerExecutor()
    
    with patch('subprocess.Popen') as mock_popen:
        trigger = {
            "command": "cat",
            "input": "stdin data"
        }
        context = {}
        
        executor._execute_shell_command(trigger, context, async_exec=True)
        
        call_kwargs = mock_popen.call_args[1]
        assert call_kwargs["stdin"] is not None


def test_trigger_executor_execute_python_function():
    executor = TriggerExecutor()
    
    def my_func(context):
        return f"processed {context.get('selected_cell')}"
    
    executor.register_python_function("my_func", my_func)
    
    trigger = {"function": "my_func"}
    context = {"selected_cell": "value"}
    
    result = executor._execute_python_function(trigger, context)
    assert result == "processed value"


def test_trigger_executor_execute_python_function_not_registered():
    executor = TriggerExecutor()
    
    trigger = {"function": "nonexistent"}
    context = {}
    
    result = executor._execute_python_function(trigger, context)
    assert result is None


def test_trigger_executor_format_string_simple():
    executor = TriggerExecutor()
    
    template = "Selected: {selected_cell}"
    data = {"selected_cell": "value"}
    
    result = executor._format_string(template, data)
    assert result == "Selected: value"


def test_trigger_executor_format_string_nested():
    executor = TriggerExecutor()
    
    template = "Name: {selected_row.name}"
    data = {"selected_row": {"name": "Alice"}}
    
    result = executor._format_string(template, data)
    assert result == "Name: Alice"


def test_trigger_executor_format_string_missing_key():
    executor = TriggerExecutor()
    
    template = "Missing: {nonexistent}"
    data = {"selected_cell": "value"}
    
    result = executor._format_string(template, data)
    assert result == "Missing: {nonexistent}"


def test_trigger_executor_build_environment():
    executor = TriggerExecutor()
    
    with patch.dict('os.environ', {'EXISTING': 'value'}, clear=False):
        context = {
            "selected_cell": "cell",
            "selected_row": {"name": "Alice"},
            "selected_index": 5,
            "selected_column": "name",
            "DV_CUSTOM": "custom"
        }
        additional_env = {"EXTRA": "extra_value"}
        
        env = executor._build_environment(context, additional_env)
        
        assert env["DV_SELECTED_CELL"] == "cell"
        assert "name" in env["DV_SELECTED_ROW"]
        assert env["DV_SELECTED_INDEX"] == "5"
        assert env["DV_SELECTED_COLUMN"] == "name"
        assert env["DV_CUSTOM"] == "custom"
        assert env["EXTRA"] == "extra_value"


def test_trigger_manager_set_table_triggers():
    manager = TriggerManager()
    
    triggers = {"on_select": "echo selected"}
    manager.set_table_triggers(triggers)
    
    assert manager.table_triggers == triggers


def test_trigger_manager_set_row_triggers():
    manager = TriggerManager()
    
    triggers = {"on_enter": "echo enter"}
    manager.set_row_triggers(0, triggers)
    
    assert manager.row_triggers[0] == triggers


def test_trigger_manager_set_cell_triggers():
    manager = TriggerManager()
    
    triggers = {"on_enter": "echo enter cell"}
    manager.set_cell_triggers(0, "name", triggers)
    
    assert manager.cell_triggers[(0, "name")] == triggers


def test_trigger_manager_get_trigger_table_only():
    manager = TriggerManager()
    manager.set_table_triggers({"on_select": "table_select"})
    
    context = {"selected_index": 0, "selected_column": "name"}
    trigger = manager.get_trigger("on_select", context)
    
    assert trigger == "table_select"


def test_trigger_manager_get_trigger_row_override():
    manager = TriggerManager()
    manager.set_table_triggers({"on_select": "table_select"})
    manager.set_row_triggers(0, {"on_select": "row_select"})
    
    context = {"selected_index": 0, "selected_column": "name"}
    trigger = manager.get_trigger("on_select", context)
    
    assert trigger == "row_select"


def test_trigger_manager_get_trigger_cell_override():
    manager = TriggerManager()
    manager.set_table_triggers({"on_select": "table_select"})
    manager.set_row_triggers(0, {"on_select": "row_select"})
    manager.set_cell_triggers(0, "name", {"on_select": "cell_select"})
    
    context = {"selected_index": 0, "selected_column": "name"}
    trigger = manager.get_trigger("on_select", context)
    
    assert trigger == "cell_select"


def test_trigger_manager_execute_trigger_event():
    manager = TriggerManager()
    
    with patch.object(manager.executor, 'execute_trigger') as mock_execute:
        mock_execute.return_value = "output"
        
        manager.set_table_triggers({"on_select": {"command": "echo test"}})
        context = {"selected_index": 0, "selected_column": "name"}
        
        result = manager.execute_trigger_event("on_select", context, async_exec=False)
        
        assert result == "output"
        mock_execute.assert_called_once()


def test_trigger_manager_register_python_function():
    manager = TriggerManager()
    
    def dummy_func(context):
        return "result"
    
    manager.register_python_function("dummy", dummy_func)
    assert "dummy" in manager.executor.python_functions


def test_execute_trigger_legacy():
    with patch('dv_tui.triggers.subprocess.Popen') as mock_popen:
        trigger = {"command": "echo test"}
        item = {"selected_cell": "value"}
        
        result = execute_trigger(trigger, item, async_exec=True)
        
        assert result is None
        mock_popen.assert_called_once()


def test_format_string_legacy():
    template = "Value: {selected_cell}"
    data = {"selected_cell": "test"}
    
    result = format_string(template, data)
    assert result == "Value: test"


def test_execute_trigger_chain():
    with patch('dv_tui.triggers.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="output1\noutput2")
        
        triggers = [
            {"command": "echo test1", "async": False},
            {"command": "echo test2", "async": False}
        ]
        item = {"selected_cell": "value"}
        
        results = execute_trigger_chain(triggers, item, stop_on_error=False)
        
        assert len(results) == 2


def test_get_triggers_for_item_field_equality():
    trigger_map = {
        "type=work": [{"command": "work command"}],
        "type=study": [{"command": "study command"}]
    }
    
    item = {"type": "work", "summary": "Task 1"}
    triggers = get_triggers_for_item(item, trigger_map)
    
    assert len(triggers) == 1
    assert triggers[0]["command"] == "work command"


def test_get_triggers_for_item_field_pattern():
    trigger_map = {
        "summary=*test*": [{"command": "test command"}]
    }
    
    item = {"summary": "This is a test task"}
    triggers = get_triggers_for_item(item, trigger_map)
    
    assert len(triggers) == 1


def test_matches_condition_field_equality():
    item = {"type": "work"}
    
    assert matches_condition(item, "type=work") is True
    assert matches_condition(item, "type=study") is False


def test_matches_condition_field_pattern():
    item = {"summary": "This is a test"}
    
    assert matches_condition(item, "summary=*test*") is True
    assert matches_condition(item, "summary=*nomatch*") is False


def test_matches_condition_missing_field():
    item = {"type": "work"}
    
    assert matches_condition(item, "summary=test") is False


def test_matches_condition_invalid_format():
    item = {"type": "work"}
    
    assert matches_condition(item, "invalid") is False
