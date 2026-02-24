#!/bin/bash
# Test script for tab management features

echo "=== Tab Management Test Script ==="
echo ""
echo "This script demonstrates the new tab management features."
echo ""
echo "Features tested:"
echo "  1. Loading tabs from JSON config (_config.tabs)"
echo "  2. Custom tab field name (--tab-field)"
echo "  3. Multiple files as tabs"
echo "  4. Per-tab state (selection, scroll) preservation"
echo ""

# Test 1: Tabs from config
echo "Test 1: Tabs from JSON config (_config.tabs)"
echo "  Command: dv test_with_tabs.json"
echo "  Expected: Two tabs (test_data_projects.json, test_data_tasks.json)"
echo "  Try: Press 'h' to switch to previous tab, 'l' for next tab"
echo "         Navigate and select items, switch tabs and notice state is preserved"
echo ""

# Test 2: Custom tab field
echo "Test 2: Custom tab field name"
echo "  Command: dv --tab-field myTabs test_custom_tab_field.json"
echo "  Expected: Uses 'myTabs' field instead of default '_config.tabs'"
echo ""

# Test 3: Multiple files as tabs
echo "Test 3: Multiple files as tabs"
echo "  Command: dv test_data_projects.json test_data_tasks.json"
echo "  Expected: Two tabs from CLI args (no config needed)"
echo ""

# Test 4: Per-tab state
echo "Test 4: Per-tab state preservation"
echo "  In any multi-tab view:"
echo "    1. Select row 5 in first tab"
echo "    2. Scroll down"
echo "    3. Press 'l' to switch to second tab"
echo "    4. Navigate in second tab"
echo "    5. Press 'h' to go back to first tab"
echo "  Expected: First tab remembers selection position and scroll offset"
echo ""

echo "=== Keybinds for Tabs ==="
echo "  h / ← : Previous tab"
echo "  l / → : Next tab"
echo ""

echo "=== Run tests ==="
echo "Press Ctrl+C to exit any test"
echo ""

# Optional: run interactive tests
read -p "Run test 1 (tabs from config)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    dv test_with_tabs.json
fi

read -p "Run test 2 (custom tab field)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    dv --tab-field myTabs test_custom_tab_field.json
fi

read -p "Run test 3 (multiple files)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    dv test_data_projects.json test_data_tasks.json
fi

echo "=== Testing complete ==="
