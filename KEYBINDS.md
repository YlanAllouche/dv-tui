# KEYBINDS.md - Keyboard Shortcuts Guide

dv-tui provides a flexible keybinding system with Vim-inspired defaults. Keybindings can be customized via configuration files or CLI flags.

## Default Keybindings

### Normal Mode

Normal mode is the default mode for navigating and selecting rows.

| Key | Action | Description |
|-----|--------|-------------|
| `j` / `↓` | Move down | Navigate to next row |
| `k` / `↑` | Move up | Navigate to previous row |
| `h` / `←` | Previous tab | Switch to previous tab (or left cell in cell mode) |
| `l` / `→` | Next tab | Switch to next tab (or right cell in cell mode) |
| `/` | Enter search | Open search mode to filter rows |
| `c` | Toggle mode | Switch between row and cell selection mode |
| `Enter` | Select | Select current row/cell and trigger on_enter/on_select |
| `q` / `Q` | Quit | Exit dv-tui |
| `Esc` | Go back | Go back from drill-down navigation (if available) |
| `e` | Cycle enum next | Cycle to next enum value (cell mode with enum) |
| `E` | Cycle enum prev | Cycle to previous enum value (cell mode with enum) |
| `Ctrl+E` | Enum picker | Open enum picker dialog (cell mode with enum) |
| `;` | Leader key | Start leader key sequence for custom actions |

### Search Mode

Search mode allows fuzzy filtering of rows by typing.

| Key | Action | Description |
|-----|--------|-------------|
| Type | Filter | Add character to search query |
| `Tab` / `↓` | Next result | Navigate to next search result |
| `Shift+Tab` / `↑` | Previous result | Navigate to previous search result |
| `Enter` | Select | Select current search result and exit search |
| `Esc` | Exit search | Cancel search and return to previous position |
| `Backspace` | Delete | Remove last character from search query |

### Cell Mode

Cell mode allows navigating individual cells within rows. Press `c` in normal mode to toggle.

| Key | Action | Description |
|-----|--------|-------------|
| `j` / `↓` | Move down | Navigate to next row (same column) |
| `k` / `↑` | Move up | Navigate to previous row (same column) |
| `h` / `←` | Left cell | Navigate to previous column |
| `l` / `→` | Right cell | Navigate to next column |
| `/` | Enter search | Filter rows (stays in cell mode) |
| `c` | Toggle mode | Switch to row selection mode |
| `Enter` | Select | Select cell - drill if drillable, otherwise select row |
| `q` / `Q` | Quit | Exit dv-tui |
| `Esc` | Go back | Go back from drill-down navigation (if available) |
| `e` | Cycle enum next | Cycle to next enum value (if field has enum config) |
| `E` | Cycle enum prev | Cycle to previous enum value (if field has enum config) |
| `Ctrl+E` | Enum picker | Open enum picker dialog (if field has enum config) |

## Customizing Keybindings

### Via Config File

Edit `~/.config/dv/config.json` or use `--config` flag:

```json
{
  "keybinds": {
    "normal": {
      "down": [106, 74, 258],
      "up": [107, 75, 259],
      "quit": [113, 81]
    },
    "search": {
      "escape": 27
    }
  }
}
```

### Via CLI Flags

Add or override keybindings at runtime:

```bash
# Add keybinding
dv --bind "v:view_details" data.json

# Add keybinding for specific mode
dv --bind "search:g:goto_first" data.json

# Remove keybinding
dv --unbind "q" data.json

# Remove keybinding from specific mode
dv --unbind "search:q" data.json
```

### Keybinding Format

**For adding:**

- Single mode: `key:action`
- Specific mode: `mode:key:action`

Examples:
- `v:view_details` - Bind 'v' to 'view_details' in normal mode
- `search:Ctrl+r:refresh` - Bind 'Ctrl+r' to 'refresh' in search mode

**For removing:**

- Single mode: `key`
- Specific mode: `mode:key`

Examples:
- `q` - Unbind 'q' in normal mode
- `search:q` - Unbind 'q' in search mode

## Key Codes

Common key codes for configuration:

### Character Keys

| Key | Code | Key | Code |
|-----|------|-----|------|
| `a` | 97 | `A` | 65 |
| `q` | 113 | `Q` | 81 |
| `j` | 106 | `J` | 74 |
| `k` | 107 | `K` | 75 |
| `h` | 104 | `H` | 72 |
| `l` | 108 | `L` | 76 |
| `;` | 59 | `:` | 58 |
| `/` | 47 | `?` | 63 |
| `c` | 99 | `C` | 67 |
| `e` | 101 | `E` | 69 |
| `g` | 103 | `G` | 71 |

### Special Keys

| Key | Code | Description |
|-----|------|-------------|
| Enter | 10, 13 | Enter key |
| Esc | 27 | Escape key |
| Tab | 9 | Tab key |
| Backspace | 263, 127 | Backspace key |
| Space | 32 | Space key |

### Arrow Keys

| Key | Code | Description |
|-----|------|-------------|
| ↑ | 259 | Up arrow |
| ↓ | 258 | Down arrow |
| ← | 260 | Left arrow |
| → | 261 | Right arrow |

### Control Keys

Control keys are calculated as `ASCII code - 64`:

