import subprocess
import os
from typing import Dict, Any, List, Optional, Callable, Union
import shlex
import json


class TriggerExecutor:
    """Execute triggers with environment variables and error handling."""
    
    def __init__(self):
        """Initialize the trigger executor."""
        self.python_functions: Dict[str, Callable] = {}
    
    def register_python_function(self, name: str, func: Callable) -> None:
        """Register a Python function as a trigger."""
        self.python_functions[name] = func
    
    def execute_trigger(
        self,
        trigger: Dict[str, Any],
        context: Dict[str, Any],
        async_exec: bool = True
    ) -> Optional[str]:
        """
        Execute a trigger with the given context.
        
        Trigger format:
        {
            "command": "string command or list of args",  # for shell commands
            "function": "function_name",  # for Python functions (library usage)
            "env": {"VAR": "value"},  # optional additional env vars
            "input": "stdin input",  # optional
            "cwd": "/working/directory",  # optional
            "async_": True,  # optional, default True
        }
        
        Context should include:
        {
            "selected_cell": value,
            "selected_row": dict,
            "selected_index": int,
            "selected_column": str,
        }
        
        Returns stdout if not async_exec and shell command, None otherwise.
        """
        if not trigger:
            return None
        
        if "function" in trigger and trigger["function"]:
            return self._execute_python_function(trigger, context)
        
        return self._execute_shell_command(trigger, context, async_exec)
    
    def _execute_shell_command(
        self,
        trigger: Dict[str, Any],
        context: Dict[str, Any],
        async_exec: bool
    ) -> Optional[str]:
        """Execute a shell command trigger."""
        cmd_template = trigger.get("command", "")
        additional_env = trigger.get("env", {})
        input_data = trigger.get("input")
        cwd = trigger.get("cwd")
        
        if not cmd_template:
            return None
        
        # Format template variables first (like {selected_cell})
        cmd_str = self._format_string(cmd_template, context)
        if not cmd_str:
            return None
        
        env = self._build_environment(context, additional_env)
        async_exec = trigger.get("async_", async_exec)
        
        # Use shell=True to allow shell variable expansion ($DV_SELECTED_CELL)
        use_shell = True
        
        try:
            if async_exec:
                subprocess.Popen(
                    cmd_str,
                    stdin=subprocess.PIPE if input_data else None,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                    close_fds=True,
                    shell=use_shell
                )
                return None
            else:
                result = subprocess.run(
                    cmd_str,
                    input=input_data.encode() if input_data else None,
                    cwd=cwd,
                    env=env,
                    capture_output=True,
                    text=True,
                    shell=use_shell
                )
                return result.stdout
        except Exception as e:
            print(f"Error executing trigger: {e}")
            return None
    
    def _execute_python_function(
        self,
        trigger: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Execute a Python function trigger."""
        function_name = trigger.get("function", "")
        if not function_name or function_name not in self.python_functions:
            print(f"Python function '{function_name}' not registered")
            return None
        
        try:
            func = self.python_functions[function_name]
            result = func(context)
            return str(result) if result is not None else None
        except Exception as e:
            print(f"Error executing Python function trigger: {e}")
            return None
    
    def _parse_command(self, cmd_template: Union[str, List[str]], context: Dict[str, Any]) -> Optional[List[str]]:
        """Parse and format a command template with context."""
        if isinstance(cmd_template, list):
            return cmd_template
        
        cmd_str = self._format_string(cmd_template, context)
        if not cmd_str:
            return None
        
        try:
            return shlex.split(cmd_str)
        except ValueError as e:
            print(f"Error parsing command: {e}")
            return None
    
    def _format_string(self, template: str, data: Dict[str, Any]) -> str:
        """Format a string template with data from context."""
        result = template
        
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                result = result.replace(f"{{{key}}}", str(value))
            elif isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, (str, int, float, bool)):
                        result = result.replace(f"{{{key}.{nested_key}}}", str(nested_value))
        
        return result
    
    def _build_environment(self, context: Dict[str, Any], additional_env: Dict[str, str]) -> Dict[str, str]:
        """Build environment variables from context and additional env."""
        process_env = os.environ.copy()
        
        selected_cell = context.get("selected_cell")
        if selected_cell is not None:
            process_env["DV_SELECTED_CELL"] = str(selected_cell)
        
        selected_row = context.get("selected_row")
        if selected_row is not None:
            process_env["DV_SELECTED_ROW"] = json.dumps(selected_row)
        
        selected_index = context.get("selected_index")
        if selected_index is not None:
            process_env["DV_SELECTED_INDEX"] = str(selected_index)
        
        selected_column = context.get("selected_column")
        if selected_column is not None:
            process_env["DV_SELECTED_COLUMN"] = str(selected_column)
        
        process_env.update(additional_env)
        return process_env


class TriggerManager:
    """Manage triggers with priority handling (cell > row > table)."""
    
    def __init__(self):
        """Initialize the trigger manager."""
        self.executor = TriggerExecutor()
        self.table_triggers: Dict[str, Dict[str, Any]] = {}
        self.row_triggers: Dict[int, Dict[str, Any]] = {}
        self.cell_triggers: Dict[tuple, Dict[str, Any]] = {}
    
    def set_table_triggers(self, triggers: Dict[str, Any]) -> None:
        """Set table-level triggers."""
        self.table_triggers = triggers
    
    def set_row_triggers(self, row_index: int, triggers: Dict[str, Any]) -> None:
        """Set row-level triggers for a specific row."""
        self.row_triggers[row_index] = triggers
    
    def set_cell_triggers(self, row_index: int, column: str, triggers: Dict[str, Any]) -> None:
        """Set cell-level triggers for a specific cell."""
        self.cell_triggers[(row_index, column)] = triggers
    
    def get_trigger(self, event: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get the trigger to execute for an event with priority (cell > row > table).
        
        Events: on_enter, on_select, on_change
        """
        row_index = context.get("selected_index")
        column = context.get("selected_column")
        
        if row_index is not None and column is not None:
            cell_key = (row_index, column)
            if cell_key in self.cell_triggers:
                cell_triggers = self.cell_triggers[cell_key]
                if event in cell_triggers:
                    return cell_triggers[event]
        
        if row_index is not None and row_index in self.row_triggers:
            row_triggers = self.row_triggers[row_index]
            if event in row_triggers:
                return row_triggers[event]
        
        if event in self.table_triggers:
            return self.table_triggers[event]
        
        return None
    
    def execute_trigger_event(self, event: str, context: Dict[str, Any], async_exec: bool = True) -> Optional[str]:
        """Execute a trigger event with priority handling."""
        trigger = self.get_trigger(event, context)
        if trigger:
            return self.executor.execute_trigger(trigger, context, async_exec)
        return None
    
    def register_python_function(self, name: str, func: Callable) -> None:
        """Register a Python function as a trigger."""
        self.executor.register_python_function(name, func)


def execute_trigger(trigger: Dict[str, Any], item: Dict[str, Any], async_exec: bool = True) -> Optional[str]:
    """
    Execute a trigger on an item (legacy compatibility).
    
    Trigger format:
    {
        "command": "string command or list of args",
        "env": {"VAR": "value"},  # optional
        "input": "stdin input",  # optional
        "cwd": "/working/directory",  # optional
    }
    
    Returns stdout if not async_exec, None otherwise.
    """
    executor = TriggerExecutor()
    return executor.execute_trigger(trigger, item, async_exec)


def format_string(template: str, data: Dict[str, Any]) -> str:
    """
    Format a string template with data from an item.
    
    Supports {field} and {field.nested} syntax.
    """
    executor = TriggerExecutor()
    return executor._format_string(template, data)


def execute_trigger_chain(triggers: List[Dict[str, Any]], item: Dict[str, Any], stop_on_error: bool = False) -> List[Optional[str]]:
    """
    Execute a chain of triggers on an item.
    
    Returns list of outputs (None for async triggers).
    """
    results = []
    for trigger in triggers:
        output = execute_trigger(trigger, item)
        results.append(output)
        if stop_on_error and output is None and not trigger.get("async", True):
            break
    return results


def get_triggers_for_item(item: Dict[str, Any], trigger_map: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Get triggers that match an item based on conditions.
    
    trigger_map format:
    {
        "condition": [{"command": "..."}],
        ...
    }
    
    Conditions can be:
    - Field equality: {"type": "work"} - match items where type=work
    - Field pattern: {"summary": "*test*"} - match items where summary contains "test"
    """
    matching_triggers = []
    
    for condition, triggers in trigger_map.items():
        if matches_condition(item, condition):
            matching_triggers.extend(triggers)
    
    return matching_triggers


def matches_condition(item: Dict[str, Any], condition: str) -> bool:
    """
    Check if an item matches a condition string.
    
    Simple format: field=value
    Pattern format: field=*pattern* (contains)
    """
    if "=" not in condition:
        return False
    
    field, expected = condition.split("=", 1)
    
    item_value = item.get(field)
    if item_value is None:
        return False
    
    if expected.startswith("*") and expected.endswith("*"):
        pattern = expected[1:-1]
        return pattern.lower() in str(item_value).lower()
    else:
        return str(item_value) == expected
