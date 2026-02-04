# dv-tui Universalization Plan

## Phase 1: Architecture & Structure

### 1.1 Module Structure
**Spec:** Create proper Python package structure
- Create `dv_tui/` package directory
- Split responsibilities into logical modules
- Ensure `dv` CLI entry point works from installed package

**Sub-steps:**
- Create `dv_tui/__init__.py` (exports main API)
- Create `dv_tui/cli.py` (command-line argument parsing, entry point)
- Create `dv_tui/core.py` (TUI engine, curses wrapper)
- Create `dv_tui/table.py` (table rendering, data management)
- Create `dv_tui/config.py` (configuration loading, merging)
- Create `dv_tui/handlers.py` (keybind handling, mode management)
- Create `dv_tui/actions.py` (built-in actions: scroll, select, search, etc.)
- Create `dv_tui/triggers.py` (trigger execution, data passing)
- Create `dv_tui/data_loaders.py` (JSON/CSV loading, stdin handling)
- Create `dv_tui/ui.py` (UI components: headers, footers, dialogs)
- Create `dv_tui/utils.py` (color management, fuzzy match, helpers)
- Create `setup.py` or `pyproject.toml` for package installation
- Add `dv` entry point in package configuration

---

### 1.2 Configuration System
**Spec:** Support layered configuration with precedence: CLI flags > inline JSON config > defaults

**Sub-steps:**
- Define `Config` dataclass with all configuration options
- Implement config loader that reads from multiple sources
- Implement config merger with priority rules (CLI > inline > defaults)
- Define JSON config schema:
  ```json
  {
    "_config": {
      "columns": ["col1", "col2"],           // Optional: filter/reorder columns
      "keybinds": {
        "normal": {"j": "down", "k": "up"},
        "search": {"ESC": "exit_search"}
      },
      "triggers": {
        "table": {...},     // Table-level triggers
        "rows": {...},      // Row-level triggers (by value/pattern)
        "cells": {...}      // Cell-level triggers (by field/value)
      },
      "enum": {
        "status": {
          "source": "inferred",  // or "inline" or "external"
          "values": ["active", "pending"],
          "command": "get_statuses.sh"
        }
      },
      "drill_down": {
        "field": "items",
        "inherit_flags": true,
        "extra_flags": ["--filtered"]
      },
      "refresh": {
        "command": "query.sh",  // Optional: command to regenerate data
        "on_trigger": true      // Refresh after certain triggers
      },
      "tabs": ["file1.json", "file2.json"]  // Tab sources
    }
  }
  ```
- Add CLI flags for all config options
- Implement `--config` flag to load external config file
- Implement `--help` to show available options

---

## Phase 2: Core TUI Engine

### 2.1 Data Loading System
**Spec:** Support multiple data sources with unified interface

**Sub-steps:**
- Create `DataLoader` abstract base class
- Implement `JsonDataLoader` for file/inline JSON
- Implement `CsvDataLoader` for basic read-only CSV (no editing, just display)
- Implement `StdinDataLoader` for piped data with:
  - Default 30-second timeout (configurable via `--stdin-timeout` flag)
  - `--no-stdin-timeout` flag to wait indefinitely
  - Support for `-c "command"` to specify command for refresh
- Implement data validation and error handling
- Store original data source for refresh capability
- Handle missing columns: union of all keys, empty cells where missing

---

### 2.2 Table Rendering
**Spec:** Generalized table rendering with configurable columns

**Sub-steps:**
- Extract column header generation from hardcoded values
- Support dynamic column detection (union of all object keys)
- Add column filtering/reordering via config `columns` array
- Preserve current features:
  - Tab display with item counts
  - Color-coded values
  - Dynamic color cycling for enums
  - Fuzzy search mode
  - Scroll offset management
- Remove hardcoded assumptions about `type`, `status`, `summary` fields
- Make column widths configurable/calculated

---

### 2.3 Selection Modes
**Spec:** Support row selection (default) and cell mode (column selection on selected row)

