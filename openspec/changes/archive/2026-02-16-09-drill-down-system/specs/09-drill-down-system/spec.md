## ADDED Requirements
### Requirement: Drillable Cell Detection
The system SHALL detect cells containing arrays or nested objects.

#### Scenario: Detect array cell
- **GIVEN** a cell contains `[{"name": "a"}, {"name": "b"}]`
- **WHEN** table is rendered
- **THEN** cell is marked as drillable

#### Scenario: Detect object cell
- **GIVEN** a cell contains `{"nested": "data"}`
- **WHEN** table is rendered
- **THEN** cell is marked as drillable

#### Scenario: Primitive cell not drillable
- **GIVEN** a cell contains "hello" or 42
- **WHEN** table is rendered
- **THEN** cell is not marked as drillable

### Requirement: Drillable Cell Indicator
The system SHALL provide visual indication for drillable cells.

#### Scenario: Drillable indicator
- **GIVEN** a cell is drillable
- **WHEN** table is rendered
- **THEN** cell shows indicator (e.g., special color, arrow marker, or brackets)

### Requirement: Drill-Down Action
The system SHALL support drilling into nested data.

#### Scenario: Drill into array
- **GIVEN** cell mode with selected drillable cell containing array
- **WHEN** user presses Enter
- **THEN** view shows the array elements as rows

#### Scenario: Drill into object
- **GIVEN** cell mode with selected drillable cell containing object
- **WHEN** user presses Enter
- **THEN** view shows object keys as columns

### Requirement: Drill-Down Configuration
The system SHALL support configuration for drill-down behavior.

#### Scenario: Custom drill-down field
- **GIVEN** config has `drill_down: {"field": "items"}`
- **WHEN** user drills into a row
- **THEN** array from "items" field is displayed

#### Scenario: Inherit flags
- **GIVEN** config has `drill_down: {"inherit_flags": true}`
- **WHEN** user drills into a cell
- **THEN** parent CLI flags are passed to child view

#### Scenario: Extra flags
- **GIVEN** config has `drill_down: {"extra_flags": ["--filtered"]}`
- **WHEN** user drills into a cell
- **THEN** "--filtered" flag is added to child view

#### Scenario: New tab drill-down
- **GIVEN** config has `drill_down: {"new_tab": true}`
- **WHEN** user drills into a cell
- **THEN** new tab is created with nested data

### Requirement: Navigation Stack
The system SHALL maintain navigation stack for back functionality.

#### Scenario: Navigate back
- **GIVEN** user has drilled into nested data
- **WHEN** user presses back key (e.g., ESC in drill-down view)
- **THEN** view returns to parent level

#### Scenario: Navigate back multiple levels
- **GIVEN** user has drilled 3 levels deep
- **WHEN** user presses back key 3 times
- **THEN** view returns to original top level

### Requirement: Navigation Indicator
The system SHALL display indicator when in drill-down view.

#### Scenario: Navigation depth indicator
- **GIVEN** user is 2 levels deep
- **WHEN** table is rendered
- **THEN** header shows navigation indicator (e.g., "Level 2/3")

### Requirement: Parent Data Context
The system SHALL pass parent data context to child view.

#### Scenario: Parent context available
- **GIVEN** parent row has `{"id": 1, "name": "test"}`
- **WHEN** user drills into nested data
- **THEN** child view has access to parent context for triggers/actions
