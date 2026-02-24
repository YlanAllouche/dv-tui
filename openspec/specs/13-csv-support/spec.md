# 13-csv-support Specification

## Purpose
TBD - created by archiving change 13-csv-support. Update Purpose after archive.
## Requirements
### Requirement: CSV File Detection
The system SHALL detect CSV files by extension.

#### Scenario: Load CSV file
- **GIVEN** data.csv exists
- **WHEN** user runs `dv data.csv`
- **THEN** CSV data is parsed and displayed

### Requirement: CSV Delimiter Detection
The system SHALL use comma as default delimiter with support for custom delimiters.

#### Scenario: Default comma delimiter
- **GIVEN** data.csv uses comma delimiter
- **WHEN** user runs `dv data.csv`
- **THEN** CSV is correctly parsed with comma delimiter

#### Scenario: Custom semicolon delimiter
- **GIVEN** data.csv uses semicolon delimiter
- **WHEN** user runs `dv data.csv --delimiter ';'`
- **THEN** CSV is correctly parsed with semicolon delimiter

### Requirement: CSV Header Handling
The system SHALL treat first row as headers by default with option to skip.

#### Scenario: Default header parsing
- **GIVEN** data.csv has headers in first row
- **WHEN** user runs `dv data.csv`
- **THEN** first row is used as column headers

#### Scenario: Skip headers
- **WHEN** user runs `dv data.csv --no-headers`
- **THEN** first row is treated as data, columns are numbered

### Requirement: CSV to Table Conversion
The system SHALL convert CSV data to internal table format.

#### Scenario: Convert CSV rows
- **GIVEN** CSV has headers "name,age" and rows "Alice,30", "Bob,25"
- **WHEN** CSV is loaded
- **THEN** data is converted to `[{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]`

### Requirement: CSV Feature Parity
The system SHALL support same features for CSV as JSON.

#### Scenario: Search CSV data
- **GIVEN** CSV data is loaded
- **WHEN** user searches for "Alice"
- **THEN** rows with "Alice" are filtered

#### Scenario: Select CSV rows
- **GIVEN** CSV data is loaded
- **WHEN** user selects a row
- **THEN** row is highlighted and can trigger actions

#### Scenario: CSV triggers
- **GIVEN** CSV data is loaded with trigger configured
- **WHEN** trigger event occurs
- **THEN** trigger is executed with CSV row data

### Requirement: CSV Read-Only Limitation
The system SHALL indicate CSV is read-only and does not support editing or CSV export.

#### Scenario: CSV read-only
- **GIVEN** CSV data is loaded
- **WHEN** user attempts to edit data
- **THEN** error message indicates CSV is read-only

#### Scenario: No CSV export
- **GIVEN** CSV data is loaded and modified in memory
- **WHEN** export is attempted
- **THEN** error message indicates CSV export not supported

