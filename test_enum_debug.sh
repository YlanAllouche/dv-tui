#!/bin/bash
# Test script to check enum functionality with detailed debugging

echo "=== Enum Functionality Test ==="
echo ""
echo "This will start dv-tui with enum configuration."
echo "After starting, press the following keys in order:"
echo "1. Press 'c' to switch to cell mode"
echo "2. Press Ctrl+e to open enum picker dialog"
echo "3. Or press 'e'/'E' to cycle through enum values"
echo ""
echo "The application logs all key presses to /tmp/dv_keys.txt"
echo "Run this in another terminal to see the logs:"
echo "  tail -f /tmp/dv_keys.txt"
echo ""
read -p "Press Enter to start..." 
echo ""

# Start dv-tui
python dv.py test_enum_tasks.json -c test_enum_config_inline.json

# After exiting, show relevant logs
echo ""
echo "=== Key Log Summary ==="
echo "Looking for enum-related key presses:"
grep -E "(5|101|69)" /tmp/dv_keys.txt | tail -10

echo ""
echo "Looking for enum picker calls:"
grep "enum_picker" /tmp/dv_keys.txt | tail -10

echo ""
echo "Looking for enum cycle calls:"
grep "enum_cycle" /tmp/dv_keys.txt | tail -10
