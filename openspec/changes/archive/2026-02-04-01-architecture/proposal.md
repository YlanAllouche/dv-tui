# Change: Establish Python Package Architecture

## Why
Transform the single-file `dv.py` script into a proper Python package with modular structure for maintainability and distribution.

## What Changes
- Create `dv_tui/` package directory with proper `__init__.py`
- Split responsibilities into logical modules: cli.py, core.py, table.py, config.py, handlers.py, actions.py, triggers.py, data_loaders.py, ui.py, utils.py
- Create `pyproject.toml` for package installation
- Add `dv` CLI entry point in package configuration

## Impact
- Affected specs: None (new capability)
- Affected code: Current single-file `dv.py` will be refactored into modular package structure
