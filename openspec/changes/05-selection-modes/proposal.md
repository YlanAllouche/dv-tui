# Change: Implement Row and Cell Selection Modes

## Why
Support both row-level and cell-level selection to enable different interaction patterns and actions.

## What Changes
- Add `selection_mode` state: 'row' or 'cell'
- Track `selected_column` index in cell mode
- Add visual indicator for selected cell
- Enter key behavior varies by mode
- Add keybind to toggle between modes
- Update footer hints based on current mode

## Impact
- Affected specs: None (new capability)
- Affected code: table.py, handlers.py modules
