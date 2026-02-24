#!/usr/bin/env python3
import json
from dv_tui.config import load_config
from dv_tui.table import Table

# Load test data
with open('test_enum_tasks.json') as f:
    data = json.load(f)

# Load config
config = load_config('test_enum_config_inline.json')

print("=== Config Debug ===")
print(f"Config has enum: {config.enum is not None}")
if config.enum:
    print(f"Enum config object: {config.enum}")
    print(f"Enum attributes: {[attr for attr in dir(config.enum) if not attr.startswith('_')]}")
    print(f"Status: {config.enum.status}")
    print(f"Priority: {config.enum.priority}")
    print(f"Type: {config.enum.type}")

print("\n=== Table Debug ===")
table = Table(data, enum_config=config.enum)
print(f"Table created with enum_fields: {table.enum_fields}")
print(f"Table columns: {table.columns}")

print("\n=== Checking each column ===")
for col in table.columns:
    if col in table.enum_fields:
        print(f"  {col}: YES (has enum config)")
    else:
        print(f"  {col}: NO (no enum config)")
        # Try getattr to see what happens
        result = getattr(config.enum, col, None)
        print(f"    getattr(config.enum, '{col}', None) = {result}")
