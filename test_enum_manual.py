#!/usr/bin/env python3
import json
from dv_tui.config import load_config
from dv_tui.table import Table
from dv_tui.ui import get_enum_options

# Load test data
with open('test_enum_tasks.json') as f:
    data = json.load(f)

# Load config
config = load_config('test_enum_config_inline.json')

# Create Table
table = Table(data, enum_config=config.enum)
print(f"Table created with enum_fields: {table.enum_fields}")
print(f"Columns: {table.columns}")

# Simulate being on status column (index 1)
field_name = "status"
selected_index = 0
selected_column = table.columns.index(field_name)

print(f"\nSelected column: {field_name} (index {selected_column})")
print(f"Current value: {data[selected_index][field_name]}")

# Get enum config for this field
enum_config = getattr(config.enum, field_name, None)
print(f"\nEnum config for '{field_name}': {enum_config}")

# Build context
context = {
    "selected_index": selected_index,
    "selected_column": field_name,
    "selected_row": data[selected_index],
    "selected_cell": data[selected_index].get(field_name),
}

# Get enum options
options = get_enum_options(enum_config, field_name, data, context)
print(f"\nEnum options: {options}")

# Test cycling
current_value = str(data[selected_index].get(field_name, ""))
try:
    current_index = options.index(current_value)
except ValueError:
    current_index = -1

print(f"Current value: '{current_value}' (index {current_index})")
if current_index >= 0:
    next_index = (current_index + 1) % len(options)
    print(f"Next value (e key): '{options[next_index]}' (index {next_index})")
    
    prev_index = (current_index - 1) % len(options)
    print(f"Prev value (E key): '{options[prev_index]}' (index {prev_index})")

# Test color cycling
print(f"\nTesting color cycling:")
for i, item in enumerate(data):
    value = item.get(field_name)
    color = table.get_enum_color(field_name, str(value))
    print(f"  Row {i}: {value} -> color={color}")
