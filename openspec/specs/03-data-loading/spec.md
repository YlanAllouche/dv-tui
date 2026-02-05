# 03-data-loading Specification

## Purpose
TBD - created by archiving change 03-data-loading. Update Purpose after archive.
## Requirements
### Requirement: JSON Data Loading
The system SHALL load JSON data from files or inline input.

#### Scenario: Load JSON file
- **WHEN** user runs `dv data.json`
- **THEN** JSON data from data.json is parsed and displayed

#### Scenario: Load inline JSON
- **WHEN** user runs `dv -c '[{"a":1},{"a":2}]'`
- **THEN** inline JSON is parsed and displayed

### Requirement: CSV Data Loading
The system SHALL load and parse CSV data for read-only display.

#### Scenario: Load CSV file
- **WHEN** user runs `dv data.csv`
- **THEN** CSV data is parsed with first row as headers and displayed

#### Scenario: Custom CSV delimiter
- **GIVEN** data.csv uses semicolon as delimiter
- **WHEN** user runs `dv data.csv --delimiter ';'`
- **THEN** CSV is correctly parsed using semicolon delimiter

### Requirement: Stdin Data Loading
The system SHALL load data from stdin with configurable timeout.

#### Scenario: Load from stdin with default timeout
- **WHEN** data is piped to dv via stdin
- **THEN** data is read with 30-second timeout

#### Scenario: Load from stdin with custom timeout
- **WHEN** user runs `dv --stdin-timeout 60`
- **THEN** data is read from stdin with 60-second timeout

#### Scenario: Load from stdin without timeout
- **WHEN** user runs `dv --no-stdin-timeout`
- **THEN** dv waits indefinitely for stdin data

#### Scenario: Stdin with refresh command
- **WHEN** user runs `dv -c "query.sh"`
- **THEN** data can be refreshed by re-running query.sh

### Requirement: Data Validation
The system SHALL validate loaded data and provide clear error messages.

#### Scenario: Invalid JSON
- **GIVEN** data.json contains invalid JSON
- **WHEN** user runs `dv data.json`
- **THEN** error message shows parsing error location

#### Scenario: Missing columns
- **GIVEN** data has rows with different keys
- **WHEN** data is loaded
- **THEN** all keys are unioned as columns, missing cells are empty

