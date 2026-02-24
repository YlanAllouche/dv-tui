# Quick CSV Testing Guide

## Test Files Created

```
test_tasks.csv       - 5 tasks with status, priority, type, assigned_to
test_mixed.csv      - 5 products with various data types
test_semicolon.csv   - 3 tasks with semicolon delimiter
test_no_headers.csv  - 4 people without header row
```

## Try These Commands (In Order)

### 1. Basic CSV Viewing
```bash
./dv.py test_tasks.csv
```
- First row automatically used as headers
- Arrow keys or j/k to navigate
- q to quit

### 2. Custom Delimiter
```bash
./dv.py --delimiter ';' test_semicolon.csv
```
- Uses semicolon instead of comma

### 3. Skip Headers
```bash
./dv.py --skip-headers test_no_headers.csv
```
- Creates column names: col_0, col_1, etc.

### 4. Column Filtering
```bash
./dv.py --columns "name,status,priority" test_tasks.csv
```
- Only shows specified columns

### 5. Search in CSV
```bash
./dv.py test_tasks.csv
# Press '/' to search, type "Alice"
```

### 6. Cell Mode
```bash
./dv.py test_tasks.csv
# Press 'c' to switch to cell mode
# Use h/l to move between cells
```

### 7. Multiple Files
```bash
./dv.py test_tasks.csv test_mixed.csv
# Use h/l to switch tabs
```

### 8. Single-Select Mode
```bash
./dv.py -s test_tasks.csv
# Select a row, outputs JSON to stdout
```

## Verification Commands

```bash
# Quick verify CSV loading works
python3 -c "
from dv_tui.data_loaders import CsvDataLoader
data = CsvDataLoader('test_tasks.csv').load()
print(f'✓ Loaded {len(data)} rows')
print(f'  Columns: {list(data[0].keys())}')
"

# Verify custom delimiter
python3 -c "
from dv_tui.data_loaders import CsvDataLoader
data = CsvDataLoader('test_semicolon.csv', delimiter=';').load()
print(f'✓ Custom delimiter works: {len(data)} rows')
"

# Verify skip headers
python3 -c "
from dv_tui.data_loaders import CsvDataLoader
data = CsvDataLoader('test_no_headers.csv', skip_headers=True).load()
print(f'✓ Skip headers works: {len(data)} rows')
print(f'  Columns: {list(data[0].keys())}')
"
```

## Real-World Examples

### View exported data
```bash
# Export from database or API to CSV, then view
./dv.py my_export.csv
```

### Pipe and view
```bash
# Generate CSV on the fly
echo -e "name,value\na,1\nb,2" | ./dv.py /dev/stdin
```

### Process selected rows
```bash
# Select and use in scripts
./dv.py -s test_tasks.csv | jq '.status'
```

## Keyboard Shortcuts (CSV Mode)

| Key | Action |
|-----|--------|
| j/↓ | Down |
| k/↑ | Up |
| h/← | Previous tab (or left cell in cell mode) |
| l/→ | Next tab (or right cell in cell mode) |
| / | Search |
| c | Toggle cell/row mode |
| Enter | Select row |
| q | Quit |
| R | Refresh (if file changed) |

## All Options

```
--delimiter CHAR     CSV delimiter (default: ',')
--skip-headers       Don't use first row as headers
--columns COLS       Comma-separated columns to show
--tab-name NAME      Custom tab name
--config FILE        Config file
-s, --single-select  Exit after selection
```
