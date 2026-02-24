# dv-tui

Terminal UI for browsing and filtering JSON/CSV data with keyboard navigation.

![screenshot](./screen1.png)

## Overview

dv-tui (data viewer - terminal user interface) is a curses-based terminal UI for viewing and interacting with JSON and CSV data. It provides a fast, keyboard-driven interface for browsing, searching, and filtering structured data.

Key features include:

- **Multi-tab browsing** - Load multiple files and switch between tabs
- **Vim keybindings** - Navigate with j/k, h/l for tabs and cells
- **Fuzzy search** - Real-time filtering with smart character-distance scoring
- **Auto-reload** - Detects and reloads modified files
- **Color-coded display** - Dynamic color cycling for statuses and types
- **Type handling** - Supports string types and integer durations (shown as minutes)
- **Smart sanitization** - Cleans control characters and truncates long strings
- **Tab indicators** - Shows item counts; search mode shows filtered vs. total count
- **Multiple file formats** - Supports JSON and CSV data files
- **Drill-down navigation** - Navigate into nested lists and objects
- **Enum cell editing** - Cycle through pre-defined values in cells
- **Custom keybindings** - Configure keys via CLI or config file
- **Trigger system** - Execute commands on row/cell selection and navigation events

## Installation

### From PyPI

```bash
pip install dv-tui
```

### From Source

```bash
# Clone the repository
git clone https://github.com/YlanAllouche/dv-tui.git
cd dv-tui

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
dv --help
```

## Usage

### Command Line

Basic usage:

```bash
# View a JSON file
dv file.json

# View a CSV file
dv data.csv

# View multiple files as tabs
dv file1.json file2.json

# View data from stdin
cat data.json | dv

# View data from a command output
query.sh | dv
```

Single-select mode (exit after selecting):

```bash
dv -s file.json
```

Custom column display:

```bash
dv --columns "name,status,age" file.json
```

Auto-refresh from command:

```bash
dv -c "query.sh" --refresh --refresh-interval 5
```

### Tmux Integration

Use dv-tui as a tmux popup window:

```bash
bind-key e run-shell "tmux display-popup -w 90% -h 80% -E ~/.local/bin/dv -s ~/share/_tmp/query1.json"
```

### Interactive Selection

Prompt for file from directory:

```bash
# Interactive selection from ~/share/_tmp/
dv

# Custom directory
dv ~/data/*.json
```

## Configuration

dv-tui supports configuration through multiple sources:

1. **Config file**: `~/.config/dv/config.json` or custom path via `--config`
2. **Inline JSON**: Configuration embedded in first data item via `_config` field
3. **Command line**: Override via flags like `--columns`, `--bind`, etc.

Configuration priority: CLI flags > inline JSON > config file > defaults

For detailed configuration options, see [CONFIG.md](CONFIG.md).

## Keyboard Shortcuts

### Normal Mode

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `h` / `←` | Previous tab (or left cell in cell mode) |
| `l` / `→` | Next tab (or right cell in cell mode) |
| `/` | Enter search mode |
| `c` | Toggle row/cell selection mode |
| `Enter` | Select row/cell |
| `q` | Quit |

### Search Mode

| Key | Action |
|-----|--------|
| Type | Filter results |
| `Tab` / `↓` | Next result |
| `Shift+Tab` / `↑` | Previous result |
| `Esc` | Exit search (restores position) |
| `Backspace` | Delete search character |
| `Enter` | Select result |

### Cell Mode (with enum configuration)

| Key | Action |
|-----|--------|
| `e` | Cycle to next enum value |
| `E` | Cycle to previous enum value |
| `Ctrl+E` | Open enum picker dialog |

For detailed keybinding customization, see [KEYBINDS.md](KEYBINDS.md).

## Library Usage

dv-tui can be used as a Python library in your applications:

```python
from dv_tui import TableUI

data = [
    {"name": "Alice", "status": "active", "age": 30},
    {"name": "Bob", "status": "inactive", "age": 25},
]

# Create TUI
tui = TableUI(data)

# Handle selections
def on_enter(selected_row):
    print(f"Selected: {selected_row}")

tui.bind_key('Enter', on_enter)

# Run
selected = tui.run()
```

For detailed API documentation and examples, see [LIBRARY.md](LIBRARY.md).

## JSON Structure

dv-tui expects JSON data as an array of objects:

```json
[
  {
    "type": "work",
    "status": "active",
    "summary": "Task description",
    "file": "path/to/file",
    "line": 42,
    "locator": "url_or_id"
  }
]
```

### Special Fields

- `_config`: Embedded configuration (see [CONFIG.md](CONFIG.md))
- Any field with nested objects/arrays is drillable

## CSV Structure

CSV files are automatically converted to JSON objects:

```csv
name,status,age
Alice,active,30
Bob,inactive,25
```

## Advanced Features

### Drill-Down Navigation

Press `Enter` on cells containing arrays or nested objects to drill into them. Use `Esc` to go back.

### Enum Cell Editing

Configure enum fields to cycle through values:

```json
{
  "_config": {
    "enum": {
      "status": {
        "source": "inline",
        "values": ["todo", "in-progress", "done"]
      }
    }
  }
}
```

### Trigger System

Execute commands on events:

```json
{
  "_config": {
    "triggers": {
      "table": {
        "on_enter": "echo $DV_SELECTED_ROW | jq",
        "on_select": "open_file $DV_SELECTED_INDEX"
      }
    }
  }
}
```

### Custom Keybindings

Bind custom actions via config or CLI:

```bash
dv --bind "v:view_details"
```

## Examples

See the `examples/` directory for complete example scripts:

- `basic_library_usage.py` - Basic Python library usage
- `custom_keybindings.py` - Custom keybinding configuration
- `programmatic_updates.py` - Updating data programmatically

## Development

### Running Tests

```bash
pytest tests/
```

### Test Data

Sample test data is provided in `tests/data/`:

```bash
dv tests/data/work_tasks.json
dv tests/data/study_tasks.json
dv tests/data/mixed_tasks.csv
```

See `tests/data/README.md` for more testing examples.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT License - see LICENSE file for details
