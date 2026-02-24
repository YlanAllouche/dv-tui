#!/usr/bin/env python3
"""Interactive trigger system test"""

from dv_tui.triggers import TriggerManager, TriggerExecutor
from dv_tui.config import Config
import json

def test_basic_triggers():
    """Test basic trigger execution."""
    print("\n1. Testing Basic Triggers")
    print("-" * 40)
    
    executor = TriggerExecutor()
    
    # Test shell command
    context = {
        'selected_cell': 'Task 1',
        'selected_row': {'id': 1, 'name': 'Task 1'},
        'selected_index': 0,
        'selected_column': 'name'
    }
    
    result = executor.execute_trigger({
        'command': 'echo "Selected: $DV_SELECTED_CELL"',
        'async_': False
    }, context, async_exec=False)
    
    print(f"Shell trigger output: {result.strip()}")
    
    # Test Python function
    def log_selection(ctx):
        return f"Logged selection: {ctx['selected_cell']}"
    
    executor.register_python_function('log_selection', log_selection)
    result = executor.execute_trigger({'function': 'log_selection'}, context)
    print(f"Python trigger output: {result}")

def test_priority():
    """Test trigger priority (cell > row > table)."""
    print("\n2. Testing Trigger Priority")
    print("-" * 40)
    
    manager = TriggerManager()
    
    # Set triggers at all levels
    manager.set_table_triggers({
        'on_select': {'command': 'echo "Table level"'}
    })
    manager.set_row_triggers(0, {
        'on_select': {'command': 'echo "Row level"'}
    })
    manager.set_cell_triggers(0, 'name', {
        'on_select': {'command': 'echo "Cell level"'}
    })
    
    # Test at cell level (should use cell trigger)
    context = {
        'selected_cell': 'Task 1',
        'selected_row': {'id': 1, 'name': 'Task 1'},
        'selected_index': 0,
        'selected_column': 'name'
    }
    
    trigger = manager.get_trigger('on_select', context)
    print(f"Trigger for (0, name): {trigger['command']}")
    
    # Test at row level (should use row trigger)
    context['selected_column'] = 'other_column'
    trigger = manager.get_trigger('on_select', context)
    print(f"Trigger for (0, other): {trigger['command']}")
    
    # Test at table level (should use table trigger)
    context['selected_index'] = 5
    trigger = manager.get_trigger('on_select', context)
    print(f"Trigger for (5, other): {trigger['command']}")

def test_env_vars():
    """Test environment variable passing."""
    print("\n3. Testing Environment Variables")
    print("-" * 40)
    
    executor = TriggerExecutor()
    
    context = {
        'selected_cell': 'Active Task',
        'selected_row': {'id': 1, 'name': 'Task 1', 'status': 'active'},
        'selected_index': 0,
        'selected_column': 'name'
    }
    
    # Build environment
    env = executor._build_environment(context, {})
    
    print(f"DV_SELECTED_CELL: {env.get('DV_SELECTED_CELL')}")
    print(f"DV_SELECTED_INDEX: {env.get('DV_SELECTED_INDEX')}")
    print(f"DV_SELECTED_COLUMN: {env.get('DV_SELECTED_COLUMN')}")
    print(f"DV_SELECTED_ROW: {env.get('DV_SELECTED_ROW')[:50]}...")

def test_template_formatting():
    """Test command template formatting."""
    print("\n4. Testing Template Formatting")
    print("-" * 40)
    
    executor = TriggerExecutor()
    
    context = {
        'selected_cell': 'Task 1',
        'selected_index': 0,
        'selected_column': 'name'
    }
    
    templates = [
        "Task {selected_cell}",
        "Index: {selected_index}",
        "Column: {selected_column}",
        "Task {selected_cell} at index {selected_index}"
    ]
    
    for template in templates:
        formatted = executor._format_string(template, context)
        print(f"{template:40} -> {formatted}")

def test_config_loading():
    """Test loading triggers from config."""
    print("\n5. Testing Config Loading")
    print("-" * 40)
    
    # Load test config
    with open('tests/trigger_test_config.json') as f:
        config_data = json.load(f)
    
    print(f"Config has triggers: {'triggers' in config_data}")
    print(f"Table triggers: {list(config_data.get('triggers', {}).get('table', {}).keys())}")
    print(f"Row triggers: {list(config_data.get('triggers', {}).get('rows', {}).keys())}")
    print(f"Cell triggers: {list(config_data.get('triggers', {}).get('cells', {}).keys())}")

def main():
    """Run all tests."""
    print("=" * 50)
    print("TRIGGER SYSTEM INTERACTIVE TEST")
    print("=" * 50)
    
    test_basic_triggers()
    test_priority()
    test_env_vars()
    test_template_formatting()
    test_config_loading()
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 50)
    print("\nTo test interactively with the CLI:")
    print("  dv tests/trigger_test_data.json --config tests/trigger_test_config.json")
    print("\nFor more examples, see tests/TRIGGER_TESTING.md")

if __name__ == '__main__':
    main()
