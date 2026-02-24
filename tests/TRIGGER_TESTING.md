# Trigger System Testing Guide

This guide provides examples for testing the trigger system implemented in change proposal 10-trigger-system.

## Test Data

Two test files are provided:
- `tests/trigger_test_data.json` - Sample task data
- `tests/trigger_test_config.json` - Configuration with trigger examples

## Example 1: Basic Trigger Testing

Test table-level triggers with basic echo commands:

```bash
# Run dv-tui with trigger configuration
dv tests/trigger_test_data.json --config tests/trigger_test_config.json
```

**Expected behavior:**
- Arrow keys up/down will trigger `on_change` (sync, visible in terminal)
- Press Enter to trigger `on_select` (async, logs selection)
- Navigate and see different messages

## Example 2: Row-Specific Triggers

The config has row-specific triggers for row 0 and row 3.

```bash
dv tests/trigger_test_data.json --config tests/trigger_test_config.json
```

**Test steps:**
1. Navigate to row 0 (first row)
2. Press Enter - should see "You selected the first task"
3. Navigate to row 3 (fourth row)
4. Press Enter - should see "High priority task selected!"
5. Press Enter on other rows - should see default table trigger

## Example 3: Cell-Specific Triggers

The config has cell-specific triggers for row 0:name and row 2:status.

```bash
dv tests/trigger_test_data.json --config tests/trigger_test_config.json
```

**Test steps:**
1. Press 'c' to toggle to cell mode
2. Navigate to row 0, column "name"
3. Press Enter - should see "Cell value: Task 1 at column name"
4. Navigate to row 2, column "status"
5. Press Enter - should see "Task status: done"
6. Navigate to other cells - should use table/row triggers

## Example 4: Custom Trigger Scripts

Using shell scripts as triggers:

```bash
# Create a config that uses custom scripts
cat > tests/trigger_custom_config.json << 'EOF'
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "./tests/trigger_scripts/show_task_details.sh",
                "async_": false
            }
        }
    }
}
EOF

# Test it
dv tests/trigger_test_data.json --config tests/trigger_custom_config.json
```

## Example 5: Logging Triggers

Use triggers to log all selections to a file:

```bash
# Create a logging config
cat > tests/trigger_logging_config.json << 'EOF'
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "./tests/trigger_scripts/log_selection.sh",
                "async_": true
            }
        }
    }
}
EOF

# Test it
dv tests/trigger_test_data.json --config tests/trigger_logging_config.json

# After testing, check the log
cat /tmp/dv-tui-triggers.log
```

## Example 6: Environment Variable Testing

Test that all environment variables are passed correctly:

```bash
# Create a config that dumps all environment variables
cat > tests/trigger_env_config.json << 'EOF'
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "env | grep DV_SELECTED_",
                "async_": false
            }
        }
    }
}
EOF

# Test it
dv tests/trigger_test_data.json --config tests/trigger_env_config.json
```

**Expected output:**
```
DV_SELECTED_CELL=Task 1
DV_SELECTED_INDEX=0
DV_SELECTED_COLUMN=name
DV_SELECTED_ROW={"id":1,"name":"Task 1","status":"active","priority":"high"}
```

## Example 7: Command Formatting with Templates

Use template variables in commands:

```bash
# Create a config with command templates
cat > tests/trigger_template_config.json << 'EOF'
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "echo \"Task {selected_cell} (row {selected_index})\"",
                "async_": false
            }
        }
    }
}
EOF

# Test it
dv tests/trigger_test_data.json --config tests/trigger_template_config.json
```

## Example 8: Python Function Triggers (Library Usage)

For Python library usage, you can register Python functions as triggers:

