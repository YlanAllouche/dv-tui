#!/bin/bash
# Test dv-tui with all the debug output to see what happens

echo "=== Running dv-tui with debug ==="
echo ""
echo "This will start dv-tui and log all activity to /tmp/dv_keys.txt"
echo ""
echo "Please:"
echo "1. Press 'c' to enter cell mode"
echo "2. Navigate to 'status' or 'priority' column"
echo "3. Press Ctrl+e to test enum picker"
echo "4. Press 'e' or 'E' to test enum cycling"
echo "5. Press 'q' to quit"
echo ""
echo "Watch the log in another terminal:"
echo "  tail -f /tmp/dv_keys.txt"
echo ""
read -p "Press Enter to start..."

# Start dv-tui
python dv.py test_enum_tasks.json -c test_enum_config_inline.json

echo ""
echo "=== dv-tui exited ==="
echo ""
echo "Key log summary:"
echo ""
echo "Checking for key codes 5, 101, 69 (Ctrl+e, e, E):"
grep -E "(Key:   (5|101|69)|Processing key (5|101|69))" /tmp/dv_keys.txt

echo ""
echo "Checking for enum function calls:"
grep -i "enum" /tmp/dv_keys.txt | tail -20

echo ""
echo "Checking for render calls:"
grep -i "render" /tmp/dv_keys.txt | tail -10

echo ""
echo "Checking for errors or exceptions:"
grep -i "error|exception|traceback" /tmp/dv_keys.txt | tail -10

echo ""
echo "If you see 'Loop start' but no 'After check_and_reload', something crashed during check_and_reload"
echo "If you see 'After check_and_reload' but no 'After render', something crashed during render"
echo "If you see 'After render' but no 'Key:', something crashed during getch()"
