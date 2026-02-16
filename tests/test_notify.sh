#!/bin/bash
# Simple test to verify trigger execution

echo "Testing trigger system..."
echo ""

PYTHONPATH=. python3 << 'PYEOF'
from dv_tui.config import load_config
from dv_tui.handlers import KeyHandler
from dv_tui.table import Table
import time

# Load config
config = load_config(config_path='tests/trigger_test_config.json')
handler = KeyHandler(config)

# Create table with test data
data = [
    {"id": 1, "name": "Task 1", "status": "active", "priority": "high"},
    {"id": 2, "name": "Task 2", "status": "pending", "priority": "medium"},
    {"id": 3, "name": "Task 3", "status": "done", "priority": "low"},
    {"id": 4, "name": "Task 4", "status": "active", "priority": "high"}
]
table = Table(data)

print("✓ Triggers loaded:")
print(f"  Table triggers: {list(handler.trigger_manager.table_triggers.keys())}")
print(f"  Row triggers: {list(handler.trigger_manager.row_triggers.keys())}")
print(f"  Cell triggers: {list(handler.trigger_manager.cell_triggers.keys())}")
print("")

print("Testing triggers with notify-send...")
print("Check your desktop for notifications!")
print("")

# Test table trigger (on_change)
print("1. Testing table on_change trigger (row 2 -> row 3)...")
table.selected_index = 2
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_change", context, async_exec=False)
time.sleep(1)

# Test table trigger (on_select)
print("2. Testing table on_select trigger (row 2)...")
table.selected_index = 2
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_select", context, async_exec=False)
time.sleep(1)

# Test row trigger (row 0)
print("3. Testing row on_select trigger (row 0)...")
table.selected_index = 0
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_select", context, async_exec=False)
time.sleep(1)

# Test row trigger (row 3)
print("4. Testing row on_select trigger (row 3)...")
table.selected_index = 3
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_select", context, async_exec=False)
time.sleep(1)

# Test cell trigger
print("5. Testing cell on_select trigger (row 0, column 'name')...")
table.selection_mode = 'cell'
table.selected_column = 1  # name column
table.selected_index = 0
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_select", context, async_exec=False)
time.sleep(1)

print("")
print("✓ All trigger tests completed!")
print("If you saw 5 notifications, the trigger system is working correctly.")
PYEOF

echo ""
echo "Check your desktop notifications!"
