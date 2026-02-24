#!/usr/bin/env python3
"""Basic example of using dv-tui as a library."""

from dv_tui import TableUI

# Sample data
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

# Create TUI instance
tui = TableUI(data)

# Bind Enter key to handler
tui.bind_key('Enter', on_enter_handler)

# Set quit callback
tui.on_quit(on_quit_handler)

# Run the TUI
selected = tui.run()

print(f"Final selection: {selected}")
