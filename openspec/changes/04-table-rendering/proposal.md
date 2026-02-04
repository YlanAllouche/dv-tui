# Change: Implement Generalized Table Rendering

## Why
Support dynamic, configurable table display that works with any data structure without hardcoded field assumptions.

## What Changes
- Extract column header generation from hardcoded values
- Support dynamic column detection (union of all object keys)
- Add column filtering/reordering via config `columns` array
- Preserve current features (tab display with item counts, color-coded values, fuzzy search, scroll offset)
- Remove hardcoded assumptions about specific fields
- Make column widths configurable/calculated

## Impact
- Affected specs: None (new capability)
- Affected code: table.py module