**Sub-steps:**
- Add `selection_mode` state: `'row'` or `'cell'`
- In cell mode: track `selected_column` index along with `selected_row`
- Add visual indicator for selected cell in cell mode
- Enter key behavior:
  - Row mode: select entire row, trigger row-level actions
  - Cell mode: select cell, trigger cell-level actions
- Add keybind to toggle between modes (e.g., `c` or configurable)
- Update footer hints based on current mode

---

### 2.4 Keybind System
**Spec:** Mode-based keybinds with layering (CLI > inline JSON > defaults)

**Sub-steps:**
- Define default keybinds for each mode:
  - `normal`: j/k, h/l, q, Enter, /, y, c, etc.
  - `search`: typing, backspace, Enter, ESC, Tab/Shift+Tab
  - `cell`: j/k to move column, Enter to select cell
- Implement `KeybindManager` to handle:
  - Mode switching
  - Keybind lookup with precedence
  - Unbinding specific keybinds at different layers
- Support nested keybind syntax in config:
  ```json
  {
    "_config": {
      "keybinds": {
        "normal": {
          "j": "down",
          "k": "up",
          "y": "yank_cell",
          "c": "toggle_mode"
        },
        "cell": {
          "j": "next_column",
          "k": "prev_column",
          "Enter": "select_cell"
        }
      }
    }
  }
  ```
- Allow CLI flags to add/remove keybinds (e.g., `--bind 'j:down'`, `--unbind 'j'`)

---

### 2.5 Built-in Actions
**Spec:** Core actions that work on generic data

**Sub-steps:**
- Extract existing actions to `actions.py`:
  - `scroll_up`, `scroll_down`
  - `select_row`, `select_cell`
  - `toggle_selection_mode`
  - `enter_search`, `exit_search`, `search_navigate`
  - `yank_cell` (with clipboard auto-detection)
  - `quit`
- Implement `Clipboard` utility:
  - Auto-detect: try `xclip`, `wl-copy`, `pbcopy`
  - Fallback: error message if none available
- Add `show_message` action for temporary popups
- Add `refresh_data` action:
  - For files: reload from disk
  - For stdin: show warning or re-run command if `-c` was used

---

### 2.6 Tab Management
**Spec:** Support tabs via JSON `tabs` array (replaces CLI args)

**Sub-steps:**
- Add `--tab-field` CLI flag to specify custom tab field name (default: `_config.tabs`)
- Load tabs from JSON config if present, ignore CLI file args
- Preserve existing tab navigation (h/l for prev/next)
- Support drill-down to new tab (configurable per drill-down)
- Each tab maintains its own data, selection, and scroll state

---

## Phase 3: Advanced Features

### 3.1 Drill-Down System
**Spec:** Navigate nested data by clicking on array-containing cells

**Sub-steps:**
- Detect cells containing arrays/objects (not just primitive values)
- Add visual indicator for drillable cells (e.g., special color or marker)
- On Enter in cell mode on drillable cell:
  - Default: replace current view with nested data
  - Optional: create new tab (configurable per drill-down)
- Drill-down configuration:
  ```json
  {
    "_config": {
      "drill_down": {
        "field": "items",              // Field containing array
        "inherit_flags": true,         // Inherit parent CLI flags
        "extra_flags": ["--filtered"], // Additional flags
        "new_tab": false               // Optional: open in new tab
      }
    }
  }
  ```
- Implement navigation stack for "back" functionality
- Pass parent data context to child view (optional)

---

### 3.2 Trigger System
**Spec:** Execute scripts/functions on cell/row/table events with environment variables

**Sub-steps:**
- Define trigger schema:
  ```json
  {
    "_config": {
      "triggers": {
        "table": {
          "on_select": "process_table.sh"
        },
        "rows": {
          "on_enter": {
            "script": "edit.sh",
            "data": "row"  // or "cell"
          }
        },
        "cells": {
          "status": {
            "on_change": "update_status.sh",
            "data": "cell"
          }
        }
      }
    }
  }
  ```
