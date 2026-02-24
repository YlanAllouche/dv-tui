#!/bin/bash
# Test separate row/cell navigation events

echo "Testing separate navigation events..."
echo ""

PYTHONPATH=. python3 << 'PYEOF'
from dv_tui.config import load_config
from dv_tui.handlers import KeyHandler
from dv_tui.table import Table
import time

# Load config
config = load_config(config_path='tests/trigger_navigate_config.json')
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

print("Testing navigation events with notify-send...")
print("Check your desktop for notifications!")
print("")

# Test row navigation (up/down)
print("1. Testing on_navigate_row (row 0 -> row 1)...")
table.selected_index = 1
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_navigate_row", context, async_exec=False)
time.sleep(1)

print("2. Testing on_navigate_row (row 1 -> row 2)...")
table.selected_index = 2
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_navigate_row", context, async_exec=False)
time.sleep(1)

# Test cell navigation (left/right)
print("3. Testing on_navigate_cell (cell mode, column 0 -> column 1)...")
table.selection_mode = 'cell'
table.selected_column = 1
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_navigate_cell", context, async_exec=False)
time.sleep(1)

print("4. Testing on_navigate_cell (cell mode, column 1 -> column 2)...")
table.selected_column = 2
context = handler._build_trigger_context(table)
handler.trigger_manager.execute_trigger_event("on_navigate_cell", context, async_exec=False)
time.sleep(1)

# Test that row navigation doesn't fire cell triggers
print("5. Testing row navigation doesn't fire cell triggers...")
table.selected_index = 3
table.selection_mode = 'row'
context = handler._build_trigger_context(table)
print(f"   Context: col={context['selected_column']}, cell={context['selected_cell']}")

trigger = handler.trigger_manager.get_trigger("on_navigate_cell", context)
if trigger is None:
    print("   ✓ Correctly: No on_navigate_cell trigger for row mode")
else:
    print("   ✗ BUG: on_navigate_cell fired in row mode!")

# Test that cell navigation doesn't fire row triggers
print("6. Testing cell navigation doesn't fire row triggers...")
table.selection_mode = 'cell'
table.selected_column = 0
context = handler._build_trigger_context(table)
print(f"   Context: col={context['selected_column']}, cell={context['selected_cell']}")

trigger = handler.trigger_manager.get_trigger("on_navigate_row", context)
if trigger is None:
    print("   ✓ Correctly: No on_navigate_row trigger for cell mode")
else:
    print("   ✗ BUG: on_navigate_row fired in cell mode!")

print("")
print("✓ All navigation tests completed!")
print("If you saw 4 notifications, separate events are working correctly.")
PYEOF

echo ""
echo "Check your desktop notifications!"
