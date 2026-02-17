# Lifecycle Triggers Documentation

## Overview

Lifecycle triggers are special events that fire at key points in the TUI lifecycle:

- **on_startup** - Fires when the TUI first loads (once per session)
- **on_drilldown** - Fires when drilling down into nested data structures
- **on_backup** - Fires when backing up from a drill-down level (ESC key)

These events are available at all three trigger levels: `table`, `rows`, and `cells`.

## on_startup

### When It Fires
- Only once when the TUI starts and loads initial data
- Does NOT fire when switching tabs
- Does NOT fire when reloading data

### Available Context Variables

**Standard variables:**
- `DV_SELECTED_CELL` - Value of selected cell (None on startup)
- `DV_SELECTED_ROW` - Full row data as JSON string
- `DV_SELECTED_INDEX` - Row index (0 on startup)
- `DV_SELECTED_COLUMN` - Column name (None on startup)

**Lifecycle-specific variables:**
- `DV_DATA_SOURCE` - Path to the data file being loaded
- `DV_CONFIG_FILE` - Path to the config file (if specified with `--config`)

### Example

```json
{
  "triggers": {
    "table": {
      "on_startup": {
        "command": "notify-send \"TUI Started\" \"Loading: $DV_DATA_SOURCE\"",
        "async_": true
      }
    }
  }
}
```

### Use Cases
- Log session start
- Initialize external services
- Load additional resources
- Send startup notifications
- Validate environment

---

## on_drilldown

### When It Fires
- When pressing Enter on a drillable cell (arrays `[]` or objects `{}`)
- Does NOT fire when switching tabs
- Fires each time you drill deeper into nested structures

### Available Context Variables

**Standard variables:**
- `DV_SELECTED_CELL` - Value of the cell being drilled into
- `DV_SELECTED_ROW` - Full row data as JSON string
- `DV_SELECTED_INDEX` - Row index of the drilled cell
- `DV_SELECTED_COLUMN` - Column name of the drilled cell

**Lifecycle-specific variables:**
- `DV_DRILL_DEPTH` - Current drill depth level (starts at 0, increments with each drill)
- `DV_DRILL_FIELD` - Name of the field being drilled into (e.g., "tasks", "settings")
- `DV_DRILL_VALUE` - JSON string representation of the value being drilled into
- `DV_PARENT_DATA` - JSON string of the parent row data (the row being drilled from)

### Example

```json
{
  "triggers": {
    "table": {
      "on_drilldown": {
        "command": "notify-send \"Drill Down\" \"Field: $DV_DRILL_FIELD, Depth: $DV_DRILL_DEPTH\"",
        "async_": true
      }
    }
  }
}
```

### Use Cases
- Track navigation depth for analytics
- Load related data when drilling into specific fields
- Update breadcrumbs or navigation history
- Trigger data enrichment APIs
- Log drill-down patterns

### Example Drill-Down Flow

```
Level 0: Projects table
  ↓ Press Enter on "tasks[]" (row 0)
Level 1: Tasks table (drill_depth=1, drill_field="tasks")
  ↓ Press Enter on "metadata{}" (row 1)
Level 2: Metadata table (drill_depth=2, drill_field="metadata")
  ↓ Press ESC to back up
Level 1: Tasks table (backup_level=1)
  ↓ Press ESC to back up
Level 0: Projects table (backup_level=0)
```

---

## on_backup

### When It Fires
- When pressing ESC to back up from a drill-down level
- Only fires if there's a previous level in the navigation stack
- Fires each time you go back one level

### Available Context Variables

**Standard variables:**
- `DV_SELECTED_CELL` - Value of selected cell in the restored view
- `DV_SELECTED_ROW` - Full row data as JSON string (in restored view)
- `DV_SELECTED_INDEX` - Row index (in restored view)
- `DV_SELECTED_COLUMN` - Column name (in restored view)

**Lifecycle-specific variables:**
- `DV_BACKUP_DEPTH` - Depth level after backing up (navigation stack size after pop)
- `DV_BACKUP_TO` - JSON string of the context we're backing up to, including:
  - `selected_index` - The selected index in the previous state
  - `parent_context` - The parent context of the previous state

### Example

```json
{
  "triggers": {
    "table": {
      "on_backup": {
        "command": "notify-send \"Backup\" \"From level $DV_BACKUP_DEPTH\"",
        "async_": true
      }
    }
  }
}
```

### Use Cases
- Track navigation patterns (drill-down vs backup)
- Clean up resources when exiting a level
- Restore UI state for previous level
- Log navigation history
- Implement breadcrumb updates

---

## Trigger Priority

Like all triggers, lifecycle triggers follow the priority system:

