# Comprehensive Context for ALL Triggers

## Overview

Implemented comprehensive dataset context that's now available to ALL trigger events (not just lifecycle ones).

## What Changed

### Before: Minimal Context

Standard triggers (`on_select`, `on_navigate_row`, `on_navigate_cell`, `on_enter`) only had:
- `DV_SELECTED_CELL`
- `DV_SELECTED_ROW`
- `DV_SELECTED_INDEX`
- `DV_SELECTED_COLUMN`

### After: Comprehensive Context

ALL triggers now have access to:
- `DV_DATASET_SIZE` - Number of items in current dataset
- `DV_DATA_SOURCE` - Data file path or identifier
- `DV_LEVEL_NAME` - Name of current navigation level
- `DV_DEPTH` - Navigation depth level (0-based)

**Plus** the 4 standard variables.

## New Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `DV_DATASET_SIZE` | Integer | Total items in current data | `3` |
| `DV_DATA_SOURCE` | String | File path or source identifier | `data.json` |
| `DV_LEVEL_NAME` | String | Current navigation level name | `tasks [drill-down]` |
| `DV_DEPTH` | Integer | Current navigation depth | `0`, `1`, `2` |

These are available to:
- ✅ **on_startup** - Startup trigger
- ✅ **on_drilldown** - Lifecycle drill-down trigger
- ✅ **on_backup** - Lifecycle backup trigger
- ✅ **on_select** - Standard selection trigger
- ✅ **on_navigate_row** - Row navigation trigger
- ✅ **on_navigate_cell** - Cell navigation trigger
- ✅ **on_enter** - Enter key press trigger

## Implementation Details

### Modified: dv_tui/handlers.py

**_build_trigger_context() method (lines 507-527):**
```python
# BEFORE:
context = {
    "selected_index": table.selected_index,
    "selected_column": None,
    "selected_row": table.selected_item,
    "selected_cell": None,
}

# AFTER:
context = {
    "selected_index": table.selected_index,
    "selected_column": None,
    "selected_row": table.selected_item,
    "selected_cell": None,
    # Dataset information available to all triggers
    "dataset_size": len(table.data),
    "data_source": getattr(table, 'data_source', ''),
    # Level information (if available)
    "level_name": getattr(table, 'level_name', ''),
    "depth": getattr(table, 'depth', 0),
}
```

**Benefits:**
1. **Consistency** - All triggers get the same comprehensive context
2. **Automatic** - Works without modifying trigger method signatures
3. **Flexible** - Uses getattr() to safely access optional attributes
4. **Extensible** - Easy to add more context variables in future

### How It Works

1. **table.data_source** is set**:
   - When loading from file → file path
   - When drilling down → inherited from parent

2. **table.level_name** and **table.depth** are set**:
   - When drilling down → incremented depth, level name updated
   - When backing up → decremented depth

3. **dataset_size** is calculated**:
   - Always reflects current table's data length
   - Updates when drilling down (nested data size)
   - Restores when backing up (original data size)

## Example Usage

### on_select with dataset context

```json
{
  "triggers": {
    "table": {
      "on_select": {
        "command": "notify-send \"Selected row $DV_SELECTED_INDEX (dataset size: $DV_DATASET_SIZE, from $DV_DATA_SOURCE)\"",
        "async_": true
      }
    }
  }
}
```

**Notification:**
```
Selected row 1 (dataset size: 10, from data.json)
```

### on_navigate_row with dataset context

```json
{
  "triggers": {
    "table": {
      "on_navigate_row": {
        "command": "notify-send \"Moved to row $DV_SELECTED_INDEX (dataset size: $DV_DATASET_SIZE, level: $DV_LEVEL_NAME, depth: $DV_DEPTH)\"",
        "async_": false
      }
    }
  }
}
```

**Notification:**
```
Moved to row 2 (dataset size: 10, level: tasks [drill-down], depth 0)
```

### on_startup with dataset context

