# LIBRARY.md - Python API Reference

dv-tui provides a Python API for using it as a library in your applications.

## Installation

```bash
pip install dv-tui
```

## Quick Start

```python
from dv_tui import TableUI

data = [
    {"name": "Alice", "status": "active", "age": 30},
    {"name": "Bob", "status": "inactive", "age": 25},
]

tui = TableUI(data)
selected = tui.run()

print(f"Selected: {selected}")
```

## API Reference

### TableUI

The main class for using dv-tui as a Python library.

#### Constructor

```python
TableUI(data, columns=None, keybinds=None, enum_config=None)
```

Initialize TableUI with data.

**Parameters:**

- `data` (List[Dict[str, Any]]): List of dictionaries to display
- `columns` (Optional[List[str]]): Optional list of column names to display
- `keybinds` (Optional[Dict[str, Any]]): Optional keybindings dict (e.g., `{"normal": {"j": "custom_down"}}`)
- `enum_config` (Optional[Any]): Optional enum configuration for dropdowns

**Example:**

```python
from dv_tui import TableUI

data = [
    {"name": "Alice", "status": "active"},
    {"name": "Bob", "status": "inactive"},
]

tui = TableUI(data, columns=["name", "status"])
```

#### Methods

##### bind_key

```python
bind_key(key, handler)
```

Bind a key to a Python function.

**Parameters:**

- `key` (str): Key name (e.g., 'Enter', 'q', 'j', 'v')
- `handler` (Callable): Function that receives selected row data when key is pressed

**Example:**

```python
def handle_enter(selected_row):
    print(f"Selected: {selected_row}")

tui.bind_key('Enter', handle_enter)
```

##### bind_trigger

```python
bind_trigger(trigger_name, handler)
```

Bind a trigger event to a Python function.

**Parameters:**

- `trigger_name` (str): Trigger name (e.g., 'on_enter', 'on_select', 'on_navigate_row')
- `handler` (Callable): Function that receives event data when trigger fires

**Example:**

```python
def handle_startup(event_data):
    print(f"TUI started: {event_data}")

tui.bind_trigger('on_startup', handle_startup)
```

##### update_data

```python
update_data(data)
```

Update the data programmatically.

**Parameters:**

- `data` (List[Dict[str, Any]]): New list of dictionaries to display

**Example:**

```python
new_data = [
    {"name": "Charlie", "status": "active"},
]
tui.update_data(new_data)
```

##### on_quit

```python
on_quit(callback)
```

Set callback for when TUI exits.

**Parameters:**

- `callback` (Callable): Function to call when TUI exits (no parameters)

**Example:**

```python
def cleanup():
    print("Cleaning up...")

tui.on_quit(cleanup)
```

##### on_mode_change

```python
on_mode_change(callback)
```

Set callback for when selection mode changes.

**Parameters:**

- `callback` (Callable): Function that receives mode name when mode changes

**Example:**

```python
def mode_changed(mode):
    print(f"Mode changed to: {mode}")

tui.on_mode_change(mode_changed)
```

##### on_select

```python
on_select(callback)
```

Set callback for when a row is selected.

**Parameters:**

- `callback` (Callable): Function that receives selected row data

**Example:**

```python
def row_selected(row):
    print(f"Row selected: {row}")

tui.on_select(row_selected)
```

##### run

```python
run() -> Optional[Dict[str, Any]]
```

Start the TUI and run until user quits.

**Returns:**

- Selected item data if any, None otherwise

**Example:**

```python
selected = tui.run()
if selected:
    print(f"User selected: {selected}")
else:
    print("User quit without selection")
```

## Example Scripts

### Basic Usage

```python
#!/usr/bin/env python3
"""Basic example of using dv-tui as a library."""

from dv_tui import TableUI

data = [
    {"id": 1, "name": "Alice", "status": "active", "age": 30},
    {"id": 2, "name": "Bob", "status": "inactive", "age": 25},
    {"id": 3, "name": "Charlie", "status": "active", "age": 35},
]

def on_enter_handler(selected_row):
    """Handle Enter key press."""
    print(f"Selected: {selected_row}")
    
def on_quit_handler():
    """Handle TUI exit."""
    print("TUI exited!")

tui = TableUI(data)

tui.bind_key('Enter', on_enter_handler)
tui.on_quit(on_quit_handler)

selected = tui.run()

print(f"Final selection: {selected}")
```

### Custom Columns

```python
#!/usr/bin/env python3
"""Example with custom column ordering."""

from dv_tui import TableUI

data = [
    {"name": "Task 1", "priority": "high", "status": "todo", "assignee": "Alice"},
    {"name": "Task 2", "priority": "low", "status": "done", "assignee": "Bob"},
    {"name": "Task 3", "priority": "medium", "status": "in-progress", "assignee": "Charlie"},
]

tui = TableUI(data, columns=["name", "priority", "assignee", "status"])
selected = tui.run()
```

