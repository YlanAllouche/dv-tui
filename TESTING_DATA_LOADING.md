# Interactive Testing Guide for 03-data-loading Implementation

## Overview
The 03-data-loading change adds unified data loading support for JSON, CSV, and stdin sources with enhanced features.

## Test Data Available

### CSV Test Data
- `tests/data/mixed_tasks.csv` - CSV file with comma delimiter
- Custom CSV test files can be created with any delimiter

### JSON Test Data
- `tests/data/work_tasks.json` - JSON file with work tasks
- `tests/data/study_tasks.json` - JSON file with study tasks
- `tests/data/test_inline_*.json` - Various inline JSON configs

### Stdin Test Data
- `tests/stdin_data/valid_json.json` - Valid JSON array
- `tests/stdin_data/missing_keys.json` - JSON with missing keys
- `tests/stdin_data/invalid_json.json` - Invalid JSON for error testing

---

## Interactive Testing Scenarios

### 1. JSON File Loading

**Basic JSON file:**
```bash
dv tests/data/work_tasks.json
```

**Multiple JSON files as tabs:**
```bash
dv tests/data/work_tasks.json tests/data/study_tasks.json
```

**Expected:**
- File opens with tab switching support (h/l or arrow keys)
- All data displayed correctly
- File reloads automatically when modified

---

### 2. CSV File Loading

**Basic CSV file:**
```bash
dv tests/data/mixed_tasks.csv
```

**CSV with custom delimiter (semicolon):**
```bash
# Create a test CSV with semicolon delimiter
cat > /tmp/test_semicolon.csv << 'EOF'
type;status;summary
work;active;Task 1
study;focus;Task 2
EOF

dv /tmp/test_semicolon.csv --delimiter ';'
```

**CSV with tab delimiter:**
```bash
# Create a test CSV with tab delimiter
printf "type\tstatus\tsummary\nwork\tactive\tTask 1\nstudy\tfocus\tTask 2\n" > /tmp/test_tab.csv

dv /tmp/test_tab.csv --delimiter $'\t'
```

**Expected:**
- CSV data displays with headers
- Delimiter parsing works correctly
- All fields shown properly

---

### 3. Inline JSON Loading

**Inline JSON array:**
```bash
dv '[{"type": "work", "status": "active", "summary": "Task 1"}, {"type": "study", "status": "focus", "summary": "Task 2"}]'
```

**Inline JSON object (should show error):**
```bash
dv '{"type": "work", "status": "active", "summary": "Task 1"}'
# Expected: Error - "JSON must be a list of objects"
```

**Inline JSON with missing keys:**
```bash
dv '[{"type": "work", "status": "active"}, {"type": "study", "summary": "Task 2"}]'
# Expected: Both rows shown, missing columns filled with empty strings
```

---

### 4. Stdin Loading with Timeout

**Default timeout (30 seconds):**
```bash
cat tests/stdin_data/valid_json.json | dv
```

**Custom timeout (60 seconds):**
```bash
cat tests/stdin_data/valid_json.json | dv --stdin-timeout 60
```

**No timeout (wait indefinitely):**
```bash
cat tests/stdin_data/valid_json.json | dv --no-stdin-timeout
```

**Test timeout behavior:**
```bash
# This should timeout after 2 seconds
timeout 2 cat | dv --stdin-timeout 1
# Expected: "Timeout waiting for stdin data after 1 seconds"
```

**Expected:**
- Data loads from stdin
- Timeout works as configured
- Error message on timeout

---

### 5. Piped Command Output

**Pipe from command:**
```bash
echo '[{"type": "work", "status": "active", "summary": "Task 1"}]' | dv
```

**Pipe from curl:**
```bash
curl -s 'https://api.github.com/users/python/repos?per_page=5' | dv
```

**Pipe from jq:**
```bash
cat tests/data/work_tasks.json | jq '[.[] | {type, status}]' | dv
```

---

### 6. Error Handling Tests

**Invalid JSON file:**
```bash
echo '{"invalid": json}' > /tmp/invalid.json
dv /tmp/invalid.json
# Expected: Error with line/column information
```

**Missing file:**
```bash
dv /nonexistent/file.json
# Expected: "/nonexistent/file.json not found"
```

**Invalid inline JSON:**
```bash
dv '[{invalid json}]'
# Expected: "Invalid JSON at position 1: Expecting value"
```

