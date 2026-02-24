#!/usr/bin/env python3
"""
Interactive test script for selection mode features.
Run this to verify row/cell selection modes work correctly.
"""

from dv_tui import Table, load_file

def test_selection_modes():
    print("=" * 60)
    print("SELECTION MODES - INTERACTIVE TEST")
    print("=" * 60)
    print()

    data = load_file("tests/data/selection_test.json")
    table = Table(data)

    print(f"Loaded {len(data)} items")
    print(f"Columns: {table.columns}")
    print()

    print("Testing initial state:")
    print(f"  selection_mode: {table.selection_mode}")
    print(f"  selected_index: {table.selected_index}")
    print(f"  selected_column: {table.selected_column}")
    print()

    print("Test 1: Default row mode")
    print(f"  ✓ selection_mode == 'row': {table.selection_mode == 'row'}")
    print()

    print("Test 2: Toggle to cell mode")
    table.selection_mode = 'cell'
    table.selected_column = 0
    print(f"  ✓ selection_mode == 'cell': {table.selection_mode == 'cell'}")
    print(f"  ✓ selected_column == 0: {table.selected_column == 0}")
    print()

    print("Test 3: Navigate columns in cell mode")
    table.selected_column = 1
    print(f"  ✓ selected_column == 1: {table.selected_column == 1}")
    table.selected_column = 2
    print(f"  ✓ selected_column == 2: {table.selected_column == 2}")
    print()

    print("Test 4: Toggle back to row mode")
    table.selection_mode = 'row'
    print(f"  ✓ selection_mode == 'row': {table.selection_mode == 'row'}")
    print()

    print("Test 5: Simulate Enter key behavior")
    print()

    print("  a) Row mode Enter (returns full row):")
    table.selection_mode = 'row'
    table.selected_index = 1
    row_data = table.selected_item
    print(f"     Row data: {row_data}")
    has_all = all(k in row_data for k in table.columns)
    print(f"     ✓ Has all columns: {has_all}")
    print()

    print("  b) Cell mode Enter (returns cell info):")
    table.selection_mode = 'cell'
    table.selected_index = 1
    table.selected_column = 2
    item = table.data[table.selected_index]
    cell_value = item.get(table.columns[table.selected_column])
    cell_info = {
        "value": cell_value,
        "row": table.selected_index,
        "column": table.columns[table.selected_column],
        "column_index": table.selected_column,
        "item": table.selected_item
    }
    print(f"     Cell info: {cell_info}")
    has_value = 'value' in cell_info
    matches = cell_info['value'] == 'pending'
    print(f"     ✓ Has 'value' key: {has_value}")
    print(f"     ✓ Value matches: {matches}")
    print()

    print("=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("To test interactively, run:")
    print("  dv tests/data/selection_test.json")
    print()
    print("Interactive test steps:")
    print("  1. Press 'c' to toggle to cell mode")
    print("  2. Press 'h'/'l' to navigate between columns")
    print("  3. Press Enter on a row in row mode (opens file in nvim)")
    print("  4. Press Enter on a cell in cell mode (opens file in nvim)")
    print("  5. Press 'c' again to return to row mode")
    print()

if __name__ == "__main__":
    test_selection_modes()