### Custom Keybindings

```python
#!/usr/bin/env python3
"""Example with custom keybindings."""

from dv_tui import TableUI

data = [
    {"id": 1, "name": "Alice", "status": "active"},
    {"id": 2, "name": "Bob", "status": "inactive"},
]

def view_details(row):
    """View details of selected row."""
    print(f"Details for {row['name']}:")
    print(f"  ID: {row['id']}")
    print(f"  Status: {row['status']}")

def refresh_data():
    """Refresh data (placeholder)."""
    print("Refreshing data...")

tui = TableUI(data)
tui.bind_key('v', view_details)
tui.bind_key('r', lambda _: refresh_data())

selected = tui.run()
```

### Triggers

```python
#!/usr/bin/env python3
"""Example using triggers."""

from dv_tui import TableUI

data = [
    {"id": 1, "name": "Task 1", "status": "todo"},
    {"id": 2, "name": "Task 2", "status": "done"},
]

def on_startup_handler(event_data):
    """Handle startup trigger."""
    print(f"TUI started with {len(data)} items")

def on_navigate_handler(event_data):
    """Handle navigation trigger."""
    print(f"Navigated to row {event_data.get('selected_index')}")

tui = TableUI(data)
tui.bind_trigger('on_startup', on_startup_handler)
tui.bind_trigger('on_navigate_row', on_navigate_handler)

selected = tui.run()
```

### Programmatic Updates

```python
#!/usr/bin/env python3
"""Example of updating data programmatically."""

from dv_tui import TableUI
import time

data = [
    {"id": 1, "name": "Task 1", "status": "todo"},
    {"id": 2, "name": "Task 2", "status": "done"},
]

def refresh_handler(_):
    """Handle refresh key press."""
    new_data = [
        {"id": 1, "name": "Task 1", "status": "done"},
        {"id": 2, "name": "Task 2", "status": "done"},
        {"id": 3, "name": "Task 3", "status": "todo"},
    ]
    tui.update_data(new_data)
    print("Data updated!")

tui = TableUI(data)
tui.bind_key('r', refresh_handler)

selected = tui.run()
```

### Mode Change Callback

```python
#!/usr/bin/env python3
"""Example handling mode changes."""

from dv_tui import TableUI

data = [
    {"id": 1, "name": "Alice", "status": "active"},
    {"id": 2, "name": "Bob", "status": "inactive"},
]

def mode_changed(mode):
    """Handle mode change."""
    print(f"Selection mode: {mode}")

tui = TableUI(data)
tui.on_mode_change(mode_changed)

selected = tui.run()
```

### Enum Configuration

```python
#!/usr/bin/env python3
"""Example with enum configuration for cell editing."""

from dv_tui import TableUI
from dv_tui.config import EnumConfig, EnumSourceConfig

data = [
    {"id": 1, "name": "Task 1", "status": "todo"},
    {"id": 2, "name": "Task 2", "status": "in-progress"},
    {"id": 3, "name": "Task 3", "status": "done"},
]

enum_config = EnumConfig()
enum_config.status = EnumSourceConfig(
    source="inline",
    values=["todo", "in-progress", "review", "done"]
)

tui = TableUI(data, enum_config=enum_config)
selected = tui.run()
```

### Loading from File

```python
#!/usr/bin/env python3
"""Example loading data from file."""

from dv_tui import TableUI
from dv_tui.data_loaders import load_file

data = load_file("tasks.json")

tui = TableUI(data)
selected = tui.run()
```

### Single-Select Mode

```python
#!/usr/bin/env python3
"""Example using single-select mode."""

from dv_tui import TableUI

data = [
    {"id": 1, "name": "Option A"},
    {"id": 2, "name": "Option B"},
    {"id": 3, "name": "Option C"},
]

tui = TableUI(data)
selected = tui.run()

if selected:
    print(f"User selected: {selected['name']}")
else:
    print("User cancelled selection")
```

## Common Patterns

### Selection Menu

Create a selection menu for user to choose from options:

```python
from dv_tui import TableUI

options = [
    {"id": 1, "action": "Create new file"},
    {"id": 2, "action": "Open existing file"},
    {"id": 3, "action": "Exit"},
]

tui = TableUI(options, columns=["action"])
selected = tui.run()

if selected:
    action_id = selected['id']
    print(f"User selected action ID: {action_id}")
```

### Data Browser

Browse and select items from a dataset:

```python
from dv_tui import TableUI

items = [
    {"name": "Item 1", "price": 10.99, "stock": 100},
    {"name": "Item 2", "price": 5.99, "stock": 50},
    {"name": "Item 3", "price": 2.99, "stock": 200},
]

def on_select(item):
    print(f"Viewing details for: {item['name']}")

tui = TableUI(items)
tui.on_select(on_select)
selected = tui.run()
```

### Configuration Selection

Allow user to select from multiple configurations:

