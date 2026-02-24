# Change: Implement Drill-Down System for Nested Data

## Why
Enable navigation of nested data structures by clicking on array-containing cells.

## What Changes
- Detect cells containing arrays/objects (not just primitives)
- Add visual indicator for drillable cells
- Support opening drill-down in same tab or new tab (configurable)
- Implement drill-down configuration (field, inherit_flags, extra_flags, new_tab)
- Implement navigation stack for "back" functionality
- Pass parent data context to child view (optional)

## Impact
- Affected specs: None (new capability)
- Affected code: table.py, handlers.py modules
