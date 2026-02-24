# 17-cleanup Specification

## Purpose
TBD - created by archiving change 17-cleanup. Update Purpose after archive.
## Requirements
### Requirement: Remove Nvim Integration
The system SHALL not contain hardcoded nvim integration logic.

#### Scenario: Nvim integration as example
- **GIVEN** nvim integration was previously hardcoded
- **WHEN** code is cleaned up
- **THEN** open_in_nvim_async method is removed and example config shows how to add it

### Requirement: Remove Play Locator Integration
The system SHALL not contain hardcoded play_locator integration logic.

#### Scenario: Play locator as example
- **GIVEN** play_locator integration was previously hardcoded
- **WHEN** code is cleaned up
- **THEN** jelly_play_yt command is removed and example config shows how to add it

### Requirement: Remove Hardcoded Field Expectations
The system SHALL not have hardcoded expectations about specific field names.

#### Scenario: Generic column handling
- **GIVEN** data has arbitrary column names
- **WHEN** table is rendered
- **THEN** all columns are displayed regardless of name

### Requirement: Make Color Mappings Configurable
The system SHALL support configurable color mappings instead of hardcoded colors.

#### Scenario: Configurable colors
- **GIVEN** config has color mappings
- **WHEN** table is rendered
- **THEN** colors from config are used

### Requirement: Remove Debug Logging
The system SHALL not write debug logs to /tmp files.

#### Scenario: No debug files
- **WHEN** dv is running
- **THEN** no /tmp/dv_keys.txt or /tmp/dv_play.log files are created

### Requirement: Improved Error Messages
The system SHALL provide clear, actionable error messages.

#### Scenario: Clear file not found error
- **GIVEN** user runs `dv nonexistent.json`
- **WHEN** file is not found
- **THEN** error message clearly states file not found and suggests checking path

### Requirement: Type Hints
The system SHALL include type hints for all public functions and methods.

#### Scenario: Function with type hints
- **GIVEN** function loads data
- **WHEN** viewing source code
- **THEN** function signature includes parameter and return type hints

#### Scenario: Method with type hints
- **GIVEN** method in class
- **WHEN** viewing source code
- **THEN** method signature includes parameter and return type hints

### Requirement: Clear Variable Names
The system SHALL use clear, descriptive variable names.

#### Scenario: Descriptive names
- **GIVEN** variable holds current row index
- **WHEN** viewing source code
- **THEN** variable is named something descriptive (e.g., current_row_index)

### Requirement: Remove Unused Code
The system SHALL not contain unused code or imports.

#### Scenario: No unused imports
- **WHEN** viewing source code
- **THEN** all imported modules are actually used

#### Scenario: No unused functions
- **WHEN** viewing source code
- **THEN** all defined functions are actually called

