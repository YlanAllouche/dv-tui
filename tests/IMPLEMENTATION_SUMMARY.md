# Implementation Summary: Lifecycle Triggers

## Overview

Added three new trigger events to dv-tui that fire at key points in the TUI lifecycle:
- `on_startup` - Fires when TUI loads (once per session)
- `on_drilldown` - Fires when drilling down into nested data
- `on_backup` - Fires when backing up from drill-down level

All events are available at table/row/cell levels and default to async (non-blocking) execution.

## Files Modified

### 1. dv_tui/config.py

**Changes:**
- Added three new fields to `TriggerConfig` dataclass:
  - `on_startup: Optional[Union[str, Dict[str, Any]]] = None`
  - `on_drilldown: Optional[Union[str, Dict[str, Any]]] = None`
  - `on_backup: Optional[Union[str, Dict[str, Any]]] = None`
- Updated `CONFIG_SCHEMA` to include new events in `table`, `rows`, and `cells` sections
- Updated `Config.to_dict()` method to serialize new events
- Updated `load_config()` to parse these events from JSON config

**Lines modified:**
- 468-473: Added new fields to TriggerConfig dataclass
- 119-131: Added on_startup schema for table triggers
- 141-158: Added on_drilldown and on_backup schema for table triggers
- 199-227: Added new event schemas for rows triggers
- 268-295: Added new event schemas for cells triggers
- 554-577: Updated to_dict() to include new events
- 774-805: Updated load_config() to parse new events

### 2. dv_tui/handlers.py

**Changes:**
- Added `import json` to support JSON serialization in trigger context
- Updated `_load_triggers()` to load new events for all three levels (table/row/cell)
- Added three new trigger helper methods:
  - `trigger_startup_event(table, data_source, config_file)` - Execute on_startup trigger
  - `trigger_drilldown_event(table, drill_value, drill_field, drill_level, parent_data)` - Execute on_drilldown trigger
  - `trigger_backup_event(table, backup_level, backup_to_context)` - Execute on_backup trigger

**Lines modified:**
- 3: Added `import json`
- 210-237: Updated _load_triggers() to include new events for table
- 224-234: Updated _load_triggers() to include new events for rows
- 241-259: Updated _load_triggers() to include new events for cells
- 514-548: Added three new trigger helper methods

### 3. dv_tui/core.py

**Changes:**
- In `run()` method: Call `trigger_startup_event()` after `load_data()` completes
- In `drill_down()` method: Call `trigger_drilldown_event()` after successfully drilling down
- In `go_back()` method: Call `trigger_backup_event()` after successfully backing up

**Lines modified:**
- 552-565: Added startup trigger call in run()
- 342-351: Added drilldown trigger call in drill_down()
- 383-399: Added backup trigger call in go_back()

### 4. dv_tui/triggers.py

**Changes:**
- Updated docstring to include new events in the events list
- Updated `_build_environment()` method to dynamically add ALL context variables starting with `DV_` prefix

**Lines modified:**
- 209: Updated events docstring
- 159-181: Updated `_build_environment()` to handle all `DV_` prefixed context variables

### Critical Fix: Context Variables

**Problem:** Lifecycle triggers were firing but not receiving their context variables (`DV_DATA_SOURCE`, `DV_DRILL_DEPTH`, etc.)

**Solution:** Updated `_build_environment()` to dynamically add all context variables starting with `DV_` prefix to environment

**Before:** Only 4 hardcoded standard variables were set
**After:** Any `DV_` prefixed context variable is automatically available as environment variable

See `tests/CONTEXT_VARS_FIX.md` for detailed explanation of the fix.

## Files Created

### 1. tests/trigger_lifecycle_data.json
Test data with nested structures for testing drill-down/backup:
- Row 0: Project with nested `tasks` array
- Row 1: Project with nested `settings` object
- Row 2: Project with nested `tags` array

### 2. tests/trigger_lifecycle_config.json
Configuration with all lifecycle triggers:
- `on_startup`: Notify on TUI start with data source
- `on_drilldown`: Notify on drill-down with field and depth
- `on_backup`: Notify on backup with level and context
- `on_select`: Notify on row selection (for comparison)
- `on_navigate_row`: Notify on row navigation (for comparison)

### 3. tests/test_trigger_lifecycle.sh
Automated test script that:
- Explains what the test demonstrates
- Shows expected behavior
- Runs dv-tui with test data and config
- Provides user guidance

