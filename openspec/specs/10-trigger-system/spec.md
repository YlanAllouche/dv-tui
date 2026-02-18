# 10-trigger-system Specification

## Purpose
TBD - created by archiving change 10-trigger-system. Update Purpose after archive.
## Requirements
### Requirement: Trigger Schema
The system SHALL support a trigger schema for table, row, and cell events.

#### Scenario: Table-level trigger
- **GIVEN** inline JSON has `_config.triggers.table.on_select: "process.sh"`
- **WHEN** table selection changes
- **THEN** process.sh is executed

#### Scenario: Row-level trigger
- **GIVEN** inline JSON has `_config.triggers.rows.on_enter: {"script": "edit.sh", "data": "row"}`
- **WHEN** user presses Enter on a row
- **THEN** edit.sh is executed with row data

#### Scenario: Cell-level trigger
- **GIVEN** inline JSON has `_config.triggers.cells.status.on_change: "update.sh"`
- **WHEN** cell in "status" column changes
- **THEN** update.sh is executed with cell data

### Requirement: Environment Variables
The system SHALL pass environment variables to trigger scripts.

#### Scenario: DV_SELECTED_ROW variable
- **GIVEN** selected row is `{"id": 1, "name": "test"}`
- **WHEN** trigger is executed
- **THEN** DV_SELECTED_ROW environment variable contains `{"id": 1, "name": "test"}`

#### Scenario: DV_SELECTED_CELL variable
- **GIVEN** cell mode with selected cell containing "hello"
- **WHEN** trigger is executed
- **THEN** DV_SELECTED_CELL environment variable contains "hello"

#### Scenario: DV_SELECTED_INDEX variable
- **GIVEN** selected row index is 5
- **WHEN** trigger is executed
- **THEN** DV_SELECTED_INDEX environment variable contains "5"

#### Scenario: DV_SELECTED_COLUMN variable
- **GIVEN** cell mode with selected column "name"
- **WHEN** trigger is executed
- **THEN** DV_SELECTED_COLUMN environment variable contains "name"

### Requirement: Sync vs Async Execution
The system SHALL support both synchronous and asynchronous trigger execution.

#### Scenario: Synchronous execution (default)
- **GIVEN** trigger is configured without async flag
- **WHEN** trigger fires
- **THEN** execution blocks until script completes

#### Scenario: Asynchronous execution
- **GIVEN** trigger is configured with async flag
- **WHEN** trigger fires
- **THEN** execution continues immediately, script runs in background

### Requirement: Trigger Priority
The system SHALL execute triggers with priority: cell (in cell mode) > row > table.

#### Scenario: Cell trigger has priority over row
- **GIVEN** cell mode with cell-level and row-level triggers on same event
- **WHEN** event fires
- **THEN** only cell-level trigger is executed

#### Scenario: Row trigger has priority over table
- **GIVEN** row-level and table-level triggers on same event
- **WHEN** event fires
- **THEN** only row-level trigger is executed

#### Scenario: Row mode falls back to row trigger
- **GIVEN** row mode with cell-level and row-level triggers
- **WHEN** event fires
- **THEN** only row-level trigger is executed (not cell)

### Requirement: Python Function Triggers
The system SHALL support Python function triggers for library usage.

#### Scenario: Bind Python function to trigger
- **GIVEN** using dv-tui as library
- **WHEN** user calls `tui.bind_trigger('on_enter', my_function)`
- **THEN** on_enter event calls my_function with selected data

### Requirement: Trigger Error Handling
The system SHALL handle trigger errors gracefully.

#### Scenario: Script execution error
- **GIVEN** trigger script exits with error
- **WHEN** trigger fires
- **THEN** error message is shown but TUI continues running

#### Scenario: Script not found
- **GIVEN** trigger script does not exist
- **WHEN** trigger fires
- **THEN** error message shows script not found

