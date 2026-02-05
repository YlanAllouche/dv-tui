#!/bin/bash
# Quick test commands for table rendering changes

echo "=========================================="
echo "TABLE RENDERING - VERIFICATION COMMANDS"
echo "=========================================="
echo ""

echo "1. Run all tests (78 total)"
echo "   python -m pytest tests/ -v"
echo ""

echo "2. Run only table module tests (27 tests)"
echo "   python -m pytest tests/test_table.py -v"
echo ""

echo "3. Run interactive verification script"
echo "   python verify_table_changes.py"
echo ""

echo "4. Test with new test data files"
echo ""
echo "   a) View simple products (auto-detect columns):"
echo "      dv tests/data/simple_products.json"
echo ""
echo "   b) View people data (missing fields):"
echo "      dv tests/data/people.json"
echo ""
echo "   c) View tasks with column filtering:"
echo "      dv tests/data/tasks.json -c tests/data/tasks_config.json"
echo ""

echo "5. Multiple tabs with different schemas:"
echo "   dv tests/data/simple_products.json tests/data/people.json tests/data/tasks.json"
echo ""

echo "6. Quick Python tests:"
echo ""
echo "   a) Test dynamic column detection:"
echo "      python -c 'from dv_tui import Table, load_file; data = load_file(\"tests/data/simple_products.json\"); t = Table(data); print(\"Columns:\", t.columns)'"
echo ""
echo "   b) Test column filtering:"
echo "      python -c 'from dv_tui import Table, load_file; data = load_file(\"tests/data/tasks.json\"); t = Table(data, columns=[\"title\", \"status\"]); print(\"Filtered:\", t.columns)'"
echo ""
echo "   c) Test column reordering:"
echo "      python -c 'from dv_tui import Table, load_file; data = load_file(\"tests/data/tasks.json\"); t = Table(data, columns=[\"status\", \"priority\", \"title\"]); print(\"Reordered:\", t.columns)'"
echo ""
echo "   d) Test width calculation:"
echo "      python -c 'from dv_tui import Table, load_file; data = load_file(\"tests/data/simple_products.json\"); t = Table(data); w = t.calculate_column_widths(t.columns, 80); print(\"Widths:\", w)'"
echo ""

echo "7. Verify package installation:"
echo "   python -c 'import dv_tui; print(\"Version:\", dv_tui.__version__)'"
echo ""

echo "=========================================="
echo "All commands ready!"
echo "=========================================="
