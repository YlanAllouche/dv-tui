# CSV Support - Demo Commands

## Basic CSV Loading

```bash
# View CSV file (default behavior - first row as headers)
./dv.py test_tasks.csv

# View CSV with automatic column detection
./dv.py test_mixed.csv
```

## Custom Delimiter

```bash
# View CSV with semicolon delimiter
./dv.py --delimiter ';' test_semicolon.csv

# View CSV with tab delimiter (if you create one)
./dv.py --delimiter '\t' test_tab.csv
```

## Skip Headers

```bash
# View CSV without using first row as headers
./dv.py --skip-headers test_no_headers.csv

# Combines with delimiter
./dv.py --delimiter ';' --skip-headers test_semicolon.csv
```

## Column Filtering

```bash
# Show only specific columns
./dv.py --columns "name,status" test_tasks.csv

# Filter with custom delimiter
./dv.py --delimiter ';' --columns "name,status" test_semicolon.csv
```

## Search and Navigation

```bash
# Open CSV and use '/' to search
./dv.py test_tasks.csv
# Press '/' then type "Alice" to filter
# Press 'j'/'k' to navigate
# Press 'q' to quit
```

## Selection Mode

```bash
# Single-select mode (useful for scripts)
./dv.py -s test_tasks.csv

# Select a row and it will print the JSON to stdout
# Pipe to other commands:
./dv.py -s test_tasks.csv | jq '.name'
```

## Custom Tab Name

```bash
# Set custom tab name
./dv.py --tab-name "My Tasks" test_tasks.csv
```

## Multiple Files (Tabs)

```bash
# Open multiple CSV files as tabs
./dv.py test_tasks.csv test_mixed.csv

# Navigate between tabs with 'h' (previous) and 'l' (next)
```

## Advanced: Cell Mode

```bash
# Open CSV and press 'c' to switch to cell mode
./dv.py test_tasks.csv
# Then use 'h'/'l' to navigate between cells
# Press 'c' again to return to row mode
```

## Advanced: Column Widths (via config file)

Create a config file `csv_config.json`:
```json
{
  "_config": {
    "columns": ["name", "status", "type"],
    "column_widths": {
      "name": 20,
      "status": 15,
      "type": 10
    }
  }
}
```

Then use:
```bash
./dv.py --config csv_config.json test_tasks.csv
```

## Real-World Examples

### View system processes exported to CSV
```bash
# Export and view
ps aux --sort=-%cpu | head -20 | awk '{print $1","$2","$3","$4","$11}' > processes.csv
./dv.py --skip-headers processes.csv
```

### View CSV data from web
```bash
# Download and view
curl -s "https://example.com/data.csv" > data.csv
./dv.py data.csv
```

### Chain with other commands
```bash
# Select and process
./dv.py -s test_tasks.csv | jq '.name'
```

## Tips

1. **Auto-refresh**: CSV files can be refreshed with `R` key if they're modified externally
2. **Search**: Press `/` to search, use regex patterns
3. **Drill-down**: If a cell contains JSON or arrays, press Enter to drill down
4. **Colors**: The app automatically colors different columns based on values

## Test Files

- `test_tasks.csv` - Tasks with status, priority, type
- `test_mixed.csv` - Products with various data types
- `test_semicolon.csv` - Data with semicolon delimiter
- `test_no_headers.csv` - Data without header row
