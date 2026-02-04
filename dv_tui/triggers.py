import subprocess
from typing import Dict, Any, List, Optional
import shlex


def execute_trigger(trigger: Dict[str, Any], item: Dict[str, Any], async_exec: bool = True) -> Optional[str]:
    """
    Execute a trigger on an item.
    
    Trigger format:
    {
        "command": "string command or list of args",
        "env": {"VAR": "value"},  # optional
        "input": "stdin input",  # optional
        "cwd": "/working/directory",  # optional
    }
    
    Returns stdout if not async_exec, None otherwise.
    """
    cmd_template = trigger.get("command", "")
    env = trigger.get("env", {})
    input_data = trigger.get("input")
    cwd = trigger.get("cwd")
    
    # Format command with item data
    if isinstance(cmd_template, str):
        cmd_str = format_string(cmd_template, item)
        try:
            cmd = shlex.split(cmd_str)
        except ValueError as e:
            print(f"Error parsing command: {e}")
            return None
    else:
        cmd = cmd_template
    
    if not cmd:
        return None
    
    # Build environment
    import os
    process_env = os.environ.copy()
    process_env.update(env)
    
    try:
        if async_exec:
            subprocess.Popen(cmd, 
                           stdin=subprocess.PIPE if input_data else None,
                           cwd=cwd,
                           env=process_env,
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True, 
                           close_fds=True)
            return None
        else:
            result = subprocess.run(cmd,
                                  input=input_data.encode() if input_data else None,
                                  cwd=cwd,
                                  env=process_env,
                                  capture_output=True,
                                  text=True)
            return result.stdout
    except Exception as e:
        print(f"Error executing trigger: {e}")
        return None


def format_string(template: str, data: Dict[str, Any]) -> str:
    """
    Format a string template with data from an item.
    
    Supports {field} and {field.nested} syntax.
    """
    result = template
    
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool)):
            result = result.replace(f"{{{key}}}", str(value))
        elif isinstance(value, dict):
            for nested_key, nested_value in value.items():
                if isinstance(nested_value, (str, int, float, bool)):
                    result = result.replace(f"{{{key}.{nested_key}}}", str(nested_value))
    
    return result


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
