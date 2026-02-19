#!/bin/bash
# Quick test script for enum choice tool

echo "=== Enum Choice Tool Test Script ==="
echo ""
echo "Choose a test scenario:"
echo "1. Inline enum source (predefined values)"
echo "2. Inferred enum source (scan column)"
echo "3. External enum source (command-based)"
echo "4. Mixed enum sources (all three types)"
echo "5. Run all tests sequentially"
echo "q. Quit"
echo ""
read -p "Select option: " choice

case $choice in
  1)
    echo ""
    echo "Testing inline enum source..."
    echo "Press 'c' for cell mode, navigate to status/priority column"
    echo "  e = cycle next, E = cycle prev, ctrl-e = popup"
    sleep 2
    python dv.py test_enum_tasks.json -c test_enum_config_inline.json
    ;;
  2)
    echo ""
    echo "Testing inferred enum source..."
    echo "Press 'c' for cell mode, navigate to any column"
    echo "  e = cycle next, E = cycle prev, ctrl-e = popup"
    sleep 2
    python dv.py test_enum_comprehensive.json -c test_enum_config_inferred.json
    ;;
  3)
    echo ""
    echo "Testing external enum source..."
    echo "Press 'c' for cell mode, navigate to priority column"
    echo "  e = cycle next, E = cycle prev, ctrl-e = popup"
    sleep 2
    python dv.py test_enum_tasks.json -c test_enum_config_external.json
    ;;
  4)
    echo ""
    echo "Testing mixed enum sources..."
    echo "Press 'c' for cell mode, try different columns"
    echo "  e = cycle next, E = cycle prev, ctrl-e = popup"
    sleep 2
    python dv.py test_enum_comprehensive.json -c test_enum_config_mixed.json
    ;;
  5)
    echo ""
    echo "Running all tests..."
    for i in {1..4}; do
      echo ""
      echo "Test $i of 4 - Press Enter to start..."
      read
      case $i in
        1) python dv.py test_enum_tasks.json -c test_enum_config_inline.json ;;
        2) python dv.py test_enum_comprehensive.json -c test_enum_config_inferred.json ;;
        3) python dv.py test_enum_tasks.json -c test_enum_config_external.json ;;
        4) python dv.py test_enum_comprehensive.json -c test_enum_config_mixed.json ;;
      esac
    done
    ;;
  q|Q)
    echo "Goodbye!"
    exit 0
    ;;
  *)
    echo "Invalid option"
    exit 1
    ;;
esac