1. **Cell trigger** - If a cell-specific trigger exists for the selected cell
2. **Row trigger** - If a row-specific trigger exists for the selected row
3. **Table trigger** - Default/fallback trigger

### Example: Multiple Levels

```json
{
  "triggers": {
    "table": {
      "on_drilldown": {
        "command": "notify-send \"Table: Drilled down at $DV_DRILL_DEPTH\"",
        "async_": true
      }
    },
    "rows": {
      "0": {
        "on_drilldown": {
          "command": "notify-send \"Row 0: Special drill-down behavior\"",
          "async_": true
        }
      }
    },
    "cells": {
      "0:tasks": {
        "on_drilldown": {
          "command": "notify-send \"Cell (0, tasks): Custom drill-down\"",
          "async_": true
        }
      }
    }
  }
}
```

**Result:**
- Drilling down on row 0, column "tasks" → Cell trigger fires
- Drilling down on row 1, any column → Row trigger fires
- Drilling down on row 2+, any column → Table trigger fires

---

## Async Behavior

All lifecycle triggers default to `async_: true`, meaning they:
- Execute in the background without blocking the UI
- Don't wait for the command to complete
- Are suitable for notifications, logging, and non-critical operations

For synchronous (blocking) execution, set `"async_": false`:
```json
{
  "on_startup": {
    "command": "./setup.sh",
    "async_": false
  }
}
```

---

## Testing

### Quick Test

```bash
# Run the lifecycle trigger test script
./tests/test_trigger_lifecycle.sh

# Or run manually with test data
python dv.py tests/trigger_lifecycle_data.json --config tests/trigger_lifecycle_config.json
```

### Expected Behavior

1. **On startup**: "TUI Started" notification with data source path
2. **Navigate to row 0**, press 'c' to enter cell mode, navigate to `tasks[]`, press Enter:
   - "Drill Down" notification with field="tasks", depth=0
3. **Navigate in drilled-down view**, press ESC:
   - "Backup" notification with backup_level=0
4. **Navigate to row 1**, press 'c', navigate to `settings{}`, press Enter:
   - "Drill Down" notification with field="settings", depth=1
5. **Press ESC**:
   - "Backup" notification with backup_level=1

### Test Files

- `tests/trigger_lifecycle_data.json` - Test data with nested arrays and objects
- `tests/trigger_lifecycle_config.json` - Configuration with all lifecycle triggers
- `tests/test_trigger_lifecycle.sh` - Automated test script

---

## Real-World Examples

### Log Session Start

```json
{
  "triggers": {
    "table": {
      "on_startup": {
        "command": "echo \"$(date) - Session started: $DV_DATA_SOURCE\" >> ~/.dv_sessions.log",
        "async_": true
      }
    }
  }
}
```

### Track Navigation Depth for Analytics

```json
{
  "triggers": {
    "table": {
      "on_drilldown": {
        "command": "curl -X POST https://analytics.example.com/track \\
          -d '{\"event\": \"drill_down\", \"depth\": \"$DV_DRILL_DEPTH\", \"field\": \"$DV_DRILL_FIELD\"}'",
        "async_": true
      }
    }
  }
}
```

### Conditional Setup on Startup

```json
{
  "triggers": {
    "table": {
      "on_startup": {
        "command": "./check_setup.sh \"$DV_DATA_SOURCE\" || notify-send \"Setup Required\" \"Some dependencies missing\"",
        "async_": false
      }
    }
  }
}
```

### Clean Up on Backup

```json
{
  "triggers": {
    "table": {
      "on_backup": {
        "command": "./cleanup_level.sh \"$DV_BACKUP_DEPTH\"",
        "async_": true
      }
    }
  }
}
```

---

## Notes

- **on_startup** fires only once per TUI session, not per tab
- **on_drilldown** tracks navigation depth (0 = first level, 1 = second level, etc.)
- **on_backup** fires when backing up, not when going back to top level (stack empty)
- All lifecycle triggers use `async_: true` by default (non-blocking)
- The priority system (cell > row > table) applies to all lifecycle triggers
- Context variables are passed as strings, not as JSON objects
- Use environment variable expansion (`$DV_...`) for variables in shell commands
- Python function triggers (library usage) receive context as a dict, not env vars

---

## Migration Guide

If you were using `on_enter` for startup-like behavior:

**Old pattern:**
```json
{
  "triggers": {
    "table": {
      "on_enter": {
        "command": "./setup.sh"
      }
    }
  }
}
```

**New pattern:**
```json
{
  "triggers": {
    "table": {
      "on_startup": {
        "command": "./setup.sh"
      }
    }
  }
}
```

**Note:** `on_enter` still exists and fires when pressing Enter key. `on_startup` is a dedicated event for TUI initialization.