### 4. tests/LIFECYCLE_TRIGGERS.md
Comprehensive documentation covering:
- Event descriptions and when they fire
- All available context variables for each event
- Trigger priority system (cell > row > table)
- Real-world examples
- Testing guide
- Migration guide from `on_enter`

### 5. tests/LIFECYCLE_README.md
Quick start guide including:
- What's new
- Quick test command
- Test scenario with step-by-step instructions
- Context variable reference
- File documentation

## New Context Variables

### on_startup
**Standard:**
- `DV_SELECTED_CELL`, `DV_SELECTED_ROW`, `DV_SELECTED_INDEX`, `DV_SELECTED_COLUMN`

**Lifecycle-specific:**
- `DV_DATA_SOURCE` - Path to data file
- `DV_CONFIG_FILE` - Path to config file

### on_drilldown
**Standard:**
- All standard variables

**Lifecycle-specific:**
- `DV_DRILL_DEPTH` - Current drill depth (0, 1, 2...)
- `DV_DRILL_FIELD` - Field name being drilled into
- `DV_DRILL_VALUE` - JSON string of drilled value
- `DV_PARENT_DATA` - JSON string of parent row data

### on_backup
**Standard:**
- All standard variables (for restored view)

**Lifecycle-specific:**
- `DV_BACKUP_DEPTH` - Depth after backing up (stack size)
- `DV_BACKUP_TO` - JSON string of backed-up context

## Behavior

### on_startup
- Fires once when TUI starts and loads initial data
- Does NOT fire when switching tabs
- Does NOT fire when reloading data
- Default: async_=true (non-blocking)

### on_drilldown
- Fires when pressing Enter on drillable cell (arrays `[]` or objects `{}`)
- Does NOT fire when switching tabs
- Fires each time you drill deeper
- Depth starts at 0, increments with each drill
- Default: async_=true (non-blocking)

### on_backup
- Fires when pressing ESC to back up from drill-down level
- Only fires if navigation stack has items
- Fires each time you go back one level
- Default: async_=true (non-blocking)

## Testing

### Verification Tests

All tests passed:
✅ Config schema validation includes new events
✅ TriggerConfig dataclass has new fields
✅ Config loading parses new events correctly
✅ Trigger manager loads new events for all levels
✅ All trigger methods execute correctly
✅ Python files compile without syntax errors

### Manual Testing

To test manually:

```bash
# Run automated test script
./tests/test_trigger_lifecycle.sh

# Or run manually
python dv.py tests/trigger_lifecycle_data.json --config tests/trigger_lifecycle_config.json
```

**Expected behavior:**
1. "TUI Started" notification on startup (with data source)
2. Press 'c', navigate to tasks[], press Enter → "Drill Down" notification
3. Press ESC → "Backup" notification
4. Press 'c', navigate to settings{}, press Enter → "Drill Down" notification
5. Press ESC → "Backup" notification

## Priority System

All three new events follow the existing priority system:

1. **Cell trigger** - If cell-specific trigger exists for selected cell
2. **Row trigger** - If row-specific trigger exists for selected row
3. **Table trigger** - Default/fallback trigger

Example configuration demonstrating priority:

```json
{
  "triggers": {
    "table": {
      "on_drilldown": {
        "command": "notify-send \"Table: Drilled down\"",
        "async_": true
      }
    },
    "rows": {
      "0": {
        "on_drilldown": {
          "command": "notify-send \"Row 0: Drilled down\"",
          "async_": true
        }
      }
    },
    "cells": {
      "0:tasks": {
        "on_drilldown": {
          "command": "notify-send \"Cell (0, tasks): Drilled down\"",
          "async_": true
        }
      }
    }
  }
}
```

**Result:**
- Drill on row 0, column "tasks" → Cell trigger fires
- Drill on row 0, other columns → Row trigger fires
- Drill on row 1+, any column → Table trigger fires

## Notes

- All lifecycle triggers default to async_=true (non-blocking)
- All triggers follow cell > row > table priority
- Context variables are passed as environment variables for shell commands
- For Python function triggers (library usage), context is passed as a dict
- The `on_enter` event still exists and fires when pressing Enter key
- `on_startup` is NOT a replacement for `on_enter`, they serve different purposes

## Next Steps

The implementation is complete and ready for testing. Consider:

1. Run the test script to verify all events fire correctly
2. Test with different data structures (nested arrays, objects, mixed)
3. Test priority system by defining triggers at multiple levels
4. Test edge cases (empty drill-down, backup at top level)
5. Update documentation in main README if needed
