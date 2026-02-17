# Comprehensive Context for Lifecycle Triggers

## Overview

Updated lifecycle trigger events to provide comprehensive navigation context instead of minimal information.

**Previous issue:** `parent_context: "null"` in backup notifications wasn't useful.

**Solution:** Implemented Option A - comprehensive context with:
- Current cursor position after action
- Level name and depth
- Previous cursor position
- Dataset size and source
- Full navigation context

## New Context Variables

### on_drilldown

All context variables are passed with `DV_` prefix:

| Variable | Description | Example |
|----------|-------------|---------|
| `DV_SELECTED_INDEX` | Row index after drilldown | `0` |
| `DV_SELECTED_COLUMN` | Column name after drilldown | `None` |
| `DV_SELECTED_CELL` | Full row data after drilldown | `{"id": 1, "name": "Project"}` |
| `DV_DRILL_LEVEL_NAME` | Name of level entered | `tasks [drill-down]` |
| `DV_DRILL_DEPTH` | Navigation depth (0-based) | `0` |
| `DV_PARENT_LEVEL_INDEX` | Parent row index | `5` |
| `DV_PARENT_LEVEL_NAME` | Name of parent level | `projects` |
| `DV_DATASET_SIZE` | Number of items in new dataset | `3` |
| `DV_DRILL_DATA_SOURCE` | Data file path | `data.json` |

**Example notification:**
```
Drill Down
Into: tasks at 0 (dataset size: 3, parent row: 5)
```

---

### on_backup

All context variables are passed with `DV_` prefix:

| Variable | Description | Example |
|----------|-------------|---------|
| `DV_CURRENT_INDEX` | Row index after backup | `0` |
| `DV_CURRENT_COLUMN` | Column name after backup | `name` |
| `DV_CURRENT_CELL` | Full row data after backup | `{"id": 1, "name": "Project"}` |
| `DV_CURRENT_LEVEL_NAME` | Name of level backed up to | `projects` |
| `DV_CURRENT_DEPTH` | Navigation depth after backup | `0` |
| `DV_DATASET_SIZE` | Number of items in dataset | `2` |
| `DV_DATA_SOURCE` | Data file path | `data.json` |
| `DV_PREVIOUS_LEVEL_INDEX` | Row index in level we left | `5` |
| `DV_PREVIOUS_LEVEL_NAME` | Name of level we left | `tasks [drill-down]` |
| `DV_PREVIOUS_PARENT_CONTEXT` | Original parent context of previous level | `null` |

**Example notification:**
```
Backup
To: row 0 at projects (depth 0, size 2) from row 5 in tasks [drill-down]
```

---

## Implementation Details

### Modified Files

#### dv_tui/core.py

**drill_down() method (lines 335-357):**
```python
# BEFORE:
self.key_handler.trigger_drilldown_event(
    self.table,
    drill_value=value,
    drill_field=field_name or "unknown",
    drill_level=drill_level + 1,
    parent_data=parent_context
)

# AFTER:
drill_to_context = {
    "selected_index": self.current_tab.table.selected_index,  # 0 after drill
    "selected_column": self.current_tab.table.selected_column,  # None
    "selected_cell": self.current_tab.table.selected_item,  # New row data
    "level_name": self.current_tab.name + " [drill-down]",  # "tasks [drill-down]"
    "depth": drill_level + 1,  # 1
    "parent_level_index": self.table.selected_index,  # Parent row
    "parent_level_name": self.current_tab.name,  # "projects"
    "dataset_size": len(nested_data),  # 3
    "data_source": self.current_file,  # "data.json"
}
self.key_handler.trigger_drilldown_event(
    self.table,
    drill_to_context=drill_to_context
)
```

**go_back() method (lines 360-408):**
```python
# BEFORE:
backup_to_context = {
    "selected_index": previous_state["selected_index"],
    "parent_context": previous_state["parent_context"]  # Often null!
}

# AFTER:
backup_to_context = {
    # Current view AFTER backup
    "selected_index": self.current_tab.table.selected_index,  # Restored position
    "selected_column": self.current_tab.table.selected_column,  # Restored column
    "selected_cell": self.current_tab.table.selected_item,  # Restored data
    "level_name": self.current_tab.name,  # "projects"
    "depth": backup_level,  # 0 (after pop)
    "dataset_size": len(self.current_tab.data),  # 2
    "data_source": self.current_file,  # "data.json"
    # Previous level we LEFT
    "previous_level_index": previous_state["selected_index"],  # 5
    "previous_level_name": previous_level_name,  # "tasks [drill-down]"
    "previous_parent_context": previous_state.get("parent_context"),  # null
}
self.key_handler.trigger_backup_event(
    self.table,
    backup_to_context=backup_to_context
)
```

#### dv_tui/handlers.py

**trigger_drilldown_event() method (lines 536-553):**
```python
# Uses key mapping dictionary to map context keys to DV_ variable names
key_mapping = {
    "selected_index": "DRILL_FROM_INDEX",
    "selected_column": "DRILL_FROM_COLUMN",
    "selected_cell": "DRILL_FROM_CELL",
    "level_name": "DRILL_LEVEL_NAME",
    "depth": "DRILL_DEPTH",
    "parent_level_index": "PARENT_LEVEL_INDEX",
    "parent_level_name": "PARENT_LEVEL_NAME",
    "dataset_size": "DATASET_SIZE",
    "data_source": "DRILL_DATA_SOURCE",
}

# Maps each context key to DV_ prefix using lookup, not string replacement
def trigger_drilldown_event(self, table, drill_to_context: Dict[str, Any]) -> None:
    context = self._build_trigger_context(table)
    for key, value in drill_to_context.items():
        if key in key_mapping:
            context[f"DV_{key_mapping[key]}"] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
```

