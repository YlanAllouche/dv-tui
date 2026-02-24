# CONFIG.md - Configuration Guide

dv-tui provides a flexible configuration system that supports multiple sources and priority levels.

## Configuration Sources

Configuration is loaded from multiple sources in the following priority order (highest to lowest):

1. **CLI flags** - Command-line arguments (e.g., `--columns`, `--bind`)
2. **Inline JSON** - Configuration embedded in data file via `_config` field
3. **Config file** - `~/.config/dv/config.json` or custom path via `--config`
4. **Defaults** - Built-in default configuration

## Configuration File Location

Default configuration file: `~/.config/dv/config.json`

Custom configuration file:

```bash
dv --config /path/to/config.json
```

## Full Configuration Schema

```json
{
  "columns": ["type", "status", "summary"],
  "column_widths": {
    "type": 8,
    "status": 12,
    "summary": null
  },
  "tab_name": "Custom Tab Name",
  "keybinds": {
    "normal": {
      "leader": 59,
      "quit": [113, 81],
      "down": [106, 74, 258],
      "up": [107, 75, 259],
      "left": [104, 72, 260],
      "right": [108, 76, 261],
      "search": 47,
      "enter": [10, 13],
      "escape": 27,
      "backspace": [263, 127],
      "toggle_mode": 99,
      "enum_picker": 5,
      "enum_cycle_next": 101,
      "enum_cycle_prev": 69
    },
    "search": {
      "enter": [10, 13],
      "escape": 27,
      "backspace": [263, 127],
      "tab": 9,
      "shift_tab": 353
    },
    "cell": {
      "leader": 59,
      "quit": [113, 81],
      "down": [106, 74, 258],
      "up": [107, 75, 259],
      "left": [104, 72, 260],
      "right": [108, 76, 261],
      "search": 47,
      "enter": [10, 13],
      "escape": 27,
      "backspace": [263, 127],
      "toggle_mode": 99,
      "enum_picker": 5,
      "enum_cycle_next": 101,
      "enum_cycle_prev": 69
    }
  },
  "colors": {
    "type": {
      "work": [5, true],
      "study": [6, true]
    },
    "status": {
      "focus": [2, true],
      "active": [3, true]
    },
    "date": {
      "prefix": "2025-",
      "color": 4
    }
  },
  "triggers": {
    "table": {
      "on_enter": "echo $DV_SELECTED_ROW",
      "on_select": "open_file $DV_SELECTED_INDEX",
      "on_navigate_row": "log_navigation",
      "on_navigate_cell": "log_cell_navigation",
      "on_startup": "init_session",
      "on_drilldown": "handle_drilldown",
      "on_backup": "handle_backup",
      "data": "row",
      "async": true
    },
    "rows": {
      "0": {
        "on_enter": "handle_first_row",
        "data": "row"
      }
    },
    "cells": {
      "0:status": {
        "on_navigate_cell": "handle_status_cell",
        "data": "cell"
      }
    }
  },
  "enum": {
    "status": {
      "source": "inline",
      "values": ["todo", "in-progress", "done"],
      "command": null
    },
    "priority": {
      "source": "inferred"
    },
    "type": {
      "source": "external",
      "command": "get_types.sh"
    }
  },
  "drill_down": {
    "enabled": true,
    "field_name": "items",
    "inherit_flags": true,
    "extra_flags": [],
    "new_tab": false
  },
  "refresh": {
    "enabled": true,
    "on_trigger": false,
    "interval": 1.0,
    "command": "data_query.sh"
  },
  "tabs": ["file1.json", "file2.json"],
  "delimiter": ",",
  "skip_headers": false,
  "stdin_timeout": 30,
  "binds": [
    {"key": "v", "action": "view_details", "mode": "normal"}
  ],
  "unbinds": [
    {"key": "q", "mode": "normal"}
  ]
}
```

## Configuration Options

### columns

Array of column names to display and their order.

```json
{
  "columns": ["name", "status", "priority", "due_date"]
}
```

If not specified, columns are auto-detected from data keys.

### column_widths

Object mapping column names to fixed widths. Last column gets remaining space.

```json
{
  "column_widths": {
    "name": 20,
    "status": 12,
    "priority": null
  }
}
```

### tab_name

Custom name for the tab (displayed in tab bar).

```json
{
  "tab_name": "My Data"
}
```

