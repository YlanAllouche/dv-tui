# Change: Implement Layered Configuration System

## Why
Support flexible configuration with CLI flags > inline JSON config > defaults precedence to make the tool adaptable to various use cases.

## What Changes
- Define `Config` dataclass with all configuration options
- Implement config loader that reads from multiple sources
- Implement config merger with priority rules
- Define JSON config schema for columns, keybinds, triggers, enums, drill-down, refresh, tabs
- Add CLI flags for all config options
- Implement `--config` flag for external config file

## Impact
- Affected specs: None (new capability)
- Affected code: config.py module, cli.py argument parsing
