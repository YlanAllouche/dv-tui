# Change: Implement Python Library API

## Why
Provide simple, high-level API for using dv-tui as a Python library for programmatic integration.

## What Changes
- Define main API in __init__.py
- Implement TableUI class for library usage
- Support keybinding with method calls
- Expose configuration options via constructor arguments
- Support programmatic data updates
- Provide event callbacks for TUI events
- Clear distinction between CLI and library usage

## Impact
- Affected specs: None (new capability)
- Affected code: __init__.py, core.py modules
