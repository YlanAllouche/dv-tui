# Change: Implement Trigger System for Event Actions

## Why
Enable execution of scripts/functions on cell/row/table events with environment variables for integration with external tools.

## What Changes
- Define trigger schema (table, rows, cells)
- Implement `TriggerExecutor` to run shell commands
- Pass environment variables (DV_SELECTED_CELL, DV_SELECTED_ROW, DV_SELECTED_INDEX, DV_SELECTED_COLUMN)
- Handle both sync and async execution
- Support Python function triggers (for library usage)
- Implement priority: cell (in cell mode) > row > table

## Impact
- Affected specs: None (new capability)
- Affected code: triggers.py, handlers.py modules
