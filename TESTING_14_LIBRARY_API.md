# Testing 14-Library-API: Python Library API

This document provides instructions for manually testing the Python Library API implementation.

## Overview

The TableUI class provides a high-level API for using dv-tui as a Python library, allowing programmatic integration with your applications.

## Test Data

### Sample JSON Data

Create a file `test_data.json`:

```json
[
  {
    "id": 1,
    "name": "Alice",
    "status": "active",
    "age": 30,
    "department": "Engineering"
  },
  {
    "id": 2,
    "name": "Bob",
    "status": "inactive",
    "age": 25,
    "department": "Sales"
  },
  {
    "id": 3,
    "name": "Charlie",
    "status": "active",
    "age": 35,
    "department": "Marketing"
  },
  {
    "id": 4,
    "name": "Diana",
    "status": "pending",
    "age": 28,
    "department": "Engineering"
  }
]
```

### Sample CSV Data

Create a file `test_data.csv`:

```csv
id,name,status,age,department
1,Alice,active,30,Engineering
2,Bob,inactive,25,Sales
3,Charlie,active,35,Marketing
4,Diana,pending,28,Engineering
5,Eve,active,31,Sales
6,Frank,inactive,27,Marketing
```

## Testing Steps

### 1. Basic Library Usage

Run the basic example:

```bash
python examples/basic_library_usage.py
```

**Expected behavior:**
- TUI displays the data with 3 rows
- Press `Enter` on any row to see the selection printed
- Press `q` to quit
- "TUI exited!" message is printed on quit
- Final selection is printed

### 2. Custom Keybindings

Run the custom keybindings example:

```bash
python examples/custom_keybindings.py
```

**Expected behavior:**
- TUI displays only the specified columns: name, status, age, department
- Custom keybindings are available
- Press `Enter` to see name printed
- Press `q` to quit with selection message
- Custom "Thank you" message on quit

### 3. Programmatic Data Updates

Run the programmatic updates example:

```bash
python examples/programmatic_updates.py
```

**Expected behavior:**
- TUI starts with 2 items
- Background thread adds a new item every 2 seconds
- Press `r` to acknowledge data updates
- Press `q` to quit after 3 updates

### 4. Custom Test Script

Create a custom test script:

```bash
cat > test_library_api.py << 'EOF'
#!/usr/bin/env python3
"""Custom test for TableUI library API."""

from dv_tui import TableUI
import json

# Load test data
with open('test_data.json') as f:
    data = json.load(f)

def test_enter_handler(selected_row):
    """Test Enter key handler."""
    print(f"\n[TEST] Enter pressed on: {selected_row['name']}")
    print(f"[TEST] ID: {selected_row['id']}")
    print(f"[TEST] Status: {selected_row['status']}")
    
def test_quit_handler():
    """Test quit handler."""
    print("\n[TEST] TUI quit callback executed")

def test_select_handler(selected_row):
    """Test select handler."""
    print(f"\n[TEST] Row selected: {selected_row['name']}")

# Create TUI with configuration
tui = TableUI(
    data,
    columns=["id", "name", "status", "age", "department"]
)

# Test key bindings
tui.bind_key('Enter', test_enter_handler)
tui.bind_key('s', lambda row: print(f"[TEST] Status: {row['status']}"))

# Test callbacks
tui.on_quit(test_quit_handler)
tui.on_select(test_select_handler)

# Run TUI
print("[TEST] Starting TUI...")
selected = tui.run()
print(f"[TEST] TUI finished. Selected: {selected}")
EOF

chmod +x test_library_api.py
python test_library_api.py
```

### 5. Verify CLI Entry Point Still Works

Verify the CLI still uses core.py correctly:

```bash
# Test with JSON file
dv test_data.json

# Test with CSV file
dv test_data.csv

# Test with single-select mode
dv -s test_data.json
```

**Expected behavior:**
- CLI displays data correctly
- All navigation works (j/k for down/up, Enter to select, q to quit)
- Single-select mode outputs JSON to stdout

### 6. Test Configuration Options

Create a script to test configuration options:

```bash
cat > test_config.py << 'EOF'
#!/usr/bin/env python3
"""Test TableUI configuration options."""

from dv_tui import TableUI

data = [
    {"id": 1, "name": "Alice", "status": "active", "age": 30},
    {"id": 2, "name": "Bob", "status": "inactive", "age": 25},
]

# Test with columns
tui1 = TableUI(data, columns=["name", "status"])
print("[TEST] TableUI created with columns")

# Test with keybinds
tui2 = TableUI(
    data,
    keybinds={
        "normal": {
            "j": "down",
            "k": "up",
        }
    }
)
print("[TEST] TableUI created with keybinds")

# Test update_data
new_data = [
    {"id": 1, "name": "Alice", "status": "active", "age": 30},
    {"id": 2, "name": "Bob", "status": "inactive", "age": 25},
    {"id": 3, "name": "Charlie", "status": "active", "age": 35},
]
tui1.update_data(new_data)
print("[TEST] Data updated programmatically")

# Test callbacks
tui1.on_quit(lambda: print("[TEST] Quit callback set"))
tui1.on_mode_change(lambda mode: print(f"[TEST] Mode: {mode}"))
tui1.on_select(lambda row: print(f"[TEST] Selected: {row}"))
print("[TEST] All callbacks set")

print("[TEST] Configuration tests passed!")
EOF

python test_config.py
```

## Verification Checklist

- [ ] Basic library usage example runs without errors
- [ ] Custom keybindings example displays specified columns
- [ ] Programmatic updates example shows data changes
- [ ] Key bindings (`Enter`, `q`, `s`) work as expected
- [ ] Callbacks (`on_quit`, `on_select`) execute correctly
- [ ] Data updates via `update_data()` work
- [ ] CLI entry point still works with JSON files
- [ ] CLI entry point still works with CSV files
- [ ] Single-select mode works from CLI
- [ ] Column filtering works from library API
- [ ] Configuration options are properly passed through

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running from the project root:

```bash
export PYTHONPATH=/home/ylan/workspaces/repos/github/YlanAllouche/dv-tui.git/workspaces/initial-universalizing-effort:$PYTHONPATH
python examples/basic_library_usage.py
```

### Curses Errors

If curses displays errors, ensure your terminal supports curses:

```bash
export TERM=xterm-256color
python examples/basic_library_usage.py
```

### Data Not Displaying

If data doesn't display, verify:
- Data is a list of dictionaries
- Data has at least one row
- Data keys are strings

## API Reference Summary

### TableUI Class

**Constructor:**
```python
TableUI(data, columns=None, keybinds=None, enum_config=None)
```

**Methods:**
- `bind_key(key, handler)` - Bind a key to a Python function
- `bind_trigger(trigger_name, handler)` - Bind a trigger event
- `update_data(data)` - Update data programmatically
- `on_quit(callback)` - Set quit callback
- `on_mode_change(callback)` - Set mode change callback
- `on_select(callback)` - Set selection callback
- `run()` - Start the TUI

### Example Key Bindings

Common key names:
- `'Enter'` - Enter key
- `'q'` - q key (quit)
- `'j'` - j key (down)
- `'k'` - k key (up)
- `'h'` - h key (left)
- `'l'` - l key (right)
- `'Escape'` - Escape key
- `'/'` - Forward slash (search)

## Cleanup

Remove test files:

```bash
rm -f test_data.json test_data.csv test_library_api.py test_config.py
```
