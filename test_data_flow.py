#!/usr/bin/env python3
"""Test the actual data loading flow used by dv-tui."""
import json
from dv_tui.config import load_config, load_config_from_inline_json
from dv_tui.table import Table

# Load test data
with open('test_enum_tasks.json') as f:
    data = json.load(f)

print("=== Simulating dv-tui Data Load Flow ===\n")

# Step 1: Load main config
main_config = load_config('test_enum_config_inline.json')
print(f"1. Main config loaded")
print(f"   Has enum config: {main_config.enum is not None}")
if main_config.enum:
    print(f"   Status: {main_config.enum.status}")
    print(f"   Priority: {main_config.enum.priority}")

# Step 2: Check for inline config in data
inline_config = load_config_from_inline_json(data)
print(f"\n2. Inline config from data: {inline_config is not None}")

# Step 3: Determine which config to use (this is what dv-tui does)
if inline_config:
    print("   Using inline config from data")
    tab_config = load_config(
        config_path=main_config.config_file,
        inline_config=inline_config,
        cli_config={},
    )
else:
    print("   Using main config from file")
    tab_config = main_config

print(f"\n3. Tab config to be used:")
print(f"   Has enum config: {tab_config.enum is not None}")
if tab_config.enum:
    print(f"   Status: {tab_config.enum.status}")
    print(f"   Priority: {tab_config.enum.priority}")

# Step 4: Create table with the config
enum_config = tab_config.enum if tab_config else main_config.enum
print(f"\n4. Creating Table with enum_config: {enum_config}")

table = Table(data, enum_config=enum_config)
print(f"   Table created with enum_fields: {table.enum_fields}")
print(f"   Table columns: {table.columns}")

# Step 5: Check what's accessible
print(f"\n5. Verification:")
for col in ['status', 'priority']:
    if col in table.enum_fields:
        print(f"   ✓ '{col}' IS in enum_fields")
    else:
        print(f"   ✗ '{col}' NOT in enum_fields")

print("\n✓ Data flow test complete!")
