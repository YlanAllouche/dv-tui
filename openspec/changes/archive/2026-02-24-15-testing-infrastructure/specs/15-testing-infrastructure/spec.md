## ADDED Requirements
### Requirement: Test Framework
The system SHALL use pytest for testing.

#### Scenario: Run all tests
- **WHEN** user runs `pytest`
- **THEN** all tests are executed and results are displayed

#### Scenario: Run specific test file
- **WHEN** user runs `pytest tests/test_config.py`
- **THEN** only config tests are executed

### Requirement: Config Tests
The system SHALL have unit tests for configuration loading and merging.

#### Scenario: Test config loading
- **GIVEN** config has columns and keybinds
- **WHEN** config is loaded
- **THEN** test verifies columns and keybinds are correctly parsed

#### Scenario: Test config precedence
- **GIVEN** defaults, inline JSON, and CLI flags exist
- **WHEN** config is merged
- **THEN** test verifies CLI > inline > defaults precedence

### Requirement: Data Loader Tests
The system SHALL have unit tests for data loading.

#### Scenario: Test JSON loading
- **GIVEN** valid JSON file
- **WHEN** JsonDataLoader loads it
- **THEN** test verifies data is correctly parsed

#### Scenario: Test CSV loading
- **GIVEN** valid CSV file
- **WHEN** CsvDataLoader loads it
- **THEN** test verifies data is correctly parsed with headers

#### Scenario: Test stdin loading
- **GIVEN** simulated stdin data
- **WHEN** StdinDataLoader loads it
- **THEN** test verifies data is correctly captured

### Requirement: Fuzzy Match Tests
The system SHALL have unit tests for fuzzy matching logic.

#### Scenario: Test exact match
- **GIVEN** query "test" and text "test"
- **WHEN** fuzzy_match is called
- **THEN** test returns (True, 0.0)

#### Scenario: Test fuzzy match
- **GIVEN** query "tst" and text "test"
- **WHEN** fuzzy_match is called
- **THEN** test returns (True, score > 0)

#### Scenario: Test no match
- **GIVEN** query "xyz" and text "test"
- **WHEN** fuzzy_match is called
- **THEN** test returns (False, infinity)

### Requirement: Trigger Tests
The system SHALL have unit tests for trigger execution.

#### Scenario: Test shell trigger
- **GIVEN** shell trigger configured
- **WHEN** trigger fires
- **THEN** test verifies command is executed

#### Scenario: Test environment variables
- **GIVEN** trigger configured
- **WHEN** trigger fires
- **THEN** test verifies DV_SELECTED_ROW and other env vars are set

### Requirement: Clipboard Tests
The system SHALL have unit tests for clipboard operations.

#### Scenario: Test clipboard auto-detection
- **GIVEN** system with xclip installed
- **WHEN** Clipboard utility initializes
- **THEN** test verifies xclip is detected

#### Scenario: Test clipboard fallback
- **GIVEN** system without clipboard tools
- **WHEN** Clipboard utility attempts to copy
- **THEN** test verifies error is raised

### Requirement: Curses Mocking
The system SHALL provide utilities for mocking curses in tests.

#### Scenario: Mock curses for TUI testing
- **GIVEN** test needs to verify TUI rendering
- **WHEN** curses is mocked
- **THEN** test can verify rendering without actual terminal

### Requirement: E2E Test Scenarios
The system SHALL have E2E tests for key features.

#### Scenario: Basic table display test
- **GIVEN** JSON data file
- **WHEN** TUI is initialized with mocked curses
- **THEN** test verifies table is rendered correctly

#### Scenario: Multi-tab navigation test
- **GIVEN** tabs configured with 3 files
- **WHEN** user navigates between tabs
- **THEN** test verifies correct tab is active and data displayed

#### Scenario: Search and filter test
- **GIVEN** table with 100 rows
- **WHEN** user searches for query
- **THEN** test verifies filtered results are correct

#### Scenario: Cell/row selection modes test
- **GIVEN** table with data
- **WHEN** user toggles between row and cell mode
- **THEN** test verifies mode changes and selection behavior

#### Scenario: Drill-down test
- **GIVEN** table with nested array data
- **WHEN** user drills into array
- **THEN** test verifies nested data is displayed

#### Scenario: Trigger execution test
- **GIVEN** trigger configured with mocked command
- **WHEN** trigger fires
- **THEN** test verifies command is called with correct arguments

#### Scenario: CSV parsing test
- **GIVEN** CSV file with headers
- **WHEN** CsvDataLoader loads it
- **THEN** test verifies data structure matches expectations

#### Scenario: Config merging test
- **GIVEN** multiple config sources
- **WHEN** config is merged
- **THEN** test verifies final config respects precedence rules
