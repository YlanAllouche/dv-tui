#!/bin/bash
# Test script for keybind system

echo "=========================================="
echo "Keybind System Test Scenarios"
echo "=========================================="
echo ""

echo "1. Test default keybinds"
echo "   Press 'j' to move down, 'k' to move up, '/' to search, 'q' to quit"
echo "   Command: cd test_keybinds && dv test_data.json"
echo ""
read -p "Press Enter to continue..."
clear

echo "2. Test --bind: Map 'n' to down movement"
echo "   Press 'n' to move down (instead of 'j')"
echo "   Command: cd test_keybinds && dv --bind 'n:down' test_data.json"
echo ""
read -p "Press Enter to run..."
cd test_keybinds && dv --bind 'n:down' test_data.json
clear

echo "3. Test --unbind: Remove 'j' as down key"
echo "   Press 'j' - should NOT move down anymore"
echo "   Use arrow keys or 'k' instead"
echo "   Command: cd test_keybinds && dv --unbind 'j' test_data.json"
echo ""
read -p "Press Enter to run..."
cd test_keybinds && dv --unbind 'j' test_data.json
clear

echo "4. Test --bind and --unbind together"
echo "   'n' moves down, 'j' is unbound, 'p' moves up"
echo "   Command: cd test_keybinds && dv --bind 'n:down' --bind 'p:up' --unbind 'j' test_data.json"
echo ""
read -p "Press Enter to run..."
cd test_keybinds && dv --bind 'n:down' --bind 'p:up' --unbind 'j' test_data.json
clear

echo "5. Test custom config file"
echo "   Leader key: ',' (not ';')"
echo "   Search key: 'f' (not '/')"
echo "   Down keys: 'n' and 'j'"
echo "   Up keys: 'p' and 'k'"
echo "   Command: cd test_keybinds && dv --config custom_config.json test_data.json"
echo ""
read -p "Press Enter to run..."
cd test_keybinds && dv --config custom_config.json test_data.json
clear

echo "6. Test inline config"
echo "   Search key: 's' (not '/')"
echo "   Press 's' to search for 'work'"
echo "   Command: cd test_keybinds && dv inline_config.json"
echo ""
read -p "Press Enter to run..."
cd test_keybinds && dv inline_config.json
clear

echo "7. Test precedence: CLI overrides config"
echo "   Config sets search to 'f', CLI overrides to 'x'"
echo "   Press 'x' to search (not 'f')"
echo "   Command: cd test_keybinds && dv --config custom_config.json --bind 'x:search' test_data.json"
echo ""
read -p "Press Enter to run..."
cd test_keybinds && dv --config custom_config.json --bind 'x:search' test_data.json
clear

echo "8. Test mode-specific bind"
echo "   In search mode, 'x' acts as quit"
echo "   Press '/' to enter search, then 'x' to exit"
echo "   Command: cd test_keybinds && dv --bind 'search:x:quit' test_data.json"
echo ""
read -p "Press Enter to run..."
cd test_keybinds && dv --bind 'search:x:quit' test_data.json
clear

echo "=========================================="
echo "All tests completed!"
echo "=========================================="