### keybinds

Keybinding configuration for different modes. Keys are specified as integers (ASCII codes) or key names.

#### Key Codes

Common key codes:

- `q` / `Q`: 113 / 81
- `j` / `J`: 106 / 74
- `k` / `K`: 107 / 75
- `h` / `H`: 104 / 72
- `l` / `L`: 108 / 76
- `/`: 47
- `Enter`: 10, 13
- `Esc`: 27
- `Backspace`: 263, 127
- `Tab`: 9
- `Shift+Tab`: 353
- `↓` (Down arrow): 258
- `↑` (Up arrow): 259
- `←` (Left arrow): 260
- `→` (Right arrow): 261

#### Modes

- `normal`: Default mode for row navigation
- `search`: Search/filter mode
- `cell`: Cell navigation mode

#### Example

```json
{
  "keybinds": {
    "normal": {
      "down": [106, 258],
      "up": [107, 259],
      "quit": [113]
    }
  }
}
```

### colors

Color configuration for field values.

#### type

Color mapping for the `type` field.

```json
{
  "colors": {
    "type": {
      "work": [5, true],
      "study": [6, true],
      "personal": [7, false]
    }
  }
}
```

Format: `[color_pair_number, bold]`

Color pairs (initialized by curses):
- 1: Cyan
- 2: Magenta
- 3: Green
- 4: Yellow
- 5: Blue
- 6: Cyan (alternate)
- 7: White on Blue
- 8: Red

#### status

Color mapping for the `status` field.

```json
{
  "colors": {
    "status": {
      "focus": [2, true],
      "active": [3, true],
      "done": [8, false]
    }
  }
}
```

#### date

Special color for dates matching a prefix.

```json
{
  "colors": {
    "date": {
      "prefix": "2025-",
      "color": 4
    }
  }
}
```

### triggers

Event-based command execution system.

#### Trigger Types

- `on_enter`: Execute when Enter is pressed on row/cell
- `on_select`: Execute when a row/cell is selected
- `on_navigate_row`: Execute when moving between rows
- `on_navigate_cell`: Execute when moving between cells
- `on_startup`: Execute when TUI starts
- `on_drilldown`: Execute when drilling into nested data
- `on_backup`: Execute when going back from drill-down

#### Data Options

- `row`: Pass selected row as JSON to command (via `$DV_SELECTED_ROW`)
- `cell`: Pass selected cell value (via `$DV_SELECTED_CELL`)
- `table`: Pass entire table (via `$DV_TABLE`)

#### Async Execution

- `async: true`: Run command in background (default)
- `async: false`: Run command synchronously

#### Table-level Triggers

```json
{
  "triggers": {
    "table": {
      "on_enter": {
        "command": "handle_enter.sh",
        "async": true
      },
      "on_navigate_row": {
        "command": "log_row.sh",
        "async": false
      }
    }
  }
}
```

#### Row-level Triggers

Execute triggers for specific rows by index (0-based).

```json
{
  "triggers": {
    "rows": {
      "0": {
        "on_enter": "handle_first_row.sh"
      },
      "5": {
        "on_select": "handle_sixth_row.sh"
      }
    }
  }
}
```

#### Cell-level Triggers

Execute triggers for specific cells using `row_index:field_name` format.

```json
{
  "triggers": {
    "cells": {
      "0:status": {
        "on_navigate_cell": "handle_status_cell.sh"
      },
      "5:priority": {
        "on_enter": "handle_priority_cell.sh"
      }
    }
  }
}
```

### enum

Enum configuration for dropdown selection in cell mode.

#### Source Types

- `inline`: Pre-defined list of values
- `inferred`: Extract unique values from data
- `external`: Get values from command output

#### inline Source

```json
{
  "enum": {
    "status": {
      "source": "inline",
      "values": ["todo", "in-progress", "done"]
    }
  }
}
```

#### inferred Source

```json
{
  "enum": {
    "priority": {
      "source": "inferred"
    }
  }
}
```

#### external Source

```json
{
  "enum": {
    "category": {
      "source": "external",
      "command": "get_categories.sh"
    }
  }
}
```

### drill_down

Configuration for navigating into nested data.

```json
{
  "drill_down": {
    "enabled": true,
    "field_name": "items",
    "inherit_flags": true,
    "extra_flags": [],
    "new_tab": false
  }
}
```