| Key | Code | Key | Code |
|-----|------|-----|------|
| Ctrl+A | 1 | Ctrl+A | 1 |
| Ctrl+C | 3 | Ctrl+C | 3 |
| Ctrl+E | 5 | Ctrl+E | 5 |
| Ctrl+P | 16 | Ctrl+P | 16 |

## Custom Actions

Custom actions can be defined using the triggers system. Actions are executed when keys are pressed.

### Defining Custom Actions

Custom actions are defined using the trigger system. Bind a key to a trigger name, then define the trigger in your configuration.

```json
{
  "binds": [
    {"key": "v", "action": "view_details", "mode": "normal"}
  ],
  "triggers": {
    "table": {
      "on_enter": "view_details.sh"
    }
  }
}
```

### Using Custom Actions

When the bound key is pressed, dv-tui will:

1. Execute the trigger with current selection context
2. Make environment variables available:
   - `DV_SELECTED_INDEX`: Index of selected row
   - `DV_SELECTED_ROW`: JSON of selected row
   - `DV_SELECTED_COLUMN`: Name of selected column (cell mode)
   - `DV_SELECTED_CELL`: Value of selected cell (cell mode)

### Example: View Details Action

```json
{
  "binds": [
    {"key": "v", "action": "view_details", "mode": "normal"}
  ],
  "triggers": {
    "table": {
      "on_enter": {
        "command": "view_details.sh",
        "async": true
      }
    }
  }
}
```

`view_details.sh`:

```bash
#!/bin/bash
echo "Selected row: $DV_SELECTED_ROW"
echo "Selected index: $DV_SELECTED_INDEX"
```

### Example: Custom Refresh Key

```json
{
  "binds": [
    {"key": "r", "action": "refresh", "mode": "normal"}
  ],
  "triggers": {
    "table": {
      "on_enter": "refresh_data.sh"
    }
  }
}
```

`refresh_data.sh`:

```bash
#!/bin/bash
# Regenerate data file
./fetch_data.sh > /tmp/data.json
```

### Example: Open Editor

```json
{
  "binds": [
    {"key": "o", "action": "open_editor", "mode": "normal"}
  ],
  "triggers": {
    "table": {
      "on_select": "open_editor.sh $DV_SELECTED_INDEX"
    }
  }
}
```

`open_editor.sh`:

```bash
#!/bin/bash
index=$1
# Use jq to get the file path from selected row
file=$(cat data.json | jq -r ".[$index].file")

if [ -n "$file" ] && [ -f "$file" ]; then
    vim "$file"
fi
```

## Mode-Specific Keybindings

Keybindings can be customized per mode:

### Normal Mode

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

### Search Mode

```json
{
  "keybinds": {
    "search": {
      "escape": 27,
      "enter": [10, 13]
    }
  }
}
```

### Cell Mode

```json
{
  "keybinds": {
    "cell": {
      "left": [104, 260],
      "right": [108, 261],
      "toggle_mode": 99
    }
  }
}
```

## Leader Key Sequences

The leader key (default: `;`) allows custom action sequences.

### Setting Leader Key

```json
{
  "keybinds": {
    "normal": {
      "leader": 59  ; Key code for ';'
    }
  }
}
```

### Using Leader Sequences

After pressing the leader key, you have a timeout (default: 0.5s) to press the next key. The combined sequence triggers a custom action.

Example configuration:

```json
{
  "binds": [
    {"key": ";q", "action": "quick_quit", "mode": "normal"}
  ]
}
```

In this example, pressing `;` then `q` quickly triggers the `quick_quit` action.

## Unbinding Keys

Keys can be unbound to disable default actions.

### Via Config File

```json
{
  "unbinds": [
    {"key": "q", "mode": "normal"},
    {"key": "Esc", "mode": "search"}
  ]
}
```

### Via CLI

```bash
# Unbind 'q' in normal mode
dv --unbind "q" data.json

# Unbind 'Esc' in search mode
dv --unbind "search:Esc" data.json
```

## Complete Configuration Example

```json
{
  "keybinds": {
    "normal": {
      "down": [106, 258],
      "up": [107, 259],
      "left": [104, 260],
      "right": [108, 261],
      "search": 47,
      "enter": [10, 13],
      "escape": 27,
      "backspace": [263, 127],
      "toggle_mode": 99,
      "enum_picker": 5,
      "enum_cycle_next": 101,
      "enum_cycle_prev": 69,
      "leader": 59
    },
    "search": {
      "enter": [10, 13],
      "escape": 27,
      "backspace": [263, 127],
      "tab": 9,
      "shift_tab": 353
    },
    "cell": {
      "down": [106, 258],
      "up": [107, 259],
      "left": [104, 260],
      "right": [108, 261],
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
  "binds": [
    {"key": "v", "action": "view_details", "mode": "normal"},
    {"key": "r", "action": "refresh", "mode": "normal"}
  ],
  "unbinds": [
    {"key": "q", "mode": "normal"}
  ]
}
```

## Tips

1. **Test keybindings**: Use `echo $'...'` to print key codes
   ```bash
   # Press a key to see its code
   read -sn 1 key; echo "Key code: $((key))"
   ```

2. **Leader key timeout**: Increase timeout for slower typing
   - Modify `leader_timeout_duration` in `handlers.py`

3. **Mode switching**: Remember that `h/l` behavior changes between normal and cell mode

4. **Search navigation**: Use `Tab` and `Shift+Tab` to quickly cycle through results

5. **Enum cycling**: In cell mode with enum configuration, use `e`/`E` for fast cycling
