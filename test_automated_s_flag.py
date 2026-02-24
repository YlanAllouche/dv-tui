#!/usr/bin/env python
"""
Automated test of -s flag without needing interactive TUI.
Uses a mock key sequence to test the complete flow.
"""

import sys
import json
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

print("=" * 60)
print("AUTOMATED -s FLAG TEST")
print("=" * 60)
print()

# Test 1: Simulate pressing Enter in row mode with -s
print("Test 1: Simulate Enter key in row mode with -s")
print("-" * 40)

# Mock curses to avoid TUI
with patch('curses.wrapper') as mock_wrapper:
    from dv_tui.cli import parse_args, get_cli_config
    from dv_tui.config import load_config
    from dv_tui.core import TUI
    import curses
    
    # Create TUI with single_select=True
    args = parse_args(['-s', 'tests/demo/tasks.json'])
    cli_config = get_cli_config(args)
    config = load_config(cli_config=cli_config)
    tui = TUI(['tests/demo/tasks.json'], single_select=True, config=config)
    
    # Load data
    tui.load_data()
    tui.init_curses(curses.initscr())
    
    # Mock key handler to return selected_item on Enter
    original_handle_key = tui.key_handler.handle_key
    
    def mock_handle_key(key, table, terminal_height):
        if key == ord('\n') or key == 10:  # Enter key
            # Return selected_item
            return False, table.selected_item
        return original_handle_key(key, table, terminal_height)
    
    tui.key_handler.handle_key = mock_handle_key
    
    # Capture stdout
    captured_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    
    try:
        # Simulate key press that should trigger -s output
        result = tui.run()
        sys.stdout = old_stdout
        
        output = captured_output.getvalue()
        
        if output:
            print("Output captured:")
            print(output)
            
            try:
                output_data = json.loads(output)
                print("✓ Valid JSON output")
                print(f"✓ Contains keys: {list(output_data.keys())}")
                
                # Verify it's a task
                if "name" in output_data:
                    print(f"✓ Contains task name: {output_data['name'][:30]}...")
                else:
                    print("✗ Missing expected 'name' field")
                    
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON: {e}")
        else:
            print("✗ No output captured")
            
    finally:
        sys.stdout = old_stdout
        tui.debug_file.close()

print()

# Test 2: Simulate pressing Enter in cell mode with -s
print("Test 2: Simulate Enter key in cell mode with -s")
print("-" * 40)

with patch('curses.wrapper') as mock_wrapper:
    from dv_tui.cli import parse_args, get_cli_config
    from dv_tui.config import load_config
    from dv_tui.core import TUI
    import curses
    
    args = parse_args(['-s', 'tests/demo/tasks.json'])
    cli_config = get_cli_config(args)
    config = load_config(cli_config=cli_config)
    tui = TUI(['tests/demo/tasks.json'], single_select=True, config=config)
    
    tui.load_data()
    tui.init_curses(curses.initscr())
    
    # Set cell mode
    tui.table.selection_mode = 'cell'
    tui.table.selected_column = 1  # name column
    
    original_handle_key = tui.key_handler.handle_key
    
    def mock_handle_key(key, table, terminal_height):
        if key == ord('\n') or key == 10:
            return False, table.selected_item
        return original_handle_key(key, table, terminal_height)
    
    tui.key_handler.handle_key = mock_handle_key
    
    captured_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    
    try:
        result = tui.run()
        sys.stdout = old_stdout
        
        output = captured_output.getvalue()
        
        if output:
            print("Output captured:")
            print(output)
            
            try:
                output_data = json.loads(output)
                print("✓ Valid JSON output")
                
                # Verify cell mode structure
                if "field" in output_data and "value" in output_data:
                    print(f"✓ Cell mode structure correct: field='{output_data['field']}', value='{output_data['value']}'")
                else:
                    print("✗ Missing cell mode structure")
                    
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON: {e}")
        else:
            print("✗ No output captured")
            
    finally:
        sys.stdout = old_stdout
        tui.debug_file.close()

print()

# Test 3: Verify single_select flag is respected
print("Test 3: Verify -s flag behavior without -s")
print("-" * 40)

with patch('curses.wrapper') as mock_wrapper:
    from dv_tui.cli import parse_args, get_cli_config
    from dv_tui.config import load_config
    from dv_tui.core import TUI
    import curses
    
    # WITHOUT -s flag
    args = parse_args(['tests/demo/tasks.json'])
    cli_config = get_cli_config(args)
    config = load_config(cli_config=cli_config)
    tui = TUI(['tests/demo/tasks.json'], single_select=False, config=config)
    
    tui.load_data()
    tui.init_curses(curses.initscr())
    
    # Press Enter
    original_handle_key = tui.key_handler.handle_key
    
    def mock_handle_key(key, table, terminal_height):
        if key == ord('\n') or key == 10:
            return False, table.selected_item
        return original_handle_key(key, table, terminal_height)
    
    tui.key_handler.handle_key = mock_handle_key
    
    captured_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    
    try:
        result = tui.run()
        sys.stdout = old_stdout
        
        output = captured_output.getvalue()
        
        if output:
            print("✗ UNEXPECTED: Output without -s flag")
        else:
            print("✓ Correct: No output without -s flag")
            
    finally:
        sys.stdout = old_stdout
        tui.debug_file.close()

print()

print("=" * 60)
print("AUTOMATED TESTS COMPLETE")
print("=" * 60)
