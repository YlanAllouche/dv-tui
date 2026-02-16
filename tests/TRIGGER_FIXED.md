# Trigger System - Fixed and Working

## Issue Fixed

The trigger system was not working because triggers were not being loaded from the config into the trigger manager. The issue was in the `_load_triggers` method in `handlers.py`.

### Root Cause

The config loader uses dataclasses (`TriggersConfig`, `TriggerConfig`) to store trigger configuration, but the `_load_triggers` method was checking `isinstance(triggers, dict)`, which always returned `False` for dataclass objects.

### Fix Applied

Updated `_load_triggers` in `handlers.py` to:
1. Properly access dataclass attributes (`.on_enter`, `.on_select`, `.on_change`)
2. Convert dataclass values to the format expected by `TriggerManager`
3. Handle `None` values correctly

## Verification

### Quick Test

```bash
# Run automated tests
./tests/test_triggers.sh

# Run notification test (you should see 5 desktop notifications)
./tests/test_notify.sh

# Run interactive Python tests
PYTHONPATH=. python3 tests/interactive_test.py
```

### Interactive CLI Test

```bash
# Run dv-tui with trigger configuration
dv tests/trigger_test_data.json --config tests/trigger_test_config.json
```

**What to try:**
1. Press arrow keys (up/down) - should see "Moved to row X" notification
2. Press Enter on any row - should see notification
3. Press Enter on row 0 - should see "You selected the first task" notification
4. Press Enter on row 3 - should see "High priority task selected!" notification
5. Press 'c' to toggle cell mode, navigate to row 0 column "name", press Enter - should see cell trigger notification

## Test Results

All tests pass:
- ✅ Config loads correctly
- ✅ Triggers are loaded into trigger manager
- ✅ Table triggers work
- ✅ Row triggers work
- ✅ Cell triggers work
- ✅ Priority system works (cell > row > table)
- ✅ Environment variables are passed
- ✅ Sync and async execution work
- ✅ Template formatting works
- ✅ notify-send commands work

## Configuration Files

### Simple String Format

```json
{
    "triggers": {
        "table": {
            "on_select": "notify-send \"Selected: $DV_SELECTED_CELL\""
        }
    }
}
```

### Object Format (Full Control)

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "notify-send \"Selected: $DV_SELECTED_CELL\"",
                "async_": false
            }
        }
    }
}
```

## Available Test Files

- `tests/trigger_test_data.json` - Sample task data
- `tests/trigger_test_config.json` - Configuration with notify-send triggers
- `tests/test_notify.sh` - Script to test all triggers with notifications
- `tests/test_triggers.sh` - Automated test suite
- `tests/interactive_test.py` - Python test suite
- `tests/TRIGGER_QUICKSTART.md` - Quick start guide
- `tests/TRIGGER_TESTING.md` - Comprehensive testing guide
- `tests/TRIGGER_IMPLEMENTATION.md` - Implementation summary

## Trigger Events

- `on_select` - Fired when Enter is pressed
- `on_enter` - Fired when table is entered
- `on_change` - Fired when selection changes (arrow keys)

## Environment Variables

All triggers receive these environment variables:
- `DV_SELECTED_CELL` - Value of the selected cell
- `DV_SELECTED_ROW` - Full row data as JSON string
- `DV_SELECTED_INDEX` - Row index (0-based)
- `DV_SELECTED_COLUMN` - Column name

## Trigger Priority

When multiple triggers are defined for the same event:
1. **Cell trigger** (if in cell mode and cell-specific trigger exists)
2. **Row trigger** (if row-specific trigger exists)
3. **Table trigger** (default)

## Example: All Three Levels

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "notify-send \"Table trigger: $DV_SELECTED_INDEX\"",
                "async_": false
            }
        },
        "rows": {
            "0": {
                "on_select": {
                    "command": "notify-send \"Row 0 trigger\"",
                    "async_": false
                }
            },
            "3": {
                "on_select": {
                    "command": "notify-send \"Row 3 trigger\"",
                    "async_": false
                }
            }
        },
        "cells": {
            "0:name": {
                "on_select": {
                    "command": "notify-send \"Cell (0, name) trigger: $DV_SELECTED_CELL\"",
                    "async_": false
                }
            }
        }
    }
}
```

**Testing this config:**
- Row 0, column "id" (row mode) → Row 0 trigger fires
- Row 1, any column (row mode) → Table trigger fires
- Row 3, any column (row mode) → Row 3 trigger fires
- Row 0, column "name" (cell mode) → Cell (0, name) trigger fires

## Real-World Examples

### Open Task in Editor

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "nvim +/{selected_index} tasks.md",
                "async_": true
            }
        }
    }
}
```

### Log Selections

```json
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
```

### Send Desktop Notification

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "notify-send \"Task Selected\" \"$DV_SELECTED_CELL\"",
                "async_": false
            }
        }
    }
}
```

### Make API Call

```json
{
    "triggers": {
        "rows": {
            "0": {
                "on_select": {
                    "command": "curl -X POST http://api.example.com/tasks/$DV_SELECTED_INDEX/start",
                    "async_": true
                }
            }
        }
    }
}
```

## Notes

- Triggers must be configured with `--config` flag
- Cell triggers only work in cell mode (press 'c' to toggle)
- Use `async_: true` for commands that shouldn't block the UI
- Use `async_: false` to see command output in the terminal
- Environment variables are passed as strings, not JSON objects
- Template variables use `{selected_cell}`, `{selected_index}`, etc.
- Both string and object formats are supported for triggers
- Test triggers manually before using them in production

## Troubleshooting

**Notifications not appearing:**
1. Check if notify-send is installed: `which notify-send`
2. Test manually: `notify-send "Test" "This is a test"`
3. Check notification daemon is running

**Triggers not executing:**
1. Verify config syntax: `python3 -m json.tool config.json`
2. Check triggers are loaded in test script: `./tests/test_notify.sh`
3. Enable verbose output when debugging

**Environment variables not passed:**
1. Test with `env | grep DV_SELECTED`
2. Check trigger command uses correct variable names
3. Verify trigger format (object vs string)

## Success!

The trigger system is now fully functional. All trigger types (table, row, cell) work correctly with proper priority handling, environment variable passing, and both sync/async execution modes.
