## ADDED Requirements
### Requirement: Enum Choice Dialog
The system SHALL provide a popup dialog for enum selection.

#### Scenario: Open enum picker
- **GIVEN** enum is configured for "status" column
- **WHEN** user presses 'e' in cell mode on status cell
- **THEN** enum choice dialog opens with options

#### Scenario: Enum picker display
- **GIVEN** enum options are ["active", "pending", "inactive"]
- **WHEN** enum choice dialog is open
- **THEN** options are listed with first option highlighted

### Requirement: Enum Picker Navigation
The system SHALL support arrow key navigation in enum picker.

#### Scenario: Navigate down
- **GIVEN** enum picker is open with first option highlighted
- **WHEN** user presses down arrow
- **THEN** second option is highlighted

#### Scenario: Navigate up
- **GIVEN** enum picker is open with second option highlighted
- **WHEN** user presses up arrow
- **THEN** first option is highlighted

### Requirement: Enum Picker Selection
The system SHALL support Enter to select and ESC to cancel.

#### Scenario: Select option
- **GIVEN** enum picker is open with "pending" highlighted
- **WHEN** user presses Enter
- **THEN** cell value updates to "pending" and dialog closes

#### Scenario: Cancel selection
- **GIVEN** enum picker is open
- **WHEN** user presses ESC
- **THEN** dialog closes without changing value

### Requirement: Inline Enum Source
The system SHALL support inline enum values defined in config.

#### Scenario: Inline enum
- **GIVEN** config has `enum: {"status": {"source": "inline", "values": ["active", "pending"]}}`
- **WHEN** enum picker is opened for status cell
- **THEN** options are "active" and "pending"

### Requirement: Inferred Enum Source
The system SHALL support inferring enum values from column data.

#### Scenario: Inferred enum
- **GIVEN** config has `enum: {"status": {"source": "inferred"}}`
- **GIVEN** status column values are ["active", "pending", "active", "inactive"]
- **WHEN** enum picker is opened for status cell
- **THEN** unique options are "active", "pending", "inactive" (deduplicated)

### Requirement: External Enum Source
The system SHALL support loading enum options from external command.

#### Scenario: External enum
- **GIVEN** config has `enum: {"status": {"source": "external", "command": "get_statuses.sh"}}`
- **WHEN** enum picker is opened for status cell
- **THEN** options are output of get_statuses.sh command

### Requirement: Enum Change Triggers
The system SHALL trigger on_change script after enum change if configured.

#### Scenario: Enum change with trigger
- **GIVEN** status cell has on_change trigger configured
- **WHEN** user selects "active" in enum picker
- **THEN** cell value updates to "active" and on_change script is executed

### Requirement: Configurable Enum Picker Keybind
The system SHALL support configurable keybind for opening enum picker.

#### Scenario: Custom enum picker keybind
- **GIVEN** config has `keybinds.normal: {"e": "other_action", "E": "open_enum"}`
- **WHEN** user presses 'E'
- **THEN** enum picker opens
