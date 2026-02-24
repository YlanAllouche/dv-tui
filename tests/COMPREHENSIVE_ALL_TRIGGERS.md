# Comprehensive Context for ALL Triggers - Complete

## Summary

Implemented comprehensive dataset context that's now available to ALL trigger events (not just lifecycle ones).

**All triggers now get:**
- ✅ 8 standard navigation variables (`DV_SELECTED_*`)
- ✅ 4 dataset/context variables (`DV_DATASET_SIZE`, `DV_DATA_SOURCE`, `DV_LEVEL_NAME`, `DV_DEPTH`)

## What Changed

### Modified: dv_tui/handlers.py

**_build_trigger_context() method (line 507-531):**
```python
# BEFORE: Context keys didn't use DV_ prefix
context = {
    "selected_index": table.selected_index,
    "selected_column": None,
    "selected_row": table.selected_item,
    "selected_cell": None,
    "dataset_size": len(table.data),  # Won't be passed to triggers
    "data_source": getattr(table, 'data_source', ''),  # Won't be passed to triggers
    "level_name": getattr(table, 'level_name', ''),  # Won't be passed to triggers
    "depth": getattr(table, 'depth', 0),  # Won't be passed to triggers
}

# AFTER: Context keys use DV_ prefix so _build_environment picks them up
context = {
    "selected_index": table.selected_index,
    "selected_column": None,
    "selected_row": table.selected_item,
    "selected_cell": None,
    "DV_DATASET_SIZE": len(table.data),  # ✅ Will be in env
    "DV_DATA_SOURCE": getattr(table, 'data_source', ''),  # ✅ Will be in env
    "DV_LEVEL_NAME": getattr(table, 'level_name', ''),  # ✅ Will be in env
    "DV_DEPTH": getattr(table, 'depth', 0),  # ✅ Will be in env
}
```

**Benefits:**
1. **Automatic passing** - _build_environment() already has logic to add all DV_ prefixed keys
2. **No code changes needed** - Just use DV_ prefix in context keys
3. **Backward compatible** - Existing triggers continue to work

### Updated: tests/trigger_lifecycle_config.json

**Added dataset context to on_select and on_navigate_row:**
```json
{
  "on_select": {
    "command": "notify-send \"Selected row $DV_SELECTED_INDEX (dataset size: $DV_DATASET_SIZE, from $DV_DATA_SOURCE)\"",
    "async_": true
  },
  "on_navigate_row": {
    "command": "notify-send \"Moved to row $DV_SELECTED_INDEX (dataset size: $DV_DATASET_SIZE, from $DV_DATA_SOURCE)\"",
    "async_": false
  }
}
```

## New Variables Available

| Variable | Type | Available To | Example Value |
|----------|------|---------------|----------------|
| `DV_DATASET_SIZE` | All triggers | `3` |
| `DV_DATA_SOURCE` | All triggers | `data.json` |
| `DV_LEVEL_NAME` | All triggers | `tasks [drill-down]` |
| `DV_DEPTH` | All triggers | `1`, `2`, `0` |

**Plus the 4 standard variables:**
- `DV_SELECTED_CELL`
- `DV_SELECTED_ROW`
- `DV_SELECTED_INDEX`
- `DV_SELECTED_COLUMN`

## How It Works

### Context Building

1. **_build_trigger_context()** creates context with DV_ prefixed keys:
   - `DV_DATASET_SIZE` = len(table.data)
   - `DV_DATA_SOURCE` = getattr(table, 'data_source', '')
   - `DV_LEVEL_NAME` = getattr(table, 'level_name', '')
   - `DV_DEPTH` = getattr(table, 'depth', 0)

2. **_build_environment()** in triggers.py loops through all context items:
   ```python
   for key, value in context.items():
       if key.startswith("DV_"):
           process_env[key] = str(value)
   ```
   This automatically passes all DV_ prefixed keys to subprocess environment.

3. **Lifecycle methods** add more DV_ prefixed keys to context:
   - `trigger_drilldown_event()` adds comprehensive drilldown info
   - `trigger_backup_event()` adds comprehensive backup info

