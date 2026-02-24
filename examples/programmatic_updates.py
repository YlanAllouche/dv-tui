#!/usr/bin/env python3
"""Example showing programmatic data updates."""

from dv_tui import TableUI
import time
import threading

# Initial data
data = [
    {"id": 1, "name": "Alice", "status": "active", "age": 30},
    {"id": 2, "name": "Bob", "status": "inactive", "age": 25},
]

def background_updater(tui):
    """Background thread that updates data periodically."""
    for i in range(3, 7):
        time.sleep(2)
        
        # Update data
        new_data = [
            {"id": 1, "name": "Alice", "status": "active", "age": 30},
            {"id": 2, "name": "Bob", "status": "inactive", "age": 25},
            {"id": i, "name": f"User{i}", "status": "active", "age": 20 + i},
        ]
        
        tui.update_data(new_data)
        print(f"Data updated! Now {len(new_data)} items")
        print("Press 'r' to refresh the TUI with new data")

def refresh_handler(selected_row):
    """Handle refresh request."""
    print("Refresh requested - data is updated via update_data()")

# Create TUI
tui = TableUI(data, columns=["id", "name", "status", "age"])

# Bind 'r' key for refresh
tui.bind_key('r', refresh_handler)

# Set callbacks
tui.on_quit(lambda: print("Data updater demo finished"))

# Start background updater thread
updater = threading.Thread(target=background_updater, args=(tui,))
updater.daemon = True
updater.start()

# Run the TUI
print("Starting TUI... Data will be updated every 2 seconds")
print("Press 'q' to quit, 'r' to acknowledge refresh")
tui.run()
