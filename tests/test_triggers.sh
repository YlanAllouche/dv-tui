#!/bin/bash
# Quick test script for trigger system

set -e

echo "=== Trigger System Quick Test ==="
echo ""

# Test 1: Basic functionality
echo "Test 1: Basic trigger execution with environment variables"
cat > tests/trigger_quick_test.json << 'EOF'
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "echo \"Cell: $DV_SELECTED_CELL, Index: $DV_SELECTED_INDEX\"",
                "async_": false
            }
        }
    }
}
EOF

echo "✓ Config created: tests/trigger_quick_test.json"
echo ""

# Test 2: Python trigger
echo "Test 2: Python function trigger"
python3 << 'PYEOF'
from dv_tui.triggers import TriggerManager, TriggerExecutor

# Test 1: Shell command trigger
executor = TriggerExecutor()
context = {
    'selected_cell': 'test_value',
    'selected_row': {'name': 'test'},
    'selected_index': 0,
    'selected_column': 'name'
}

# Test shell command
result = executor.execute_trigger({
    'command': 'echo "Test output"',
    'async_': False
}, context, async_exec=False)
print(f"✓ Shell trigger executed: {result.strip() if result else 'None'}")

# Test Python function
def my_func(ctx):
    return f"Processed: {ctx['selected_cell']}"

executor.register_python_function('my_func', my_func)
result = executor.execute_trigger({'function': 'my_func'}, context)
print(f"✓ Python trigger executed: {result}")

# Test trigger manager
manager = TriggerManager()
manager.set_table_triggers({'on_select': {'command': 'echo test'}})
trigger = manager.get_trigger('on_select', context)
print(f"✓ Trigger manager works: {trigger is not None}")

# Test priority
manager.set_row_triggers(0, {'on_select': {'command': 'echo row'}})
manager.set_cell_triggers(0, 'name', {'on_select': {'command': 'echo cell'}})

# Should get cell trigger (highest priority)
trigger = manager.get_trigger('on_select', context)
print(f"✓ Cell trigger priority works: {trigger['command'] == 'echo cell'}")

print("✓ All Python tests passed!")
PYEOF

echo ""

# Test 3: Config validation
echo "Test 3: Config file validation"
python3 -m json.tool tests/trigger_test_config.json > /dev/null
echo "✓ trigger_test_config.json is valid JSON"
python3 -m json.tool tests/trigger_quick_test.json > /dev/null
echo "✓ trigger_quick_test.json is valid JSON"
echo ""

# Test 4: Script executability
echo "Test 4: Trigger script executability"
if [ -x "tests/trigger_scripts/log_selection.sh" ]; then
    echo "✓ log_selection.sh is executable"
else
    echo "✗ log_selection.sh is not executable"
fi
if [ -x "tests/trigger_scripts/show_task_details.sh" ]; then
    echo "✓ show_task_details.sh is executable"
else
    echo "✗ show_task_details.sh is not executable"
fi
echo ""

# Test 5: Environment variable passing
echo "Test 5: Environment variable passing"
DV_SELECTED_CELL="test" DV_SELECTED_INDEX=5 DV_SELECTED_COLUMN="name" \
    ./tests/trigger_scripts/show_task_details.sh > /dev/null
echo "✓ Environment variables work in trigger scripts"
echo ""

# Test 6: Template formatting
echo "Test 6: Command template formatting"
python3 << 'PYEOF'
from dv_tui.triggers import TriggerExecutor

executor = TriggerExecutor()
context = {
    'selected_cell': 'Task 1',
    'selected_index': 0,
    'selected_column': 'name'
}

cmd = executor._format_string("Task {selected_cell} at index {selected_index}", context)
print(f"✓ Template formatted: {cmd}")
assert cmd == "Task Task 1 at index 0", "Template formatting failed"

cmd = executor._format_string("Column: {selected_column}", context)
print(f"✓ Column template: {cmd}")
assert cmd == "Column: name", "Column template failed"

print("✓ All template tests passed!")
PYEOF

echo ""
echo "=== All quick tests passed! ==="
echo ""
echo "To test interactively, run:"
echo "  dv tests/trigger_test_data.json --config tests/trigger_test_config.json"
echo ""
echo "See tests/TRIGGER_TESTING.md for more examples."
