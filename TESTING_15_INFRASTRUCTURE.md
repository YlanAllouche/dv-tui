# Testing Infrastructure Documentation

This document describes the testing infrastructure for dv-tui, implemented via change proposal 15-testing-infrastructure.

## Running the Test Suite

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_config.py
pytest tests/test_data_loaders.py
pytest tests/test_fuzzy_match.py
pytest tests/test_triggers.py
pytest tests/test_clipboard.py
pytest tests/test_e2e.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with detailed output
```bash
pytest -vv
```

### Run specific test
```bash
pytest tests/test_config.py::test_load_defaults
```

### Run with coverage (if coverage.py is installed)
```bash
pytest --cov=dv_tui --cov-report=html
```

### Run tests matching a pattern
```bash
pytest -k "config"
pytest -k "fuzzy"
pytest -k "e2e"
```

## Test Data Requirements

The tests use various sample data files. These are created on-the-fly using `tempfile` and do not require manual setup.

### JSON Test Data

Tests create temporary JSON files like:
```json
[
  {
    "_config": {
      "columns": ["name", "age"]
    }
  },
  {
    "name": "Alice",
    "age": 30
  },
  {
    "name": "Bob",
    "age": 25
  }
]
```

### CSV Test Data

Tests create temporary CSV files like:
```csv
name,age,city
Alice,30,NYC
Bob,25,LA
```

### Nested Array Test Data

Tests use nested structures for drill-down testing:
```json
[
  {
    "name": "Project1",
    "tags": ["bug", "feature"],
    "tasks": [
      {"title": "Task1", "status": "done"},
      {"title": "Task2", "status": "todo"}
    ]
  }
]
```

## Expected Test Results

When running the full test suite, you should see approximately 199 tests passing:

```
============================= 199 passed in 2.46s ==============================
```

### Test Breakdown

| Test File | Test Count | Coverage |
|-----------|------------|----------|
| test_config.py | 21 | Config loading, merging, validation |
| test_data_loaders.py | 74 | JSON, CSV, stdin loading |
| test_fuzzy_match.py | 21 | Fuzzy matching and filtering |
| test_triggers.py | 29 | Trigger execution, management |
| test_clipboard.py | 14 | Clipboard operations |
| test_curses_mock.py | 27 | Curses mocking utilities |
| test_e2e.py | 21 | End-to-end scenarios |
| test_table.py | 41 | Table rendering and logic |
| **Total** | **199** | **All components** |

## CLI Commands to Verify Tests Pass

### Quick verification
```bash
pytest -q
```

Expected output: `199 passed in ~2s`

### Detailed verification with summary
```bash
pytest -v --tb=short
```

### Verify specific component
```bash
# Config tests
pytest tests/test_config.py -v

# Data loader tests
pytest tests/test_data_loaders.py -v

# Trigger tests
pytest tests/test_triggers.py -v

# E2E tests
pytest tests/test_e2e.py -v
```

### Check for failed tests
```bash
pytest --tb=short | grep -E "(FAILED|ERROR)"
```

Expected output: No failures or errors

## Test Organization

### Unit Tests

**tests/test_config.py** (21 tests)
- Config loading from files and inline JSON
- Config validation
- Config merging with precedence (CLI > inline > file > defaults)
- Trigger configuration
- Enum configuration
- Drill-down configuration
- Refresh configuration
- Tab configuration

**tests/test_data_loaders.py** (74 tests)
- JSON file loading
- CSV file loading
- Inline JSON loading
- Stdin loading with timeout
- Process substitution support
- File descriptor paths (/dev/fd/*, /proc/self/fd/*)
- Custom delimiters for CSV
- Config filtering from data
- Missing key handling
- Refresh functionality

**tests/test_fuzzy_match.py** (21 tests)
- Exact matching
- Case-insensitive matching
- Substring matching
- Prefix/suffix matching
- Score calculation
- Empty query handling
- Unicode support
- Fuzzy filtering with field specification
- Result ordering by score

**tests/test_triggers.py** (29 tests)
- Shell command execution (async and sync)
- Python function execution
- Environment variable building
- Template formatting
- Trigger manager priority (cell > row > table)
- Trigger chaining
- Condition matching

**tests/test_clipboard.py** (14 tests)
- Tool detection (xclip, wl-copy, pbcopy)
- Copy operations
- Error handling
- Unicode support
- Empty string handling

### Mocking Utilities

**tests/test_curses_mock.py** (27 tests)
- Mock curses module for TUI testing
- Mock window creation and operations
- Mock constants (keys, colors, attributes)
- Mock color pair initialization
- Enables TUI testing without terminal

### E2E Tests

**tests/test_e2e.py** (21 tests)
- Basic table display
- Multi-tab navigation
- Search and filter functionality
- Cell/row selection modes
- Drill-down into nested arrays
- Trigger execution
- CSV parsing with various delimiters
- Config merging with precedence
- Large table performance (100 rows)
- JSON with inline config
- Stdin data loading
- Table navigation (up/down)
- Color configuration
- Keybind configuration
- Refresh functionality

**tests/test_table.py** (41 tests)
- Dynamic column detection
- Column filtering
- Column reordering
- Dynamic column widths
- Backward compatibility
- Scroll offset management

## Curses Mocking for TUI Testing

The test suite includes a comprehensive curses mocking framework in `tests/test_curses_mock.py` that allows testing TUI components without an actual terminal.

### MockCurses Class
Provides a mock curses module with:
- All standard curses constants (KEY_UP, KEY_DOWN, etc.)
- Mock color pair management
- Mock window creation

### MockWindow Class
Provides a mock curses window with:
- addstr/addnstr operations
- move/getyx operations
- clear/erase operations
- refresh tracking
- resize support

### Usage Example
```python
from tests.test_curses_mock import MockWindow

def test_table_rendering():
    window = MockWindow()
    table = Table(data, columns, widths)
    # Test rendering without actual terminal
```

## Adding New Tests

### Unit Test Template
```python
def test_feature_name():
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

### E2E Test Template
```python
def test_e2e_scenario():
    """Test end-to-end scenario."""
    with patch('curses.wrapper') as mock_wrapper:
        # Setup mocks
        mock_window = Mock()
        mock_window.getmaxyx.return_value = (24, 80)
        
        # Execute
        result = function_under_test(...)
        
        # Verify
        assert result == expected
```

## Continuous Integration

The test suite is designed for CI/CD:

```bash
# Run tests in CI
pytest -v --tb=short --cov=dv_tui --cov-report=xml

# Exit with non-zero on failure
pytest --exit-on-error
```

## Troubleshooting

### Import errors
Ensure dv-tui is installed in development mode:
```bash
pip install -e .
```

### Test failures
Run with verbose output to see details:
```bash
pytest -v --tb=long
```

### Specific test failures
Run just the failing test:
```bash
pytest tests/test_file.py::test_name -vv
```
