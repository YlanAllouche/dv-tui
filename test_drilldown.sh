#!/bin/bash
# Test drill-down system with various data types

echo "=== Drill-Down System Test Commands ==="
echo ""
echo "These examples demonstrate the drill-down functionality."
echo "Run each command, then press 'c' to enter cell mode, navigate to a drillable cell"
echo "marked with [] (array) or {} (object), and press Enter to drill down."
echo "Press ESC to go back to the previous level."
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "1. Test nested arrays (projects with tasks)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_nested_array.json"
echo ""

echo "2. Test nested objects (features with metadata)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_nested_object.json"
echo ""

echo "3. Test multi-level nesting (objects containing arrays containing objects)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_multi_level.json"
echo ""

echo "=== Usage Instructions ==="
echo "Navigation in drill-down mode:"
echo "  - Press 'c' to toggle between row mode and cell mode"
echo "  - Use j/k or arrow keys to navigate"
echo "  - Press 'l' or right arrow to move between cells in cell mode"
echo "  - Look for cells with [] (array) or {} (object) indicators"
echo "  - Press Enter on a drillable cell to drill down"
echo "  - Press ESC to go back to the previous level"
echo "  - The header shows 'Level X' to indicate drill-down depth"
echo ""

echo "=== Quick Test ==="
if [ -t 0 ]; then
    echo "Running first example..."
    read -p "Press Enter to start or Ctrl+C to exit"
    dv "${SCRIPT_DIR}/test_drilldown_nested_array.json"
else
    echo "Choose one of the commands above to test interactively."
fi
