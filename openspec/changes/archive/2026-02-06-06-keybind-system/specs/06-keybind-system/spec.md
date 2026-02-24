## ADDED Requirements
### Requirement: Default Normal Mode Keybinds
The system SHALL provide default keybinds for normal mode.

#### Scenario: Navigation keys
- **GIVEN** normal mode
- **WHEN** user presses 'j' or 'k'
- **THEN** selection moves down or up

#### Scenario: Quit key
- **GIVEN** normal mode
- **WHEN** user presses 'q'
- **THEN** application quits

#### Scenario: Enter key
- **GIVEN** normal mode
- **WHEN** user presses Enter
- **THEN** row is selected and row action triggered

#### Scenario: Search key
- **GIVEN** normal mode
- **WHEN** user presses '/'
- **THEN** search mode is activated

#### Scenario: Yank key
- **GIVEN** normal mode
- **WHEN** user presses 'y'
- **THEN** selected cell value is yanked to clipboard

#### Scenario: Mode toggle key
- **GIVEN** normal mode
- **WHEN** user presses 'c'
- **THEN** selection mode toggles between row and cell

### Requirement: Default Search Mode Keybinds
The system SHALL provide default keybinds for search mode.

#### Scenario: Typing in search
- **GIVEN** search mode
- **WHEN** user types characters
- **THEN** search query is updated

#### Scenario: Backspace in search
- **GIVEN** search mode
- **WHEN** user presses backspace
- **THEN** last character is removed from query

#### Scenario: Enter in search
- **GIVEN** search mode
- **WHEN** user presses Enter
- **THEN** search is confirmed and first match is selected

#### Scenario: ESC in search
- **GIVEN** search mode
- **WHEN** user presses ESC
- **THEN** search mode is exited

#### Scenario: Tab in search
- **GIVEN** search mode with multiple matches
- **WHEN** user presses Tab
- **THEN** selection moves to next match

#### Scenario: Shift+Tab in search
- **GIVEN** search mode with multiple matches
- **WHEN** user presses Shift+Tab
- **THEN** selection moves to previous match

### Requirement: Default Cell Mode Keybinds
The system SHALL provide default keybinds for cell mode.

#### Scenario: Column navigation
- **GIVEN** cell mode
- **WHEN** user presses 'j' or 'k'
- **THEN** selected column moves right or left

#### Scenario: Select cell
- **GIVEN** cell mode
- **WHEN** user presses Enter
- **THEN** cell is selected and cell action triggered

### Requirement: Keybind Precedence
The system SHALL support keybind precedence: CLI flags > inline JSON > defaults.

#### Scenario: CLI overrides config
- **GIVEN** inline JSON has `keybinds.normal: {"j": "custom_down"}`
- **WHEN** user runs `dv --bind 'j:down'`
- **THEN** 'j' triggers 'down' action

#### Scenario: Config overrides defaults
- **GIVEN** default has 'j' mapped to 'down'
- **WHEN** inline JSON has `keybinds.normal: {"j": "custom_down"}`
- **THEN** 'j' triggers 'custom_down' action

### Requirement: Keybind Unbinding
The system SHALL support unbinding specific keys at different layers.

#### Scenario: Unbind via config
- **GIVEN** default has 'q' mapped to 'quit'
- **WHEN** inline JSON has `keybinds.normal: {"q": null}`
- **THEN** 'q' has no action

#### Scenario: Unbind via CLI
- **WHEN** user runs `dv --unbind 'q'`
- **THEN** 'q' has no action

### Requirement: CLI Keybind Flags
The system SHALL support adding/removing keybinds via CLI flags.

#### Scenario: Add keybind via CLI
- **WHEN** user runs `dv --bind 'ctrl+d:half_page_down'`
- **THEN** ctrl+d triggers half_page_down action

#### Scenario: Remove keybind via CLI
- **WHEN** user runs `dv --unbind 'q'`
- **THEN** 'q' has no action
