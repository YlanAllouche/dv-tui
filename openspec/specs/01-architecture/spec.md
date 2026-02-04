# 01-architecture Specification

## Purpose
TBD - created by archiving change 01-architecture. Update Purpose after archive.
## Requirements
### Requirement: Package Structure
The system SHALL be organized as a proper Python package with modular components.

#### Scenario: Package installation
- **WHEN** user runs `pip install -e .`
- **THEN** dv-tui is installed as a package with `dv` command available

#### Scenario: Module imports
- **WHEN** importing `import dv_tui`
- **THEN** all public components are accessible

### Requirement: Module Separation
Each module SHALL have a single, well-defined responsibility.

#### Scenario: CLI module
- **WHEN** running `dv` command
- **THEN** cli.py handles argument parsing and entry point delegation

#### Scenario: Core module
- **WHEN** TUI needs to initialize
- **THEN** core.py provides TUI engine and curses wrapper

#### Scenario: Config module
- **WHEN** loading configuration
- **THEN** config.py handles all config loading and merging logic

#### Scenario: Data loaders module
- **WHEN** loading data from source
- **THEN** data_loaders.py provides unified interface for JSON/CSV/stdin

#### Scenario: Actions module
- **WHEN** executing a built-in action
- **THEN** actions.py contains all built-in action implementations

#### Scenario: Triggers module
- **WHEN** a trigger fires
- **THEN** triggers.py handles trigger execution and data passing