- `enabled`: Enable drill-down (default: false)
- `field_name`: Specific field to drill into (optional)
- `inherit_flags`: Inherit flags from parent (default: true)
- `extra_flags`: Additional flags for drill-down (array)
- `new_tab`: Create new tab for drill-down (default: false)

### refresh

Auto-refresh configuration.

```json
{
  "refresh": {
    "enabled": true,
    "on_trigger": false,
    "interval": 1.0,
    "command": "fetch_data.sh"
  }
}
```

- `enabled`: Enable auto-refresh (default: false)
- `on_trigger`: Refresh on trigger events (default: false)
- `interval`: Refresh interval in seconds (default: 1.0)
- `command`: Command to regenerate data

### tabs

Array of file paths to open as tabs.

```json
{
  "tabs": ["data/tasks.json", "data/projects.json"]
}
```

### delimiter

Delimiter for CSV files (default: `,`).

```json
{
  "delimiter": ";"
}
```

### skip_headers

Skip first row as headers for CSV files (default: false).

```json
{
  "skip_headers": true
}
```

### stdin_timeout

Timeout for stdin input in seconds (default: 30). Use 0 for no timeout.

```json
{
  "stdin_timeout": 60
}
```

### binds

Add or override keybindings.

```json
{
  "binds": [
    {"key": "v", "action": "view_details", "mode": "normal"},
    {"key": "g", "action": "go_top", "mode": "normal"}
  ]
}
```

### unbinds

Remove keybindings.

```json
{
  "unbinds": [
    {"key": "q", "mode": "normal"}
  ]
}
```

## Configuration Examples

### Basic Configuration

```json
{
  "columns": ["name", "status", "priority"],
  "colors": {
    "status": {
      "high": [8, true],
      "medium": [4, true],
      "low": [5, false]
    }
  }
}
```

### Trigger Configuration

```json
{
  "triggers": {
    "table": {
      "on_enter": "handle_selection.sh",
      "on_select": "open_editor.sh $DV_SELECTED_INDEX"
    },
    "rows": {
      "0": {
        "on_enter": "special_first_row.sh"
      }
    }
  }
}
```

### Enum Configuration

```json
{
  "enum": {
    "status": {
      "source": "inline",
      "values": ["todo", "in-progress", "review", "done"]
    },
    "priority": {
      "source": "external",
      "command": "get_priorities.sh"
    }
  }
}
```

### Complete Example

```json
{
  "columns": ["name", "status", "priority", "due_date"],
  "column_widths": {
    "name": 20,
    "status": 12,
    "priority": 10
  },
  "tab_name": "Tasks",
  "colors": {
    "status": {
      "todo": [8, true],
      "in-progress": [4, true],
      "done": [3, true]
    },
    "priority": {
      "high": [8, true],
      "medium": [4, true],
      "low": [5, false]
    }
  },
  "enum": {
    "status": {
      "source": "inline",
      "values": ["todo", "in-progress", "done"]
    },
    "priority": {
      "source": "inline",
      "values": ["high", "medium", "low"]
    }
  },
  "drill_down": {
    "enabled": true,
    "new_tab": false
  },
  "refresh": {
    "enabled": true,
    "interval": 5.0,
    "command": "get_tasks.sh"
  },
  "triggers": {
    "table": {
      "on_enter": {
        "command": "echo $DV_SELECTED_ROW",
        "async": false
      },
      "on_select": "open_task.sh $DV_SELECTED_INDEX"
    }
  },
  "binds": [
    {"key": "r", "action": "refresh", "mode": "normal"}
  ]
}
```

## Inline Configuration

Configuration can be embedded in data files via the `_config` field in the first item:

```json
[
  {
    "_config": {
      "columns": ["name", "status"],
      "colors": {
        "status": {
          "active": [3, true],
          "inactive": [8, true]
        }
      }
    }
  },
  {"name": "Task 1", "status": "active"},
  {"name": "Task 2", "status": "inactive"}
]
```

## CLI Override

Configuration can be overridden via CLI flags:

```bash
# Override columns
dv --columns "name,status,priority" data.json

# Add keybinding
dv --bind "v:view_details" data.json

# Remove keybinding
dv --unbind "q" data.json

# Custom config file
dv --config /path/to/custom_config.json data.json
```
