#!/usr/bin/env python3
"""Example showing custom keybindings and configuration."""

from dv_tui import TableUI

# Sample data
data = [
    {"id": 1, "name": "Alice", "status": "active", "age": 30, "department": "Engineering"},
    {"id": 2, "name": "Bob", "status": "inactive", "age": 25, "department": "Sales"},
    {"id": 3, "name": "Charlie", "status": "active", "age": 35, "department": "Marketing"},
    {"id": 4, "name": "Diana", "status": "active", "age": 28, "department": "Engineering"},
]

def my_custom_handler(selected_row):
    """Custom handler for 'a' key."""
    print(f"Custom action on: {selected_row['name']}")

def status_handler(selected_row):
    """Handler for 's' key to toggle status."""
    print(f"Status: {selected_row.get('status', 'N/A')}")

# Create TUI with custom columns and keybindings
tui = TableUI(
    data,
    columns=["name", "status", "age", "department"],
    keybinds={
        "normal": {
            "a": "custom_action",
            "s": "status_action",
        }
    }
)

# Note: keybinds config is passed to the TUI engine
# For direct Python function bindings, use bind_key():
tui.bind_key('Enter', lambda row: print(f"Pressed Enter on {row['name']}"))
tui.bind_key('q', lambda row: print(f"Quitting with selection: {row['name']}"))

# Set callbacks
tui.on_quit(lambda: print("Thank you for using dv-tui!"))

# Run the TUI
tui.run()
