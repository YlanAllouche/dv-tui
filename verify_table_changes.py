#!/usr/bin/env python3
"""
Interactive test script to verify table rendering changes.
Run this to see the new table features in action.
"""

import sys
sys.path.insert(0, '.')

from dv_tui import Table, load_file
import json


def test_dynamic_columns(file_path):
    """Test 1: Dynamic column detection."""
    print(f"\n{'='*60}")
    print("TEST 1: Dynamic Column Detection")
    print(f"{'='*60}")
    print(f"File: {file_path}")
    
    data = load_file(file_path)
    table = Table(data)
    
    print(f"\nData items: {len(data)}")
    print(f"Detected columns: {table.columns}")
    print(f"Number of columns: {len(table.columns)}")
    
    # Show first item
    print(f"\nFirst item:")
    print(json.dumps(data[0], indent=2))


def test_column_filtering(file_path, columns):
    """Test 2: Column filtering."""
    print(f"\n{'='*60}")
    print("TEST 2: Column Filtering")
    print(f"{'='*60}")
    print(f"File: {file_path}")
    print(f"Requested columns: {columns}")
    
    data = load_file(file_path)
    table = Table(data, columns=columns)
    
    print(f"\nResult columns: {table.columns}")
    print(f"Columns filtered: {len(table.columns)} columns")


def test_column_reordering(file_path, columns):
    """Test 3: Column reordering."""
    print(f"\n{'='*60}")
    print("TEST 3: Column Reordering")
    print(f"{'='*60}")
    print(f"File: {file_path}")
    print(f"Custom order: {columns}")
    
    data = load_file(file_path)
    table = Table(data, columns=columns)
    
    print(f"\nResult columns: {table.columns}")


def test_dynamic_widths(file_path, available_width):
    """Test 4: Dynamic column width calculation."""
    print(f"\n{'='*60}")
    print("TEST 4: Dynamic Column Width Calculation")
    print(f"{'='*60}")
    print(f"File: {file_path}")
    print(f"Available width: {available_width}")
    
    data = load_file(file_path)
    table = Table(data)
    
    widths = table.calculate_column_widths(table.columns, available_width)
    
    print(f"\nColumns: {table.columns}")
    print(f"Widths:   {widths}")
    print(f"Total:    {sum(widths) + (len(widths) - 1)} (with spacing)")


def main():
    """Run all interactive tests."""
    print("\n" + "="*60)
    print("TABLE RENDERING - INTERACTIVE VERIFICATION")
    print("="*60)
    
    # Test 1: Dynamic columns
    test_dynamic_columns('tests/data/simple_products.json')
    test_dynamic_columns('tests/data/people.json')
    test_dynamic_columns('tests/data/tasks.json')
    
    # Test 2: Column filtering
    test_column_filtering('tests/data/tasks.json', ['title', 'status'])
    test_column_filtering('tests/data/simple_products.json', ['name', 'price'])
    
    # Test 3: Column reordering
    test_column_reordering('tests/data/tasks.json', ['status', 'priority', 'title'])
    
    # Test 4: Dynamic widths
    test_dynamic_widths('tests/data/simple_products.json', 80)
    test_dynamic_widths('tests/data/people.json', 100)
    test_dynamic_widths('tests/data/tasks.json', 120)
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
