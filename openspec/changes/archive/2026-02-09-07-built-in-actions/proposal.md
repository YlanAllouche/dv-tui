# Change: Implement Core Built-In Actions

## Why
Provide a set of core actions that work on generic data without hardcoded assumptions.

## What Changes
- Extract existing actions to actions.py module
- Implement actions: scroll_up, scroll_down, select_row, select_cell, toggle_selection_mode
- Implement search actions: enter_search, exit_search, search_navigate
- Implement yank_cell action with clipboard auto-detection
- Implement show_message action for temporary popups
- Implement refresh_data action for file/stdin
- Implement quit action
- Implement Clipboard utility with auto-detection of xclip/wl-copy/pbcopy

## Impact
- Affected specs: None (new capability)
- Affected code: actions.py, utils.py modules
