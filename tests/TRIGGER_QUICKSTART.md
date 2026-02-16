# Trigger System - Quick Start

## What is the Trigger System?

The trigger system allows you to execute shell commands or Python functions when you interact with data in dv-tui. You can set triggers at three levels:

1. **Table level** - Triggers that fire for any row/cell
2. **Row level** - Triggers that fire for specific rows
3. **Cell level** - Triggers that fire for specific cells

Priority: Cell > Row > Table

## Trigger Formats

Triggers can be specified in two formats:

### 1. Simple String Format (Backward Compatible)

```json
{
    "triggers": {
        "table": {
            "on_select": "echo \"Selected: $DV_SELECTED_CELL\""
        }
    }
}
```

### 2. Object Format (Full Control)

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "echo \"Selected: $DV_SELECTED_CELL\"",
                "async_": true,
                "env": {
                    "MY_VAR": "value"
                },
                "cwd": "/path/to/dir"
            }
        }
    }
}
```

## Available Events

- `on_select` - Fired when Enter is pressed
- `on_enter` - Fired when the table is entered
- `on_change` - Fired when selection changes (arrow keys)

## Environment Variables

Triggers receive these environment variables:

- `DV_SELECTED_CELL` - Value of the selected cell
- `DV_SELECTED_ROW` - Full row data as JSON
- `DV_SELECTED_INDEX` - Row index (0-based)
- `DV_SELECTED_COLUMN` - Column name

## Quick Test

### Automated Tests

```bash
# Run quick automated tests
./tests/test_triggers.sh

# Run interactive tests
PYTHONPATH=. python3 tests/interactive_test.py
```

### Interactive CLI Test

```bash
# Run with trigger configuration
dv tests/trigger_test_data.json --config tests/trigger_test_config.json
```

**What to try:**
1. Press arrow keys (up/down) - see "on_change" trigger
2. Press Enter - see "on_select" trigger
3. Press 'c' to toggle cell mode
4. Navigate to row 0, column "name", press Enter - see cell trigger
5. Navigate to row 1, press Enter - see row trigger
6. Navigate to other rows, press Enter - see table trigger

## Configuration Example (Full)

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "echo \"Selected: $DV_SELECTED_CELL\"",
                "async_": false
            },
            "on_change": {
                "command": "echo \"Changed to: $DV_SELECTED_INDEX\"",
                "async_": false
            }
        },
        "rows": {
            "0": {
                "on_select": {
                    "command": "echo \"First row!\"",
                    "async_": false
                }
            }
        },
        "cells": {
            "0:name": {
                "on_select": {
                    "command": "echo \"Cell: $DV_SELECTED_CELL\"",
                    "async_": false
                }
            }
        }
    }
}
```

## Python Function Triggers (Library Usage)

```python
from dv_tui.triggers import TriggerManager

def my_trigger(context):
    print(f"Cell: {context['selected_cell']}")
    return "Executed"

manager = TriggerManager()
manager.register_python_function('my_trigger', my_trigger)
manager.set_table_triggers({
    'on_select': {'function': 'my_trigger'}
})
```

## Template Variables

You can use template variables in commands:

```json
{
    "on_select": {
        "command": "echo \"Task {selected_cell} at index {selected_index}\""
    }
}
```

Available templates:
- `{selected_cell}` - Cell value
- `{selected_index}` - Row index
- `{selected_column}` - Column name
- `{selected_row.field}` - Any field from the row

## Async vs Sync Execution

- `async_: true` - Command runs in background, doesn't block UI
- `async_: false` - Command runs synchronously, output visible in terminal

## Files

- `tests/trigger_test_data.json` - Sample data for testing
- `tests/trigger_test_config.json` - Configuration with example triggers
- `tests/trigger_scripts/` - Example trigger shell scripts
- `tests/TRIGGER_TESTING.md` - Comprehensive testing guide with 10 examples
- `tests/test_triggers.sh` - Automated test script
- `tests/test_triggers_interactive.sh` - Interactive test script

## More Examples

See `tests/TRIGGER_TESTING.md` for 10 detailed examples including:

1. Basic trigger testing
2. Row-specific triggers
3. Cell-specific triggers
4. Custom trigger scripts
5. Logging triggers
6. Environment variable testing
7. Command formatting with templates
8. Python function triggers (library)
9. Priority testing
10. Async vs sync execution

## Use Cases

- **Task Management**: Open task details in editor when selected
- **CI/CD Dashboard**: Trigger builds for specific jobs
- **Log Viewer**: Tail logs for selected services
- **File Browser**: Open files in external apps
- **API Viewer**: Fetch details for selected items
- **Monitoring**: Send alerts for critical metrics
- **Data Analysis**: Export data for processing

## Tips

- Use `async_: true` for commands that shouldn't block UI
- Cell triggers only work in cell mode (press 'c')
- Python function triggers are for library usage only
- Test scripts manually before using as triggers
- Use `env | grep DV_SELECTED` to debug environment passing
- Both string and object formats are supported for trigger definitions