```python
from dv_tui.triggers import TriggerManager
from dv_tui.table import Table
from dv_tui.handlers import KeyHandler

# Create a table and handler
data = [{"id": 1, "name": "Task 1"}]
table = Table(data)
handler = KeyHandler()

# Define a Python function trigger
def my_trigger(context):
    print(f"Python trigger fired!")
    print(f"Cell: {context['selected_cell']}")
    print(f"Row: {context['selected_row']}")
    return "Trigger executed"

# Register the Python function
handler.trigger_manager.register_python_function('my_trigger', my_trigger)

# Set up the trigger
handler.trigger_manager.set_table_triggers({
    'on_select': {'function': 'my_trigger'}
})

# Test trigger execution
context = {
    'selected_cell': 'Task 1',
    'selected_row': {'id': 1, 'name': 'Task 1'},
    'selected_index': 0,
    'selected_column': 'name'
}
result = handler.trigger_manager.execute_trigger_event('on_select', context)
print(f"Result: {result}")
```

## Example 9: Priority Testing (Cell > Row > Table)

Test that triggers follow the correct priority:

```bash
# Create a config with all trigger levels
cat > tests/trigger_priority_config.json << 'EOF'
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "echo \"Table trigger\"",
                "async_": false
            }
        },
        "rows": {
            "1": {
                "on_select": {
                    "command": "echo \"Row trigger\"",
                    "async_": false
                }
            }
        },
        "cells": {
            "0:name": {
                "on_select": {
                    "command": "echo \"Cell trigger\"",
                    "async_": false
                }
            }
        }
    }
}
EOF

# Test it
dv tests/trigger_test_data.json --config tests/trigger_priority_config.json
```

**Test steps:**
1. Press Enter on row 2, any column - should see "Table trigger"
2. Press Enter on row 1, any column - should see "Row trigger"
3. Press 'c' to enter cell mode, navigate to row 0, column "name", press Enter - should see "Cell trigger"

## Example 10: Async vs Sync Execution

Test the difference between async and sync execution:

```bash
# Create a config with both async and sync triggers
cat > tests/trigger_async_config.json << 'EOF'
{
    "triggers": {
        "table": {
            "on_change": {
                "command": "echo \"Sync trigger on change\"",
                "async_": false
            },
            "on_select": {
                "command": "sleep 1 && echo \"Async trigger on select (delayed)\" > /tmp/async-test.log",
                "async_": true
            }
        }
    }
}
EOF

# Test it
dv tests/trigger_test_data.json --config tests/trigger_async_config.json
```

**Expected behavior:**
- Arrow keys up/down - immediate "Sync trigger on change" output
- Enter - no immediate output, but after 1 second check `/tmp/async-test.log`

## Testing Checklist

- [ ] Table-level triggers work (on_enter, on_select, on_change)
- [ ] Row-level triggers work
- [ ] Cell-level triggers work
- [ ] Priority is correct (cell > row > table)
- [ ] Environment variables are passed correctly
- [ ] Async execution doesn't block the UI
- [ ] Sync execution shows output immediately
- [ ] Shell scripts work as triggers
- [ ] Template variables in commands are formatted correctly
- [ ] Python function triggers work (library usage)
- [ ] Errors are handled gracefully

## Debugging

If triggers aren't working as expected:

1. Check the config syntax:
```bash
python -m json.tool tests/trigger_test_config.json
```

2. Make shell scripts executable:
```bash
chmod +x tests/trigger_scripts/*.sh
```

3. Test scripts manually:
```bash
DV_SELECTED_CELL="test" DV_SELECTED_INDEX=0 ./tests/trigger_scripts/show_task_details.sh
```

4. Enable verbose output in your terminal to see trigger execution

## Real-World Use Cases

1. **Task Management**: Open task details in an editor when selected
2. **CI/CD Dashboard**: Trigger builds when selecting specific jobs
3. **Log Viewer**: Tail logs when selecting a specific service
4. **File Browser**: Open files in external applications
5. **API Viewer**: Make API calls to fetch more details
6. **Monitoring**: Send alerts when selecting critical metrics
7. **Data Analysis**: Export selected data for processing

## Notes

- Triggers are loaded from the config file's `triggers` section
- Cell triggers only work in cell mode (press 'c' to toggle)
- Environment variables use the prefix `DV_SELECTED_`
- Use `async_: true` for triggers that shouldn't block the UI
- Python function triggers are for library usage only (not CLI)
- Triggers execute in the order: cell > row > table