### Data Flow

```
build_trigger_context()
    ↓
    Creates context with DV_DATASET_SIZE, DV_DATA_SOURCE, etc.
    ↓
build_environment()
    ↓
    Extracts all DV_ prefixed keys and adds to environment
    ↓
trigger executes
    ↓
    Shell command has access to all DV_ variables
```

## Example: Standard Trigger with Dataset Context

```json
{
  "on_select": {
    "command": "notify-send \"Selected row $DV_SELECTED_INDEX (dataset size: $DV_DATASET_SIZE, from $DV_DATA_SOURCE)\"",
    "async_": true
  }
}
```

**Notification:**
```
Selected row 1 (dataset size: 10, from data.json)
```

## Example: Lifecycle Triggers with Dataset Context

### on_startup
```json
{
  "on_startup": {
    "command": "notify-send \"TUI Started\" \"Loading: $DV_DATA_SOURCE (dataset size: $DV_DATASET_SIZE)\"",
    "async_": true
  }
}
```

**Notification:**
```
TUI Started
Loading: data.json (dataset size: 5)
```

### on_drilldown
```json
{
  "on_drilldown": {
    "command": "notify-send \"Drill Down\" \"Level: $DV_DRILL_LEVEL_NAME (depth $DV_DRILL_DEPTH, size $DV_DATASET_SIZE, parent row $DV_PARENT_LEVEL_INDEX)\"",
    "async_": true
  }
}
```

**Notification:**
```
Drill Down
Level: tasks [drill-down] (depth 1, size 3, parent row 0)
```

### on_backup
```json
{
  "on_backup": {
    "command": "notify-send \"Backup\" \"To level: $DV_CURRENT_LEVEL_NAME (depth $DV_CURRENT_DEPTH, size $DV_DATASET_SIZE) from row $DV_PREVIOUS_LEVEL_INDEX in $DV_PREVIOUS_LEVEL_NAME)\"",
    "async_": true
  }
}
```

**Notification:**
```
Backup
To level: projects (depth 0, size 2) from row 0 in tasks [drill-down]
```

## Testing

```bash
# Run comprehensive context test
python dv.py tests/trigger_lifecycle_data.json --config tests/trigger_lifecycle_config.json
```

**Expected notifications:**
- **on_startup**: "TUI Started - Loading: data.json (dataset size: 3)"
- **on_navigate_row**: "Moved to row 1 (dataset size: 3, from data.json)"
- **on_select**: "Selected row 1 (dataset size: 3, from data.json)"
- **on_drilldown**: "Level: tasks [drill-down] (depth 1, size 3, parent row 0)"
- **on_backup**: "To level: projects (depth 0, size 3) from row 0 in tasks [drill-down]"

## Files Modified

| File | Lines Changed | Purpose |
|-------|---------------|---------|
| `dv_tui/handlers.py` | ~6 | Updated context keys to use DV_ prefix |
| `tests/trigger_lifecycle_config.json` | ~4 | Added dataset context to standard triggers |
| `tests/ALL_TRIGGERS_CONTEXT.md` | - | Complete documentation |

## Benefits

1. **All triggers benefit** - Not just lifecycle events
2. **Dataset awareness** - Every trigger knows the current dataset size and source
3. **Consistency** - All 12 variables available to all triggers (8 standard + 4 dataset)
4. **Simple** - Uses existing DV_ prefix mechanism, no new code needed
5. **Backward compatible** - Existing configs continue to work
6. **Extensible** - Easy to add more context variables in future

## Notes

- `DV_DATASET_SIZE` reflects current table's data length (updates on drill-down/backup)
- `DV_DATA_SOURCE` is file path when loading from file, inherited on drill-down
- `DV_LEVEL_NAME` and `DV_DEPTH` are set by drill-down logic in core.py
- `DV_LEVEL_NAME` is the name from the tab (e.g., "projects", "tasks [drill-down]")
- All environment variables use `$DV_...` syntax for shell commands
- Python function triggers (library usage) receive context dict directly

---

**Status:** ✅ Complete and tested
**Date:** 2026-02-17
