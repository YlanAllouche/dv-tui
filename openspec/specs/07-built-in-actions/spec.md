# 07-built-in-actions Specification

## Purpose
TBD - created by archiving change 07-built-in-actions. Update Purpose after archive.
## Requirements
### Requirement: Scroll Actions
The system SHALL provide scroll actions for navigation.

#### Scenario: Scroll down
- **GIVEN** data has 100 rows and 20 visible
- **WHEN** scroll_down action is triggered
- **THEN** view scrolls down one row if possible

#### Scenario: Scroll up
- **GIVEN** scroll offset is 10
- **WHEN** scroll_up action is triggered
- **THEN** scroll offset decreases to 9 if possible

### Requirement: Selection Actions
The system SHALL provide actions for selecting rows and cells.

#### Scenario: Select row
- **GIVEN** row 5 exists
- **WHEN** select_row(5) action is triggered
- **THEN** selected_row is 5 and view scrolls to show row 5

#### Scenario: Select cell
- **GIVEN** row 3, column 2 exists
- **WHEN** select_cell(3, 2) action is triggered
- **THEN** selected_row is 3, selected_column is 2, and cell mode is activated

### Requirement: Selection Mode Toggle
The system SHALL provide action to toggle between row and cell selection modes.

#### Scenario: Toggle to cell mode
- **GIVEN** current mode is 'row'
- **WHEN** toggle_selection_mode action is triggered
- **THEN** mode changes to 'cell'

#### Scenario: Toggle to row mode
- **GIVEN** current mode is 'cell'
- **WHEN** toggle_selection_mode action is triggered
- **THEN** mode changes to 'row'

### Requirement: Search Actions
The system SHALL provide actions for search functionality.

#### Scenario: Enter search
- **WHEN** enter_search action is triggered
- **THEN** search mode is activated and footer shows search prompt

#### Scenario: Exit search
- **GIVEN** search mode is active
- **WHEN** exit_search action is triggered
- **THEN** search mode is exited and view returns to normal

#### Scenario: Search navigate next
- **GIVEN** search mode with multiple matches
- **WHEN** search_navigate(1) action is triggered
- **THEN** selection moves to next match

#### Scenario: Search navigate previous
- **GIVEN** search mode with multiple matches
- **WHEN** search_navigate(-1) action is triggered
- **THEN** selection moves to previous match

### Requirement: Yank Cell Action
The system SHALL provide action to copy cell value to clipboard.

#### Scenario: Yank with xclip available
- **GIVEN** xclip is installed and selected cell contains "hello"
- **WHEN** yank_cell action is triggered
- **THEN** "hello" is copied to clipboard using xclip

#### Scenario: Yank with wl-copy available
- **GIVEN** wl-copy is installed and selected cell contains "hello"
- **WHEN** yank_cell action is triggered
- **THEN** "hello" is copied to clipboard using wl-copy

#### Scenario: Yank with pbcopy available
- **GIVEN** pbcopy is installed and selected cell contains "hello"
- **WHEN** yank_cell action is triggered
- **THEN** "hello" is copied to clipboard using pbcopy

#### Scenario: Yank without clipboard tool
- **GIVEN** no clipboard tool is installed
- **WHEN** yank_cell action is triggered
- **THEN** error message "No clipboard tool available (xclip/wl-copy/pbcopy)" is shown

### Requirement: Show Message Action
The system SHALL provide action to display temporary popup messages.

#### Scenario: Show info message
- **WHEN** show_message("Data refreshed") action is triggered
- **THEN** popup shows "Data refreshed" for 2 seconds then dismisses

### Requirement: Refresh Data Action
The system SHALL provide action to refresh data from source.

#### Scenario: Refresh file data
- **GIVEN** data was loaded from file.json
- **WHEN** refresh_data action is triggered
- **THEN** data is reloaded from file.json

#### Scenario: Refresh stdin with command
- **GIVEN** data was loaded via stdin with `-c "query.sh"`
- **WHEN** refresh_data action is triggered
- **THEN** query.sh is re-executed to regenerate data

#### Scenario: Refresh stdin without command
- **GIVEN** data was loaded via stdin without `-c` flag
- **WHEN** refresh_data action is triggered
- **THEN** warning message "Cannot refresh piped data without command" is shown

### Requirement: Quit Action
The system SHALL provide action to quit the application.

#### Scenario: Quit application
- **WHEN** quit action is triggered
- **THEN** application exits cleanly

