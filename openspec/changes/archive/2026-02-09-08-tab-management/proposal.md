# Change: Implement Tab Management System

## Why
Support multiple data views through tabs for better organization of related datasets.

## What Changes
- Add `--tab-field` CLI flag for custom tab field name (default: `_config.tabs`)
- Load tabs from JSON config if present
- Ignore CLI file args when tabs are in config
- Preserve existing tab navigation (h/l for prev/next)
- Support drill-down to new tab
- Each tab maintains its own data, selection, and scroll state

## Impact
- Affected specs: None (new capability)
- Affected code: table.py, config.py modules
