# 02-configuration-system Specification

## Purpose
TBD - created by archiving change 02-configuration-system. Update Purpose after archive.
## Requirements
### Requirement: Layered Configuration
The system SHALL support configuration from multiple sources with precedence: CLI flags > inline JSON config > defaults.

#### Scenario: CLI flags override JSON config
- **GIVEN** inline JSON config sets `columns: ["a", "b"]`
- **WHEN** user runs `dv --columns b a`
- **THEN** displayed columns are `["b", "a"]`

#### Scenario: Inline JSON config overrides defaults
- **GIVEN** default keybind for "down" is "j"
- **WHEN** inline JSON config has `keybinds.normal: {"j": "custom_action"}`
- **THEN** "j" key triggers custom_action

### Requirement: Configuration Schema
The system SHALL support a JSON configuration schema with sections for columns, keybinds, triggers, enums, drill-down, refresh, and tabs.

#### Scenario: Columns configuration
- **GIVEN** data has columns `["a", "b", "c", "d"]`
- **WHEN** inline JSON has `_config.columns: ["d", "a"]`
- **THEN** only columns `["d", "a"]` are displayed in that order

#### Scenario: Keybinds configuration
- **GIVEN** default keybinds for normal mode include `"j": "down"`
- **WHEN** inline JSON has `_config.keybinds.normal: {"j": "next_item", "ctrl+n": "down"}`
- **THEN** "j" triggers next_item, ctrl+n triggers down

#### Scenario: Triggers configuration
- **GIVEN** inline JSON has `_config.triggers.rows.on_enter: "edit.sh"`
- **WHEN** user presses Enter on a row
- **THEN** edit.sh is executed with row data

#### Scenario: Enum configuration
- **GIVEN** inline JSON has `_config.enum.status: {"source": "inline", "values": ["active", "pending"]}`
- **WHEN** user opens enum picker for status column
- **THEN** options are "active" and "pending"

#### Scenario: Drill-down configuration
- **GIVEN** inline JSON has `_config.drill_down: {"field": "items"}`
- **WHEN** user drills into a cell containing array in "items" field
- **THEN** nested data is displayed

#### Scenario: Refresh configuration
- **GIVEN** inline JSON has `_config.refresh: {"command": "query.sh"}`
- **WHEN** refresh is triggered
- **THEN** query.sh is executed to regenerate data

#### Scenario: Tabs configuration
- **GIVEN** inline JSON has `_config.tabs: ["file1.json", "file2.json"]`
- **WHEN** dv starts
- **THEN** two tabs are created with data from those files

### Requirement: External Config File
The system SHALL support loading configuration from an external file via `--config` flag.

#### Scenario: External config file
- **WHEN** user runs `dv --config my-config.json`
- **THEN** configuration is loaded from my-config.json and merged with CLI flags

### Requirement: Help Documentation
The system SHALL provide help documentation via `--help` flag showing all available options.

#### Scenario: Display help
- **WHEN** user runs `dv --help`
- **THEN** all available CLI flags and their descriptions are shown

