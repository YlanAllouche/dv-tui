## ADDED Requirements
### Requirement: Library Entry Point
The system SHALL provide a TableUI class for library usage.

#### Scenario: Import and create TUI
- **WHEN** user executes `from dv_tui import TableUI; tui = TableUI(data=[{"a":1}])`
- **THEN** TableUI instance is created with provided data

### Requirement: Data Constructor Argument
The TableUI constructor SHALL accept data as argument.

#### Scenario: Pass data to constructor
- **WHEN** user executes `TableUI(data=[{"name": "Alice"}, {"name": "Bob"}])`
- **THEN** TUI is initialized with that data

### Requirement: Keybinding API
The system SHALL provide method for binding keys to Python functions.

#### Scenario: Bind Enter key
- **WHEN** user executes `tui.bind_key('Enter', my_handler)`
- **THEN** pressing Enter calls my_handler with selected data

#### Scenario: Handler receives row data
- **GIVEN** row `{"id": 1, "name": "test"}` is selected
- **WHEN** handler is called
- **THEN** handler receives the row data as argument

### Requirement: Trigger Binding API
The system SHALL provide method for binding triggers to Python functions.

#### Scenario: Bind on_enter trigger
- **WHEN** user executes `tui.bind_trigger('on_enter', my_trigger_fn)`
- **THEN** on_enter events call my_trigger_fn with event data

### Requirement: Configuration Constructor Arguments
The TableUI constructor SHALL accept configuration options as arguments.

#### Scenario: Set columns via constructor
- **WHEN** user executes `TableUI(data=data, columns=["name", "age"])`
- **THEN** only those columns are displayed

#### Scenario: Set keybinds via constructor
- **WHEN** user executes `TableUI(data=data, keybinds={"normal": {"j": "custom_down"}})`
- **THEN** custom keybinds are applied

### Requirement: Programmatic Data Updates
The system SHALL support updating data programmatically.

#### Scenario: Update data
- **WHEN** user executes `tui.update_data([{"new": "data"}])`
- **THEN** TUI displays new data

### Requirement: Event Callbacks
The system SHALL provide callbacks for TUI events.

#### Scenario: on_quit callback
- **WHEN** user executes `tui.on_quit(lambda: print("Exiting"))`
- **THEN** callback is called when TUI exits

#### Scenario: on_mode_change callback
- **WHEN** user executes `tui.on_mode_change(lambda mode: print(f"Mode: {mode}"))`
- **THEN** callback is called when selection mode changes

#### Scenario: on_select callback
- **WHEN** user executes `tui.on_select(lambda row: print(f"Selected: {row}"))`
- **THEN** callback is called when row is selected

### Requirement: Run Method
The system SHALL provide run() method to start TUI.

#### Scenario: Start TUI
- **WHEN** user executes `tui.run()`
- **THEN** TUI starts and runs until user quits

### Requirement: CLI vs Library Separation
The system SHALL provide clear separation between CLI and library usage.

#### Scenario: CLI entry point
- **WHEN** user runs `dv data.json`
- **THEN** cli.py handles argument parsing and delegates to core.py

#### Scenario: Library entry point
- **WHEN** user imports and uses TableUI
- **THEN** core.py provides reusable TUI engine without CLI parsing
