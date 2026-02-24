#!/bin/bash
# Test commands for dv-tui with -s flag and new actions
# Run these commands in your terminal to test the implementation

echo "=========================================="
echo "DV-TUI TEST COMMANDS"
echo "=========================================="
echo ""

echo "1. Basic TUI viewing (no -s flag)"
echo "   dv tests/demo/tasks.json"
echo ""

echo "2. Single-select: Row mode - Select and exit"
echo "   dv -s tests/demo/tasks.json"
echo "   (Navigate with j/k, press Enter on a row)"
echo ""

echo "3. Single-select: Cell mode - Extract field + value"
echo "   dv -s tests/demo/tasks.json"
echo "   (Press 'c' for cell mode, navigate cells, press Enter)"
echo ""

echo "4. CSV data support"
echo "   dv tests/demo/products.csv"
echo ""

echo "5. CSV with single-select"
echo "   dv -s tests/demo/products.csv"
echo ""

echo "6. Test search mode with -s"
echo "   dv -s tests/demo/tasks.json"
echo "   (Press '/' to search, type 'bug', press Enter)"
echo ""

echo "7. Extract single field with jq (row mode)"
echo "   dv -s tests/demo/tasks.json | jq -r .name"
echo ""

echo "8. Extract ID with jq (row mode)"
echo "   dv -s tests/demo/projects.json | jq -r .project_id"
echo ""

echo "9. Extract multiple fields with jq"
echo "   dv -s tests/demo/employees.json | jq '{name, role, salary}'"
echo ""

echo "10. Cell mode + jq (extract just the value)"
echo "   dv -s tests/demo/tasks.json"
echo "   (Press 'c', select cell, press Enter)"
echo "   Then pipe to jq: ... | jq -r .value"
echo ""

echo "11. Test null values in cell mode"
echo "   dv -s tests/demo/employees.json"
echo "   (Navigate to Eve Wilson's 'manager' field - it's null)"
echo ""

echo "12. Multiple files as tabs"
echo "   dv tests/demo/tasks.json tests/demo/projects.json"
echo "   (Use h/l to switch tabs)"
echo ""

echo "13. Filter columns"
echo "   dv --columns 'id,name,status' tests/demo/tasks.json"
echo ""

echo "14. Custom delimiter for CSV"
echo "   dv --delimiter ';' tests/demo/products.csv"
echo ""

echo "15. Search then toggle mode before Enter"
echo "   dv -s tests/demo/tasks.json"
echo "   (/ → search → press Enter → press c → select cell → press Enter)"
echo ""

echo "16. Chain commands: Select ID, simulate API call"
echo "   echo \"Fetching details for: \$(dv -s tests/demo/projects.json | jq -r .project_id)\""
echo ""

echo "17. Test yank cell (copy to clipboard)"
echo "   dv tests/demo/tasks.json"
echo "   (Press 'c' for cell mode, select cell, press Enter to yank)"
echo ""

echo "18. Cell mode with different data types"
echo "   dv -s tests/demo/employees.json"
echo "   (Navigate to salary: integer, remote: boolean, join_date: string)"
echo ""

echo "=========================================="
echo "ADVANCED EXAMPLES"
echo "=========================================="
echo ""

echo "A. Select high-priority tasks and filter:"
echo "   dv -s tests/demo/tasks.json | jq 'select(.priority == \"high\")'"
echo ""

echo "B. Get total hours estimate:"
echo "   dv -s tests/demo/tasks.json | jq '[.hours_estimate] | add'"
echo ""

echo "C. Format as table for shell output:"
echo "   dv -s tests/demo/employees.json | jq -r '\"\\(.name) | \\(.role)\"'"
echo ""

echo "D. Create a shell function for easy selection:"
echo '   select_task() { dv -s tests/demo/tasks.json | jq -r "$@"; }'
echo '   select_task .name'
echo ""

echo "=========================================="
echo "TESTING COMPOSABILITY"
echo "=========================================="
echo ""

echo "Pattern 1: Select → Extract → Use in script"
echo '   TASK_ID=$(dv -s tests/demo/projects.json | jq -r .project_id)'
echo '   echo "Working on project: $TASK_ID"'
echo ""

echo "Pattern 2: Multiple selection with jq filtering"
echo '   dv -s tests/demo/tasks.json | jq -r "select(.status == \"active\") | .name"'
echo ""

echo "Pattern 3: Create new filtered JSON"
echo '   dv -s tests/demo/employees.json | jq "{employees: map(select(.remote))}"'
echo ""

echo "=========================================="
echo "MOCK API SCENARIOS"
echo "=========================================="
echo ""

echo "Simulate: Select ID → Fetch details → Display in dv"
echo "   echo \"Simulated API response:\""
echo "   curl -s https://api.github.com/repos/$(dv -s tests/demo/projects.json | jq -r '.name | ascii_downcase')"
echo ""

echo "=========================================="
echo "KEYBINDING TESTS"
echo "=========================================="
echo ""

echo "Test these in dv (without -s):"
echo "  j/k     - Navigate rows"
echo "  h/l     - Switch tabs (row mode) or cells (cell mode)"
echo "  c       - Toggle row/cell mode"
echo "  /       - Enter search mode"
echo "  Tab     - Next search result"
echo "  Esc     - Exit search"
echo "  q       - Quit"
echo ""

echo "=========================================="
echo "READY TO TEST!"
echo "=========================================="
