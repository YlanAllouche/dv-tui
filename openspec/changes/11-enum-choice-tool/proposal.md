# Change: Implement Enum Choice Tool

## Why
Provide popup dialog to change cell/row values from a predefined enum for quick data modification.

## What Changes
- Create `EnumChoiceDialog` UI component (overlay popup)
- Implement arrow key navigation in enum picker
- Implement Enter to select, ESC to cancel
- Support three enum sources: inline, inferred, external
- Add keybind to open enum picker (e.g., 'e')
- Handle enum changes (update value, optionally trigger on_change script)

## Impact
- Affected specs: None (new capability)
- Affected code: ui.py, handlers.py modules
