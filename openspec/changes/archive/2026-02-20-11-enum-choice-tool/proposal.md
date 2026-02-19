# Change: Implement Enum Choice Tool

## Why
Provide quick data modification via enum value cycling and popup dialog for cell values. Support three enum sources (inline, inferred, external) with dynamic color cycling for enum fields.

## What Changes
- Create `EnumChoiceDialog` UI component (overlay popup)
- Implement arrow key navigation in enum picker
- Implement Enter to select, ESC to cancel
- Support three enum sources: inline, inferred, external
- Add e/E keys to cycle enum values in current cell (cell mode only)
- Add ctrl-e key to open enum picker popup dialog
- Implement color cycling for all enum fields (not just "status")
- Handle enum changes (update value, optionally trigger on_change script)

## Impact
- Affected specs: None (new capability)
- Affected code: ui.py, handlers.py, core.py, table.py, config.py modules
