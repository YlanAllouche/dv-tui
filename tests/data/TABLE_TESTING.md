# Table Rendering Test Data

This directory contains test data files to verify the new generalized table rendering features.

## Test Files

### simple_products.json
Simple product data with 4 fields: `name`, `price`, `stock`, `category`
- Demonstrates dynamic column detection
- Shows numeric and string fields

### people.json
People data with 4 fields: `first_name`, `last_name`, `age`, `role`
- Demonstrates handling of missing fields (Charlie has no `last_name`)
- Mixed data types (integers, strings)

### tasks.json
Task management data with 5 fields: `id`, `title`, `priority`, `status`, `assignee`
- More complex data structure
- Shows column width calculation with varying content lengths

### tasks_config.json
Configuration file for tasks.json that demonstrates column filtering:
```json
{
    "columns": ["title", "status", "priority"]
}
```

## Interactive Verification

Run the verification script:
```bash
python verify_table_changes.py
```

This will demonstrate:
1. **Dynamic Column Detection** - Tables automatically detect all unique keys
2. **Column Filtering** - Config can specify which columns to show
3. **Column Reordering** - Columns can be displayed in any order
4. **Dynamic Width Calculation** - Widths adjust based on content and available space

## CLI Examples

### View all detected columns
```bash
dv tests/data/simple_products.json
```

### View with custom column order (via inline config)
```bash
echo '[{"columns": ["name", "price"]}]' | dv tests/data/simple_products.json -c inline:-
```

### View tasks with specific columns
```bash
dv tests/data/tasks.json -c tests/data/tasks_config.json
```

### Compare different data structures
```bash
# Open multiple tabs with different schemas
dv tests/data/simple_products.json tests/data/people.json tests/data/tasks.json
```

## Key Features Demonstrated

1. **No Hardcoded Fields** - Tables work with any JSON structure
2. **Backward Compatible** - Existing `type` and `status` color rules still work
3. **Flexible Configuration** - Columns can be filtered and reordered via config
4. **Dynamic Layouts** - Column widths adapt to content and terminal width