```python
from dv_tui import TableUI

configs = [
    {"name": "Development", "env": "dev", "region": "us-east-1"},
    {"name": "Staging", "env": "staging", "region": "us-west-2"},
    {"name": "Production", "env": "prod", "region": "eu-west-1"},
]

tui = TableUI(configs, columns=["name", "env", "region"])
selected = tui.run()

if selected:
    print(f"Selected environment: {selected['name']} ({selected['env']})")
```

### Interactive Filter

Use dv-tui for interactive filtering:

```python
from dv_tui import TableUI

data = [
    {"name": "Alice", "role": "Developer", "level": "Senior"},
    {"name": "Bob", "role": "Designer", "level": "Junior"},
    {"name": "Charlie", "role": "Developer", "level": "Junior"},
]

tui = TableUI(data, columns=["name", "role", "level"])
selected = tui.run()

if selected:
    print(f"Filtered to: {selected['name']} - {selected['role']}")
```

### Refreshable Data

Create a TUI that can refresh data:

```python
from dv_tui import TableUI
import json

def fetch_data():
    """Fetch fresh data from API or file."""
    with open("data.json") as f:
        return json.load(f)

data = fetch_data()

def on_refresh(_):
    """Refresh data on key press."""
    global data
    data = fetch_data()
    tui.update_data(data)

tui = TableUI(data)
tui.bind_key('r', on_refresh)
selected = tui.run()
```

### Custom Actions

Add custom actions via key bindings:

```python
from dv_tui import TableUI
import subprocess

data = [
    {"name": "file1.txt", "path": "/path/to/file1.txt"},
    {"name": "file2.txt", "path": "/path/to/file2.txt"},
]

def open_file(row):
    """Open file in default editor."""
    subprocess.run(["vim", row['path']])

def delete_file(row):
    """Delete file with confirmation."""
    print(f"Deleting: {row['name']}")

tui = TableUI(data)
tui.bind_key('o', open_file)
tui.bind_key('d', delete_file)
selected = tui.run()
```

### Multi-Step Selection

Guide user through multiple selection steps:

```python
from dv_tui import TableUI

categories = [
    {"id": 1, "name": "Documents"},
    {"id": 2, "name": "Images"},
    {"id": 3, "name": "Videos"},
]

# Step 1: Select category
cat_tui = TableUI(categories, columns=["name"])
selected_cat = cat_tui.run()

if selected_cat:
    cat_name = selected_cat['name']
    print(f"Selected category: {cat_name}")
    
    # Step 2: Select items in category
    items = [
        {"name": f"{cat_name} Item 1"},
        {"name": f"{cat_name} Item 2"},
    ]
    
    item_tui = TableUI(items)
    selected_item = item_tui.run()
    
    if selected_item:
        print(f"Final selection: {selected_item['name']}")
```

## Advanced Usage

### Custom Configuration

Pass custom configuration to TableUI:

```python
from dv_tui import TableUI
from dv_tui.config import Config

config = Config()
config.columns = ["name", "status"]
config.enum = enum_config

data = [{"name": "Task", "status": "todo"}]
tui = TableUI(data)
```

### Integration with CLI

Combine library usage with CLI arguments:

```python
#!/usr/bin/env python3
import argparse
import json
from dv_tui import TableUI

def main():
    parser = argparse.ArgumentParser(description="Interactive data viewer")
    parser.add_argument("file", help="JSON file to view")
    parser.add_argument("--columns", help="Comma-separated column list")
    
    args = parser.parse_args()
    
    with open(args.file) as f:
        data = json.load(f)
    
    columns = args.columns.split(",") if args.columns else None
    tui = TableUI(data, columns=columns)
    selected = tui.run()
    
    if selected:
        print(json.dumps(selected, indent=2))

if __name__ == "__main__":
    main()
```

## Tips

1. **Always handle quit**: Set up `on_quit` callback for cleanup
2. **Use type hints**: Python type hints help with IDE autocomplete
3. **Test interactions**: Test keybindings and callbacks before deploying
4. **Handle empty data**: Check if data is empty before creating TUI
5. **Validate inputs**: Validate data structure before passing to TableUI
6. **Use try/except**: Wrap `tui.run()` in try/except for error handling
7. **Clean up resources**: Use `on_quit` callback to clean up resources

## Troubleshooting

### Import Errors

```bash
# If import fails, ensure dv-tui is installed
pip install dv-tui

# Or install in development mode
pip install -e /path/to/dv-tui
```

### Terminal Issues

If curses doesn't work:

- Ensure terminal supports colors
- Check TERM environment variable: `echo $TERM`
- Try a different terminal (gnome-terminal, xterm, etc.)

### Data Not Displaying

If data doesn't display:

- Check data is a list of dictionaries
- Verify column names match dictionary keys
- Ensure data is not empty

### Keybindings Not Working

If custom keybindings don't work:

- Verify key names are correct (case-sensitive)
- Check for conflicts with default keybindings
- Use integer key codes for special keys
