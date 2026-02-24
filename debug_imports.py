#!/usr/bin/env python3
"""
Debug script to help identify import issues with dv_tui
"""

import sys
import traceback

print("=" * 60)
print("dv-tui Import Debug Script")
print("=" * 60)
print()

# Test 1: Check Python version
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# Test 2: Check sys.path
print("sys.path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")
print()

# Test 3: Try importing config module
print("Test 1: Import dv_tui.config directly")
try:
    import dv_tui.config
    print("  ✓ dv_tui.config imported successfully")
    print(f"  ✓ load_config function: {hasattr(dv_tui.config, 'load_config')}")
    if hasattr(dv_tui.config, 'load_config'):
        print(f"  ✓ load_config: {dv_tui.config.load_config}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
print()

# Test 4: Try importing load_config directly
print("Test 2: Import load_config from dv_tui.config")
try:
    from dv_tui.config import load_config
    print("  ✓ load_config imported successfully")
    print(f"  ✓ Type: {type(load_config)}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
print()

# Test 5: Try importing cli module
print("Test 3: Import dv_tui.cli")
try:
    import dv_tui.cli
    print("  ✓ dv_tui.cli imported successfully")
    print(f"  ✓ Has load_config: {hasattr(dv_tui.cli, 'load_config')}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
print()

# Test 6: Try running CLI
print("Test 4: Run CLI main() function")
try:
    from dv_tui.cli import main
    result = main(['--help'])
    print(f"  ✓ CLI executed with return code: {result}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
print()

print("=" * 60)
print("Debug complete")
print("=" * 60)
