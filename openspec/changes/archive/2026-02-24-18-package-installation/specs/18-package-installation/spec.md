## ADDED Requirements
### Requirement: Package Metadata
The system SHALL provide complete package metadata in pyproject.toml.

#### Scenario: Package name
- **GIVEN** pyproject.toml exists
- **WHEN** user views metadata
- **THEN** package name is specified (e.g., "dv-tui")

#### Scenario: Package version
- **GIVEN** pyproject.toml exists
- **WHEN** user views metadata
- **THEN** version is specified following semantic versioning

#### Scenario: Package description
- **GIVEN** pyproject.toml exists
- **WHEN** user views metadata
- **THEN** description clearly explains what the package does

### Requirement: Dependencies
The system SHALL declare dependencies in pyproject.toml.

#### Scenario: Minimal dependencies
- **GIVEN** pyproject.toml exists
- **WHEN** user views dependencies
- **THEN** only required dependencies are listed (curses is stdlib)

#### Scenario: Optional dependencies
- **GIVEN** optional features exist
- **WHEN** user views dependencies
- **THEN** extras are defined for optional features

### Requirement: CLI Entry Point
The system SHALL configure CLI entry point in pyproject.toml.

#### Scenario: Entry point configuration
- **GIVEN** pyproject.toml exists
- **WHEN** user views entry points
- **THEN** dv command is configured to point to dv_tui.cli:main

### Requirement: Installation
The system SHALL support installation via pip.

#### Scenario: Editable install
- **WHEN** user runs `pip install -e .`
- **THEN** package is installed in editable mode and dv command works

#### Scenario: Regular install
- **WHEN** user runs `pip install .`
- **THEN** package is installed and dv command works

### Requirement: License File
The system SHALL include a LICENSE file.

#### Scenario: License exists
- **GIVEN** repository root exists
- **WHEN** user views files
- **THEN** LICENSE file is present with appropriate license text

### Requirement: Version in __init__.py
The system SHALL define version in dv_tui/__init__.py.

#### Scenario: Version accessible
- **GIVEN** dv_tui is installed
- **WHEN** user executes `import dv_tui; print(dv_tui.__version__)`
- **THEN** version string is displayed

### Requirement: Changelog
The system SHALL include a CHANGELOG.md documenting changes.

#### Scenario: Changelog exists
- **GIVEN** repository root exists
- **WHEN** user views files
- **THEN** CHANGELOG.md is present with version history

#### Scenario: Changelog format
- **GIVEN** CHANGELOG.md exists
- **WHEN** user views content
- **THEN** entries are organized by version with dates and change descriptions

### Requirement: Tests Pass
The system SHALL ensure all tests pass before distribution.

#### Scenario: Run all tests
- **WHEN** user runs `pytest`
- **THEN** all tests pass without errors

### Requirement: Dependency Documentation
The system SHALL document dependencies in README.

#### Scenario: Dependencies in README
- **GIVEN** README.md exists
- **WHEN** user views README
- **THEN** dependencies section lists required and optional dependencies
