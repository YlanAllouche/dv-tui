#!/bin/bash
# Test script for lifecycle triggers (on_startup, on_drilldown, on_backup)

echo "=========================================="
echo "Testing Lifecycle Triggers"
echo "=========================================="
echo ""
echo "This test demonstrates:"
echo "1. on_startup - fires when TUI starts"
echo "2. on_drilldown - fires when drilling into nested data"
echo "3. on_backup - fires when backing up from drill-down"
echo ""

echo "Expected behavior:"
echo "  - 'TUI Started' notification on startup (with data source)"
echo "  - Press 'c', navigate to tasks[], press Enter → 'Drill Down' notification (with field and depth)"
echo "  - Press ESC → 'Backup' notification (with backup level and context)"
echo "  - Press 'c', navigate to settings{}, press Enter → 'Drill Down' notification"
echo "  - Press ESC → 'Backup' notification"
echo "  - Press up/down → 'Moved to row' notifications"
echo "  - Press Enter → 'Selected row' notification"
echo ""

read -p "Press Enter to start TUI test..."
echo ""

# Run dv with lifecycle test data and config
python dv.py tests/trigger_lifecycle_data.json --config tests/trigger_lifecycle_config.json

echo ""
echo "=========================================="
echo "Test completed"
echo "=========================================="
