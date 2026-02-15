#!/bin/bash
# Test drill-down system with various data types

echo "=== Drill-Down System Test Commands ==="
echo ""
echo "These examples demonstrate the drill-down functionality."
echo "Run each command, then press 'c' to enter cell mode, navigate to a drillable cell"
echo "marked with [] (array), {} (object), or [fieldname] (named array), and press Enter to drill down."
echo "Press ESC to go back to the previous level."
echo ""
echo "⚠️  No hard depth limit - can drill indefinitely (limited by memory only)"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Basic Test Files ==="
echo ""
echo "1. Test nested arrays (projects with tasks)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_nested_array.json"
echo ""

echo "2. Test nested objects (features with metadata)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_nested_object.json"
echo ""

echo "3. Test multi-level nesting (objects containing arrays containing objects)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_multi_level.json"
echo ""

echo "4. Test named arrays (objects with single top-level array field)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_named_array.json"
echo ""

echo "5. Test new tab drill-down (via config)"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_new_tab.json"
echo ""

echo "=== Advanced Test File ==="
echo ""
echo "6. Comprehensive test with ALL drillable type combinations:"
echo "   Command: dv ${SCRIPT_DIR}/test_drilldown_comprehensive.json"
echo "   Contains 15 different test cases including:"
echo "   - Simple arrays & objects"
echo "   - Arrays of objects"
echo "   - Named arrays"
echo "   - Multi-level nesting"
echo "   - Arrays of arrays"
echo "   - Empty structures"
echo "   - Mixed drill paths"
echo "   - Complex mixed structures"
echo ""

echo "=== Single-Select Mode Example ==="
echo "   Command: dv -s ${SCRIPT_DIR}/test_drilldown_nested_array.json"
echo "   - Drilling continues deeper (no return)"
echo "   - Selecting non-drillable value outputs to stdout and exits"
echo ""

echo "=== Usage Instructions ==="
echo "Navigation in drill-down mode:"
echo "  - Press 'c' to toggle between row mode and cell mode"
echo "  - Use j/k or arrow keys to navigate"
echo "  - Press 'l' or right arrow to move between cells in cell mode"
echo "  - Look for cells with [] (array), {} (object), or [fieldname] (named array)"
echo "  - Press Enter on a drillable cell to drill down"
echo "  - Press ESC to go back to the previous level"
echo "  - The header shows 'Level X' to indicate drill-down depth"
echo ""

echo "=== Drill-Down Depth Behavior ==="
echo "  - No hard limit on drill-down depth"
echo "  - Practically limited by memory (100+ levels possible)"
echo "  - Each level saves state to navigation stack"
echo "  - ESC goes back one level at a time"
echo "  - Press ESC enough times to return to top level"
echo ""

echo "=== Quick Test ==="
if [ -t 0 ]; then
    echo "Running comprehensive test..."
    read -p "Press Enter to start or Ctrl+C to exit"
    dv "${SCRIPT_DIR}/test_drilldown_comprehensive.json"
else
    echo "Choose one of the commands above to test interactively."
fi