```json
{
  "triggers": {
    "table": {
      "on_startup": {
        "command": "notify-send \"TUI Started\" \"Loading: $DV_DATA_SOURCE (dataset size: $DV_DATASET_SIZE)\"",
        "async_": true
      }
    }
  }
}
```

**Notification:**
```
TUI Started
Loading: data.json (dataset size: 5)
```

## Testing

### Test with Updated Config

```bash
# Run with comprehensive context test
python dv.py tests/trigger_lifecycle_data.json --config tests/trigger_lifecycle_config.json
```

**Expected notifications:**
- **Startup**: "TUI Started - Loading: data.json (dataset size: 3)"
- **Navigate**: "Moved to row 1 (dataset size: 3, from data.json)"
- **Select**: "Selected row 1 (dataset size: 3, from data.json)"
- **Drill down** on `tasks[]`: "Level: tasks [drill-down] (depth 1, size 1, parent row 0)"
- **Backup**: "To level: projects (depth 0, size 3) from row 0 in tasks [drill-down]"

## Files Modified

| File | Lines Changed | Description |
|-------|---------------|-------------|
| `dv_tui/handlers.py` | ~5 | Added dataset_size, data_source, level_name, depth to _build_trigger_context() |
| `tests/trigger_lifecycle_config.json` | ~4 | Updated on_select and on_navigate_row to use dataset context |

## Benefits

1. **All triggers benefit** - Not just lifecycle events
2. **Dataset awareness** - Triggers know how big the current dataset is
3. **Source tracking** - Can identify which data file is being viewed
4. **Level awareness** - Can track depth and level names across all triggers
5. **Analytics ready** - Easy to build usage analytics with context
6. **Debugging support** - Full context available for troubleshooting

## Use Cases

- **Analytics**: Track which datasets are used most often
- **Performance**: Correlate navigation patterns with dataset sizes
- **Monitoring**: Send dataset information to external services
- **Debugging**: Know exactly what data context triggers are operating in
- **Logging**: Include dataset and source in all trigger logs

## Notes

- All standard triggers (`on_select`, `on_navigate_row`, `on_navigate_cell`, `on_enter`) now have dataset context
- `DV_DATASET_SIZE` is always available, not just in lifecycle triggers
- `DV_DATA_SOURCE` is the file path when loading from file, or inherited from drill-down
- `DV_LEVEL_NAME` and `DV_DEPTH` are set by drill-down logic in core.py
- Environment variable names follow consistent `DV_` prefix pattern
- Comprehensive context is backward compatible - existing configs still work

## Context Variable Summary

**Standard triggers (all get these 8 variables):**
- `DV_SELECTED_INDEX`, `DV_SELECTED_CELL`, `DV_SELECTED_ROW`, `DV_SELECTED_COLUMN`
- `DV_DATASET_SIZE`, `DV_DATA_SOURCE`
- `DV_LEVEL_NAME`, `DV_DEPTH`

**Lifecycle triggers (get 4 additional variables):**
- `DV_DATA_SOURCE` - via `on_startup`
- `DV_DRILL_LEVEL_NAME`, `DV_DRILL_DEPTH`, `DV_DATASET_SIZE`
- `DV_PARENT_LEVEL_INDEX`, `DV_PARENT_LEVEL_NAME`
- Plus all 8 standard variables

**Drill-down triggers (get 4 additional variables):**
- `DV_DRILL_LEVEL_NAME`, `DV_DRILL_DEPTH`, `DV_DATASET_SIZE`
- `DV_PARENT_LEVEL_INDEX`, `DV_PARENT_LEVEL_NAME`
- Plus all 8 standard variables

**Backup triggers (get 4 additional variables):**
- `DV_CURRENT_LEVEL_NAME`, `DV_CURRENT_DEPTH`, `DV_DATASET_SIZE`
- `DV_PREVIOUS_LEVEL_INDEX`, `DV_PREVIOUS_LEVEL_NAME`
- Plus all 8 standard variables