- Implement `TriggerExecutor` to:
  - Run shell commands (async for non-blocking)
  - Pass environment variables:
    - `DV_SELECTED_CELL`: JSON of selected cell (if in cell mode)
    - `DV_SELECTED_ROW`: JSON of entire selected row
    - `DV_SELECTED_INDEX`: Index of selected row
    - `DV_SELECTED_COLUMN`: Name of selected column (if in cell mode)
  - Handle both sync and async execution
- Support Python function triggers (for library usage)
- Priority: cell (in cell mode) > row > table

---

### 3.3 Enum Choice Tool
**Spec:** Popup dialog to change cell/row values from a predefined enum

**Sub-steps:**
- Create `EnumChoiceDialog` UI component:
  - Overlay popup above current content
  - List enum options with arrow key navigation
  - Enter to select, ESC to cancel
- Support three enum sources:
  1. **Inline**: `{"source": "inline", "values": ["a", "b", "c"]}`
  2. **Inferred**: `{"source": "inferred"}` - scan all values in column
  3. **External**: `{"source": "external", "command": "get_options.sh"}`
- Define enum in config:
  ```json
  {
    "_config": {
      "enum": {
        "status": {
          "source": "inferred"
        },
        "priority": {
          "source": "inline",
          "values": ["low", "medium", "high"]
        }
      }
    }
  }
  ```
- Add keybind to open enum picker (e.g., `e` or configurable)
- Handle enum changes:
  - Update displayed value
  - Optionally trigger `on_change` script

---

### 3.4 Refresh System
**Spec:** Define how data is refreshed after triggers

**Sub-steps:**
- Add `refresh` configuration:
  ```json
  {
    "_config": {
      "refresh": {
        "enabled": true,
        "on_trigger": true,         // Refresh after triggers
        "interval": 1.0,             // Auto-refresh interval (seconds)
        "command": "regenerate.sh"   // Optional: command to regenerate data
      }
    }
  }
  ```
- Implement refresh logic:
  - For file input: reload from disk
  - For stdin with `-c command`: re-run command
  - For stdin without command: show warning "Cannot refresh piped data without command"
- Add CLI flags: `--refresh`, `--no-refresh`, `--refresh-interval SECONDS`
- Preserve selection and scroll position after refresh

---

### 3.5 CSV Support
**Spec:** Basic read-only CSV parsing and display

**Sub-steps:**
- Use Python's `csv` module for parsing
- Detect delimiter (comma by default, config to override)
- Treat first row as headers (config to skip)
- Convert to internal table format for display
- Support same features as JSON (search, selection, triggers)
- Limitations for now: read-only, no editing, no CSV export

---

## Phase 4: Python Library API

### 4.1 High-Level Library Interface
**Spec:** Simple API for using dv-tui as a Python library

**Sub-steps:**
- Define main API in `__init__.py`:
  ```python
  from dv_tui import TableUI

  # Create TUI with data
  tui = TableUI(data=[{"col1": 1, "col2": 2}, ...])

  # Bind Python functions to keys
  def my_handler(selected_row):
      print(f"Selected: {selected_row}")

  tui.bind_key('Enter', my_handler)

  # Run TUI
  tui.run()
  ```
- Expose configuration options via constructor arguments
- Support keybinding with method calls (not decorators for simplicity)
- Allow programmatic data updates
- Provide event callbacks for TUI events (quit, mode change, etc.)

---

### 4.2 Entry Point for Library Usage
**Spec:** Clear distinction between CLI and library usage

**Sub-steps:**
- `cli.py`: Entry point for `dv` command
- `core.py`: Reusable TUI engine for library usage
- `__init__.py`: Public API exports
- Documentation: separate sections for CLI and library usage
- Example scripts showing library usage patterns

---

## Phase 5: Testing & Documentation

### 5.1 Test Infrastructure
**Spec:** Unit tests for core logic, E2E scenarios with test data

