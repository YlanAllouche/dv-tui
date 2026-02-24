# Change: Implement CSV Support

## Why
Provide basic read-only CSV parsing and display to work with tabular data in CSV format.

## What Changes
- Use Python csv module for parsing
- Detect delimiter (comma by default, config to override)
- Treat first row as headers (config to skip)
- Convert to internal table format for display
- Support same features as JSON (search, selection, triggers)

## Impact
- Affected specs: None (new capability)
- Affected code: data_loaders.py module
