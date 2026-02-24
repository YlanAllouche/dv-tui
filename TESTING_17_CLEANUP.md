# Testing Guide for 17-cleanup

This document provides instructions for verifying that the cleanup changes were successfully implemented and that no hardcoded values remain.

## Overview

The 17-cleanup change removed:
- Hardcoded nvim integration (open_in_nvim_async method)
- Hardcoded play_locator integration (jelly_play_yt command)
- Hardcoded field expectations (type, status, summary columns)
- Hardcoded color mappings
- Debug logging to /tmp/dv_keys.txt and /tmp/dv_play.log
- Hardcoded paths (~/share/, ~/.cache/nvim/)

## Verification Steps

### 1. Verify No Hardcoded Paths

**Test 1.1: Check for hardcoded ~/share/ references**
```bash
grep -r "~/share/" --include="*.py" dv_tui/ dv.py
```
Expected: No matches

**Test 1.2: Check for hardcoded ~/.cache/nvim/ references**
```bash
grep -r "~/.cache/nvim/" --include="*.py" dv_tui/ dv.py
```
Expected: No matches

**Test 1.3: Check for hardcoded jelly_play_yt**
```bash
grep -r "jelly_play_yt" --include="*.py" dv_tui/ dv.py
```
Expected: No matches

### 2. Verify No Debug Logging

**Test 2.1: Check for /tmp/dv_keys.txt**
```bash
grep -r "/tmp/dv_keys.txt" --include="*.py" dv_tui/ dv.py
```
Expected: No matches

**Test 2.2: Check for /tmp/dv_play.log**
```bash
grep -r "/tmp/dv_play.log" --include="*.py" dv_tui/ dv.py
```
Expected: No matches

**Test 2.3: Verify no debug files are created**
```bash
# Run dv briefly and exit
echo '[{"name":"test"}]' | timeout 2 dv 2>/dev/null || true

# Check if debug files were created
if [ -f /tmp/dv_keys.txt ]; then echo "FAIL: /tmp/dv_keys.txt was created"; fi
if [ -f /tmp/dv_play.log ]; then echo "FAIL: /tmp/dv_play.log was created"; fi
```
Expected: No files created (no output)

### 3. Verify Generic Column Handling

**Test 3.1: Use arbitrary column names**
```bash
# Create test data with custom columns
cat > /tmp/test_custom.json <<'EOF'
[
  {"custom_field_1": "value1", "custom_field_2": "value2", "custom_field_3": "value3"},
  {"custom_field_1": "value4", "custom_field_2": "value5", "custom_field_3": "value6"}
]
EOF

# Run dv and verify columns are detected
python3 <<'PYEOF'
from dv_tui.data_loaders import JsonDataLoader
loader = JsonDataLoader('/tmp/test_custom.json')
data = loader.load()
if all('custom_field_1' in item and 'custom_field_2' in item and 'custom_field_3' in item for item in data):
    print("PASS: Custom columns detected correctly")
else:
    print("FAIL: Custom columns not detected")
PYEOF
```
Expected: "PASS: Custom columns detected correctly"

**Test 3.2: Test without type/status/summary fields**
```bash
cat > /tmp/test_no_standard.json <<'EOF'
[
  {"name": "Alice", "age": 30, "city": "NYC"},
  {"name": "Bob", "age": 25, "city": "LA"}
]
EOF

python3 <<'PYEOF'
from dv_tui.table import Table
from dv_tui.data_loaders import JsonDataLoader

loader = JsonDataLoader('/tmp/test_no_standard.json')
data = loader.load()
table = Table(data)

if set(table.columns) == {"age", "city", "name"}:
    print("PASS: Columns auto-detected without type/status/summary")
else:
    print(f"FAIL: Expected age, city, name; got {set(table.columns)}")
PYEOF
```
Expected: "PASS: Columns auto-detected without type/status/summary"

### 4. Verify Configurable Colors

**Test 4.1: Verify default colors are empty**
```bash
python3 <<'PYEOF'
from dv_tui.config import ColorsConfig

colors = ColorsConfig()
if colors.type == {} and colors.status == {}:
    print("PASS: Default color mappings are empty (no hardcoded values)")
else:
    print(f"FAIL: Default colors not empty: type={colors.type}, status={colors.status}")
PYEOF
```
Expected: "PASS: Default color mappings are empty"