**Sub-steps:**
- Set up test framework (pytest recommended)
- Create `tests/` directory structure:
  - `tests/test_config.py` - config loading, merging
  - `tests/test_data_loaders.py` - JSON/CSV loading
  - `tests/test_fuzzy_match.py` - fuzzy matching logic
  - `tests/test_triggers.py` - trigger execution
  - `tests/test_clipboard.py` - clipboard operations
- Unit tests: focus on pure functions (fuzzy match, color management, etc.)
- Mock curses for TUI testing
- Create test scenarios:
  1. Basic table display with JSON
  2. Multi-tab navigation
  3. Search and filter
  4. Cell/row selection modes
  5. Drill-down into nested arrays
  6. Trigger execution (mocked)
  7. CSV parsing
  8. Config merging and precedence

---

### 5.2 Test Data
**Spec:** Sample JSON/CSV files for manual and automated testing

**Sub-steps:**
- Create `test_data/` directory:
  - `simple.json` - basic flat table
  - `nested.json` - tables with nested arrays
  - `multi_tab/` - multiple JSON files for tab testing
  - `enum_test.json` - data for enum picker
  - `triggers.json` - data with trigger configuration
  - `sample.csv` - CSV test file
  - `large.json` - performance testing (many rows)
- Create `test_scenarios.md` documenting:
  - What to test with each file
  - Expected behaviors
  - Manual testing checklist

---

### 5.3 Documentation
**Spec:** Comprehensive docs for CLI, library, and configuration

**Sub-steps:**
- Update `README.md` with:
  - Overview and features
  - Installation instructions (pip install)
  - CLI usage examples
  - Configuration reference
  - Library usage examples
- Create `CONFIG.md`:
  - Full configuration schema
  - All available options
  - Examples for different use cases
- Create `KEYBINDS.md`:
  - Default keybindings by mode
  - How to customize keybinds
  - Defining custom actions
- Create `LIBRARY.md`:
  - Python API reference
  - Example scripts
  - Common patterns
- Update inline docstrings for all public functions

---

## Phase 6: Cleanup & Removal of Specific Features

### 6.1 Remove Hardcoded Specifics
**Spec:** Remove assumptions about specific use case

**Sub-steps:**
- Remove nvim integration (move to example config):
  - Remove `open_in_nvim_async` method
  - Remove hardcoded paths (`~/share/`, `~/.cache/nvim/`)
  - Create example trigger config for nvim
- Remove `play_locator` integration (move to example config):
  - Remove hardcoded `jelly_play_yt` command
  - Create example trigger config
- Remove hardcoded field expectations (`type`, `status`, `summary`)
- Remove hardcoded color mappings (make configurable)
- Keep as examples in documentation

---

### 6.2 Cleanup Codebase
**Spec:** Refactor and clean up existing code

**Sub-steps:**
- Remove debug logging (`/tmp/dv_keys.txt`, `/tmp/dv_play.log`)
- Improve error messages and handling
- Add type hints throughout
- Improve variable naming for clarity
- Remove unused code and imports

---

## Phase 7: Installation & Distribution

### 7.1 Package Setup
**Spec:** Proper Python package for installation

**Sub-steps:**
- Create `pyproject.toml` with:
  - Package metadata (name, version, description)
  - Dependencies (curses is stdlib, minimal extras)
  - CLI entry point: `dv = dv_tui.cli:main`
  - Build configuration
- Add `LICENSE` file
- Create `MANIFEST.in` if needed
- Test installation with `pip install -e .`
- Verify `dv` command is available in PATH

---

### 7.2 Deployment Preparation
**Spec:** Ready for distribution

**Sub-steps:**
- Add version to `dv_tui/__init__.py`
- Create CHANGELOG.md
- Verify all tests pass
- Test on different platforms (Linux)
- Document dependencies

---

## Summary of Order

**Priority 1 (Core):** Architecture, data loading, table rendering, selection modes
**Priority 2 (Features):** Keybind system, built-in actions, tab management, triggers
**Priority 3 (Advanced):** Drill-down, enum tool, refresh system, CSV support
**Priority 4 (Library):** Python API, documentation
**Priority 5 (Quality):** Tests, test data, cleanup, installation
