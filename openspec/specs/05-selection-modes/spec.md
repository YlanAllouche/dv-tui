# 05-selection-modes Specification

## Purpose
TBD - created by archiving change 05-selection-modes. Update Purpose after archive.
## Requirements
### Requirement: Row Selection Mode
The system SHALL support row selection as the default mode.

#### Scenario: Default row mode
- **WHEN** dv starts
- **THEN** selection mode is 'row'

#### Scenario: Select row
- **GIVEN** row 2 is visible
- **WHEN** user presses Enter on row 2
- **THEN** entire row 2 is selected and row-level action is triggered

### Requirement: Cell Selection Mode
The system SHALL support cell-level selection.

#### Scenario: Enter cell mode
- **GIVEN** selection mode is 'row'
- **WHEN** user presses 'c' (toggle mode keybind)
- **THEN** selection mode changes to 'cell' and a column is selected

#### Scenario: Navigate cells
- **GIVEN** selection mode is 'cell'
- **WHEN** user presses 'j' or 'k'
- **THEN** selected column changes (not selected row)

#### Scenario: Select cell
- **GIVEN** selection mode is 'cell' and cell at row 2, column 3 is selected
- **WHEN** user presses Enter
- **THEN** cell at (2, 3) is selected and cell-level action is triggered

### Requirement: Cell Visual Indicator
The system SHALL provide visual indication of selected cell in cell mode.

#### Scenario: Cell highlight
- **GIVEN** selection mode is 'cell'
- **WHEN** table is rendered
- **THEN** selected cell has distinct visual indicator (e.g., reverse colors, brackets)

### Requirement: Mode Toggle Keybind
The system SHALL provide a keybind to toggle between row and cell modes.

#### Scenario: Toggle to cell mode
- **GIVEN** selection mode is 'row'
- **WHEN** user presses 'c'
- **THEN** selection mode changes to 'cell'

#### Scenario: Toggle to row mode
- **GIVEN** selection mode is 'cell'
- **WHEN** user presses 'c'
- **THEN** selection mode changes to 'row'

#### Scenario: Configurable toggle keybind
- **GIVEN** config sets `keybinds.normal: {"v": "toggle_mode"}`
- **WHEN** user presses 'v'
- **THEN** selection mode toggles

### Requirement: Context-Aware Footer Hints
The system SHALL update footer hints based on current selection mode.

#### Scenario: Row mode hints
- **GIVEN** selection mode is 'row'
- **WHEN** table is rendered
- **THEN** footer shows row mode hints (e.g., "Enter: select row, c: cell mode")

#### Scenario: Cell mode hints
- **GIVEN** selection mode is 'cell'
- **WHEN** table is rendered
- **THEN** footer shows cell mode hints (e.g., "Enter: select cell, j/k: change column")