**Unsupported format:**
```bash
echo "test" > /tmp/test.txt
dv /tmp/test.txt
# Expected: "Unsupported file format: .txt"
```

---

### 7. Refresh Capability

**Test file reload:**
```bash
# Terminal 1: Open file
dv tests/data/work_tasks.json

# Terminal 2: Modify file
echo '{"type": "test", "status": "new", "summary": "Updated"}' >> tests/data/work_tasks.json

# Terminal 1: Observe automatic reload after 500ms
```

**Test inline JSON (no refresh):**
```bash
dv '[{"type": "work", "status": "active"}]'
# Inline JSON cannot be refreshed (only file-based)
```

---

### 8. Missing Columns Handling

**JSON with inconsistent keys:**
```bash
dv '[{"a": 1, "b": 2}, {"a": 3, "c": 4}, {"b": 5, "c": 6}]'
# Expected: All 3 columns (a, b, c) shown, missing cells empty
```

**CSV with missing values:**
```bash
printf "a,b,c\n1,2\n3,4,5\n" > /tmp/missing.csv
dv /tmp/missing.csv
# Expected: Row 1 has empty cell in column 'c'
```

---

### 9. Mixed Data Sources (Tabs)

**JSON + CSV:**
```bash
dv tests/data/work_tasks.json tests/data/mixed_tasks.csv
# Navigate between tabs with h/l or arrow keys
```

**Multiple inline JSON:**
```bash
dv '[{"type": "work"}]' '[{"type": "study"}]'
# Note: Inline JSON detected by checking if file exists
```

---

### 10. Integration with -c (refresh command)

**Note:** Refresh via `-c` flag is configured but actual refresh triggering is not yet implemented in this change.

```bash
# The flag is available and stored in config
dv tests/data/work_tasks.json -c "echo 'refresh command'"
# Refresh command is stored but not yet used
```

---

## Key Bindings for Testing

All standard keybindings work:
- `j/↓` - Move down
- `k/↑` - Move up
- `h/←` - Previous tab
- `l/→` - Next tab
- `/` - Search
- `q` - Quit
- `Enter` - Select item

---

## Verification Checklist

### JSON Loading
- [ ] Load JSON file successfully
- [ ] Display all data correctly
- [ ] Reload on file modification
- [ ] Handle invalid JSON with clear error message

### CSV Loading
- [ ] Load CSV file with comma delimiter
- [ ] Load CSV with custom delimiter (--delimiter)
- [ ] Display headers correctly
- [ ] Handle missing values

### Inline JSON
- [ ] Parse inline JSON array
- [ ] Reject inline JSON object (must be array)
- [ ] Handle missing keys (union of all keys)
- [ ] Show clear error for invalid JSON

### Stdin Loading
- [ ] Load from stdin with default timeout (30s)
- [ ] Load from stdin with custom timeout
- [ ] Load from stdin with no timeout
- [ ] Timeout with clear error message

### Data Handling
- [ ] Union of all keys as columns
- [ ] Missing cells shown as empty
- [ ] None values converted to empty strings
- [ ] All rows display consistently

### Error Messages
- [ ] File not found shows file path
- [ ] Invalid JSON shows line/column
- [ ] Invalid inline JSON shows position
- [ ] Unsupported format shows extension

---

## Test Commands Summary

```bash
# Quick test suite
dv tests/data/work_tasks.json                    # JSON file
dv tests/data/mixed_tasks.csv                   # CSV file
dv '[{"a": 1}, {"b": 2}]'                    # Inline JSON
cat tests/data/work_tasks.json | dv              # Stdin
echo '[{"test": 1}]' | dv --stdin-timeout 5    # Stdin with timeout
dv tests/data/work_tasks.json --delimiter ','    # CSV delimiter

# Advanced tests
cat <<EOF > /tmp/test.csv
a;b;c
1;2;3
4;5
EOF
dv /tmp/test.csv --delimiter ';'                 # Custom CSV delimiter
```

---

## Notes

- The `--delimiter` flag only applies to CSV files
- Inline JSON is detected by checking if the argument is a valid JSON string
- File-based JSON supports automatic refresh on modification
- Stdin timeout uses `select.select()` for precise timing
- All data loaders handle missing columns by using the union of all keys
