#!/usr/bin/env python3
"""Test enum logic without curses to verify the configuration works."""
import json
from dv_tui.config import load_config
from dv_tui.table import Table
from dv_tui.ui import get_enum_options

# Load test data
with open('test_enum_tasks.json') as f:
    data = json.load(f)

# Load config
config = load_config('test_enum_config_inline.json')

print("=== Enum Configuration Test ===\n")

# Create table
table = Table(data, enum_config=config.enum)

print(f"Enum fields configured: {table.enum_fields}")
print(f"Columns: {table.columns}\n")

# Test each enum field
for field_name in table.enum_fields:
    print(f"--- Testing field: {field_name} ---")
    
    # Get enum config
    enum_config = getattr(config.enum, field_name, None)
    print(f"  Enum config: {enum_config}")
    
    # Build context
    context = {
        "selected_index": 0,
        "selected_column": field_name,
        "selected_row": data[0],
        "selected_cell": data[0].get(field_name),
    }
    
    # Get enum options
    options = get_enum_options(enum_config, field_name, data, context)
    print(f"  Enum options: {options}")
    
    # Test cycling
    current_value = str(data[0].get(field_name, ""))
    print(f"  Current value: '{current_value}'")
    
    if options:
        try:
            current_index = options.index(current_value)
            next_index = (current_index + 1) % len(options)
            prev_index = (current_index - 1) % len(options)
            
            print(f"  Next value (e): '{options[next_index]}'")
            print(f"  Prev value (E): '{options[prev_index]}'")
        except ValueError:
            print(f"  Current value not in options!")
    else:
        print(f"  ERROR: No options available!")
    print()

# Test that non-enum fields don't have enum config
print("=== Testing non-enum fields ===\n")
for col in table.columns:
    if col not in table.enum_fields:
        print(f"Field '{col}': No enum config (expected)")

print("\n✓ Configuration test complete!")