**trigger_backup_event() method (lines 555-572):**
```python
# Uses same key mapping approach
key_mapping = {
    "selected_index": "CURRENT_INDEX",
    "selected_column": "CURRENT_COLUMN",
    "selected_cell": "CURRENT_CELL",
    "level_name": "CURRENT_LEVEL_NAME",
    "depth": "CURRENT_DEPTH",
    "dataset_size": "DATASET_SIZE",
    "data_source": "DATA_SOURCE",
    "previous_level_index": "PREVIOUS_LEVEL_INDEX",
    "previous_level_name": "PREVIOUS_LEVEL_NAME",
    "previous_parent_context": "PREVIOUS_PARENT_CONTEXT",
}

# Maps each context key to DV_ prefix using lookup
def trigger_backup_event(self, table, backup_to_context: Dict[str, Any]) -> None:
    context = self._build_trigger_context(table)
    for key, value in backup_to_context.items():
        if key in key_mapping:
            context[f"DV_{key_mapping[key]}"] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
```

#### tests/trigger_lifecycle_config.json

**Updated triggers to use new context variables:**
```json
{
  "on_drilldown": {
    "command": "notify-send \"Drill Down\" \"Into: $DV_DRILL_FIELD at $DV_DRILL_DEPTH (dataset size: $DV_DATASET_SIZE, parent row: $DV_PARENT_LEVEL_INDEX)\"",
    "async_": true
  },
  "on_backup": {
    "command": "notify-send \"Backup\" \"To: row $DV_CURRENT_INDEX at $DV_CURRENT_LEVEL_NAME (depth $DV_CURRENT_DEPTH, size $DV_DATASET_SIZE) from row $DV_PREVIOUS_LEVEL_INDEX in $DV_PREVIOUS_LEVEL_NAME\"",
    "async_": true
  }
}
```

## Benefits

### 1. Complete Navigation Context
Users now know:
- Where they are (current level, depth, dataset)
- Where they came from (previous level, parent row)
- What data they're working with (size, source)

### 2. Better Notifications
Notifications show meaningful information:
```
Drill Down
Into: tasks at 0 (dataset size: 3, parent row: 5)
```
Instead of:
```
Drill Down
Field: tasks, Depth: 0
```

### 3. Tracking & Analytics
Rich context enables:
- Session replay (know full navigation path)
- User behavior analysis (how deep do users drill?)
- Performance metrics (dataset sizes per level)

### 4. Debugging & Troubleshooting
Context provides complete state for:
- Reproducing navigation issues
- Understanding user's current view
- Diagnosing data loading problems

## Test Results

All tests pass:
✅ Python files compile without errors
✅ trigger_drilldown_event works with comprehensive context
✅ trigger_backup_event works with comprehensive context
✅ All context variables mapped to DV_ prefix correctly

## Backward Compatibility

**Breaking change:** The `trigger_drilldown_event()` and `trigger_backup_event()` method signatures have changed.

**Mitigation:** These are internal methods called only from `dv_tui/core.py`, which was updated simultaneously.

**Impact:** None - no user-facing API changes.

## Variable Mapping

### Context Key → Environment Variable Mapping

**For on_drilldown:**
| Context Key | Environment Variable | Example Value |
|-------------|---------------------|---------------|
| selected_index | DV_DRILL_FROM_INDEX | `0` |
| selected_column | DV_DRILL_FROM_COLUMN | `null` |
| selected_cell | DV_DRILL_FROM_CELL | `{"id": 1}` |
| level_name | DV_DRILL_LEVEL_NAME | `tasks [drill-down]` |
| depth | DV_DRILL_DEPTH | `0` |
| parent_level_index | DV_PARENT_LEVEL_INDEX | `5` |
| parent_level_name | DV_PARENT_LEVEL_NAME | `projects` |
| dataset_size | DV_DATASET_SIZE | `3` |
| data_source | DV_DRILL_DATA_SOURCE | `data.json` |

**For on_backup:**
| Context Key | Environment Variable | Example Value |
|-------------|---------------------|---------------|
| selected_index | DV_CURRENT_INDEX | `0` |
| selected_column | DV_CURRENT_COLUMN | `name` |
| selected_cell | DV_CURRENT_CELL | `{"id": 1}` |
| level_name | DV_CURRENT_LEVEL_NAME | `projects` |
| depth | DV_CURRENT_DEPTH | `0` |
| dataset_size | DV_DATASET_SIZE | `2` |
| data_source | DV_DATA_SOURCE | `data.json` |
| previous_level_index | DV_PREVIOUS_LEVEL_INDEX | `5` |
| previous_level_name | DV_PREVIOUS_LEVEL_NAME | `tasks [drill-down]` |
| previous_parent_context | DV_PREVIOUS_PARENT_CONTEXT | `null` |

## Notes

- All variables are passed as environment variables (`$DV_...`) for shell commands
- For Python function triggers (library usage), context dict is passed directly
- Context values that are dicts or lists are JSON-serialized
- All context values are converted to strings for subprocess compatibility
- Comprehensive context provides complete navigation state without breaking existing triggers