**Test 4.2: Test custom color configuration**
```bash
cat > /tmp/test_config_colors.json <<'EOF'
{
  "colors": {
    "type": {
      "work": (5, True),
      "personal": (6, True)
    },
    "status": {
      "active": (2, True),
      "inactive": (3, True)
    }
  }
}
EOF

python3 <<'PYEOF'
from dv_tui.config import load_config

config = load_config(config_path='/tmp/test_config_colors.json')
if config.colors['type'].get('work') == (5, True):
    print("PASS: Custom color configuration works")
else:
    print("FAIL: Custom color configuration not working")
PYEOF
```
Expected: "PASS: Custom color configuration works"

### 5. Verify Error Messages

**Test 5.1: File not found error**
```bash
dv /tmp/nonexistent_file.json 2>&1 | head -5
```
Expected: Error message containing "File not found" or "No input file"

**Test 5.2: Invalid JSON error**
```bash
echo 'invalid json' > /tmp/invalid.json
dv /tmp/invalid.json 2>&1 | head -5
```
Expected: Error message containing "Invalid JSON"

### 6. Verify Integration via Triggers

**Test 6.1: Example nvim integration exists**
```bash
if [ -f examples/nvim_integration.md ]; then
    echo "PASS: nvim integration example exists"
else
    echo "FAIL: nvim integration example missing"
fi
```
Expected: "PASS: nvim integration example exists"

**Test 6.2: Example play_locator integration exists**
```bash
if [ -f examples/play_locator_integration.md ]; then
    echo "PASS: play_locator integration example exists"
else
    echo "FAIL: play_locator integration example missing"
fi
```
Expected: "PASS: play_locator integration example exists"

### 7. Run All Tests

**Test 7.1: Run pytest**
```bash
python -m pytest tests/ -v
```
Expected: All 199 tests pass

### 8. Manual Functional Testing

**Test 8.1: Run with arbitrary data**
```bash
cat > /tmp/test_data.json <<'EOF'
[
  {"product": "Widget", "price": 10.99, "stock": 100},
  {"product": "Gadget", "price": 25.50, "stock": 50},
  {"product": "Doohickey", "price": 5.00, "stock": 200}
]
EOF

# Interactive test (you can navigate and verify columns)
timeout 2 dv /tmp/test_data.json 2>/dev/null || true
```
Expected: Application starts and displays data with columns: product, price, stock

**Test 8.2: Test without command line args (should show error)**
```bash
dv 2>&1 | head -5
```
Expected: Error message explaining usage

**Test 8.3: Test with pipe**
```bash
echo '[{"field1": "a"}, {"field1": "b"}]' | dv --no-stdin-timeout &
sleep 2
pkill -f dv 2>/dev/null || true
```
Expected: Application starts and displays data from stdin

## Summary Checklist

After running all tests, verify:

- [ ] No hardcoded paths found in code
- [ ] No debug logging files created
- [ ] Arbitrary column names work correctly
- [ ] Data without type/status/summary fields works
- [ ] Default color mappings are empty
- [ ] Custom color configuration works
- [ ] Clear error messages for common errors
- [ ] Example integration docs exist
- [ ] All 199 automated tests pass
- [ ] Manual functional tests work

## Verification Commands Summary

Run all verification checks in one go:

```bash
echo "=== Running verification checks ==="

# Check for hardcoded paths
echo -n "1. Hardcoded paths: "
if grep -q "~/share/" --include="*.py" dv_tui/ dv.py 2>/dev/null || \
   grep -q "~/.cache/nvim/" --include="*.py" dv_tui/ dv.py 2>/dev/null; then
    echo "FAIL"
else
    echo "PASS"
fi

# Check for debug logging
echo -n "2. Debug logging: "
if grep -q "/tmp/dv_keys.txt" --include="*.py" dv_tui/ dv.py 2>/dev/null || \
   grep -q "/tmp/dv_play.log" --include="*.py" dv_tui/ dv.py 2>/dev/null; then
    echo "FAIL"
else
    echo "PASS"
fi

# Check for jelly_play_yt
echo -n "3. Hardcoded jelly_play_yt: "
if grep -q "jelly_play_yt" --include="*.py" dv_tui/ dv.py 2>/dev/null; then
    echo "FAIL"
else
    echo "PASS"
fi

# Run tests
echo -n "4. Automated tests: "
if python -m pytest tests/ -q 2>&1 | tail -1 | grep -q "199 passed"; then
    echo "PASS"
else
    echo "FAIL"
fi

# Check example docs
echo -n "5. Example docs: "
if [ -f examples/nvim_integration.md ] && [ -f examples/play_locator_integration.md ]; then
    echo "PASS"
else
    echo "FAIL"
fi

echo "=== Verification complete ==="
```
