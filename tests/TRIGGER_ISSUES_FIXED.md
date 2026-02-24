# Trigger System - Issues Fixed

## Issues Fixed

### Issue 1: Row and Cell Triggers Had Same Effect
**Problem:** When in row mode, cell triggers were firing instead of row triggers.

**Cause:** In `_build_trigger_context()`, `selected_column` was always being set to a value (the first column by default), even in row mode. The trigger priority check `if row_index is not None and column is not None:` was always true, so cell triggers had priority over row triggers.

**Fix:** Modified `_build_trigger_context()` to set `selected_column` to `None` by default. It's only set when in cell mode:

```python
def _build_trigger_context(self, table, column: Optional[str] = None) -> Dict[str, Any]:
    context = {
        "selected_index": table.selected_index,
        "selected_column": None,  # Always None by default
        "selected_row": table.selected_item,
        "selected_cell": None
    }
    
    # Only set column and cell in cell mode
    if table.selection_mode == 'cell' and table.selected_column < len(table.columns):
        col_name = table.columns[table.selected_column]
        context["selected_cell"] = table.selected_item.get(col_name)
        context["selected_column"] = col_name
    
    return context
```

**Result:** Now the priority works correctly:
- Cell mode + cell trigger → Cell trigger fires
- Row mode + row trigger → Row trigger fires
- No specific trigger → Table trigger fires

### Issue 2: Environment Variables Not Expanding
**Problem:** Commands like `notify-send "Test" "$DV_SELECTED_CELL"` were showing the literal `$DV_SELECTED_CELL` instead of its value.

**Cause:** When using `subprocess.run()` with a list of arguments (via `shlex.split()`), the shell doesn't interpret environment variables. The `$DV_SELECTED_CELL` was passed literally to the command.

**Fix:** Changed `_execute_shell_command()` to:
1. Format template variables first (like `{selected_cell}`)
2. Pass the command string directly to subprocess with `shell=True`
3. This allows shell to expand `$DV_SELECTED_CELL` environment variables

```python
def _execute_shell_command(self, trigger, context, async_exec: bool) -> Optional[str]:
    # Format template variables
    cmd_str = self._format_string(cmd_template, context)
    
    # Use shell=True to allow $VAR expansion
    use_shell = True
    
    subprocess.Popen(
        cmd_str,  # String, not list
        shell=use_shell,  # Enable shell interpretation
        env=env,  # Environment with DV_SELECTED_* variables
        ...
    )
```

**Result:** Environment variables now expand correctly:
- `"$DV_SELECTED_CELL"` → actual cell value
- `"$DV_SELECTED_INDEX"` → actual row index
- `"{selected_cell}"` → template variable (still works)

## Verification

### Test Priority

```bash
PYTHONPATH=. python3 << 'PYEOF'
from dv_tui.config import load_config
from dv_tui.handlers import KeyHandler
from dv_tui.table import Table

config = load_config(config_path='tests/trigger_test_config.json')
handler = KeyHandler(config)

data = [{"id": 1, "name": "Task 1"}]
table = Table(data)

# Test row mode
table.selected_index = 0
table.selection_mode = 'row'
context = handler._build_trigger_context(table)
print(f"Row mode: col={context['selected_column']}, cell={context['selected_cell']}")

# Test cell mode
table.selection_mode = 'cell'
table.selected_column = 1
context = handler._build_trigger_context(table)
print(f"Cell mode: col={context['selected_column']}, cell={context['selected_cell']}")
PYEOF
```

Expected output:
```
Row mode: col=None, cell=None
Cell mode: col=name, cell=Task 1
```

### Test Environment Variables

```bash
PYTHONPATH=. python3 << 'PYEOF'
from dv_tui.triggers import TriggerExecutor

executor = TriggerExecutor()
context = {'selected_cell': 'Test', 'selected_index': 0}

trigger = {
    'command': 'notify-send "Test" "$DV_SELECTED_CELL"',
    'async_': False
}
executor.execute_trigger(trigger, context, async_exec=False)
PYEOF
```

Should show notification with "Test" text, not "$DV_SELECTED_CELL".

## Testing

```bash
# Run all tests
./tests/test_notify.sh

# Test interactively
dv tests/trigger_test_data.json --config tests/trigger_test_config.json
```

**In CLI:**
- Press arrow keys → "Moved to row X" notification
- Press Enter on row 0 → "You selected the first task: Task 1" notification
- Press 'c' (cell mode), go to row 0 col "name", press Enter → "Cell value: Task 1 at column name" notification
- Press Enter on row 1 → "Selected row 1" notification

## Configuration Examples

### Both Shell Variables and Template Variables

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "notify-send \"{selected_cell}\" at index $DV_SELECTED_INDEX",
                "async_": false
            }
        }
    }
}
```

Result: Shows notification like "Task 1 at index 0"

### Priority Testing

```json
{
    "triggers": {
        "table": {
            "on_select": {
                "command": "notify-send \"Table trigger\"",
                "async_": false
            }
        },
        "rows": {
            "0": {
                "on_select": {
                    "command": "notify-send \"Row 0 trigger\"",
                    "async_": false
                }
            }
        },
        "cells": {
            "0:name": {
                "on_select": {
                    "command": "notify-send \"Cell trigger\"",
                    "async_": false
                }
            }
        }
    }
}
```

**Testing:**
- Row 0, row mode → "Row 0 trigger" notification
- Row 0, cell mode, col "name" → "Cell trigger" notification  
- Row 1, row mode → "Table trigger" notification

## Summary

✅ **Fixed:** Trigger priority (cell > row > table) now works correctly
✅ **Fixed:** Environment variables (`$DV_SELECTED_CELL`) now expand to actual values
✅ **Working:** Template variables (`{selected_cell}`) still work
✅ **Working:** Both sync and async execution modes
✅ **Verified:** All trigger types (table, row, cell) work correctly

The trigger system is now fully functional with correct priority handling and environment variable expansion!
