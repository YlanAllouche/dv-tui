# Testing Guide for Package Installation

This guide covers testing the package installation and distribution of dv-tui.

## How to Test Package Installation

### Prerequisites

- Python 3.8 or higher
- pip installed
- Development environment or virtual environment

## Installation Test Commands

### 1. Install in Editable Mode (Development)

Install the package in editable mode to test changes immediately:

```bash
pip install -e .
```

Or if using an externally-managed environment:

```bash
pip install -e . --break-system-packages
```

### 2. Install in Regular Mode (Distribution)

Build and install the package as a normal user would:

```bash
pip install .
```

Or from the source distribution:

```bash
# Build source distribution
python -m build

# Install from wheel
pip install dist/dv_tui-0.1.0-py3-none-any.whl
```

### 3. Uninstall the Package

```bash
pip uninstall dv-tui
```

## Verification Steps

### 1. Verify CLI Entry Point

Check that the `dv` command is available:

```bash
dv --help
```

Expected output: Help text showing all available options

### 2. Verify Package Metadata

Check package information:

```bash
pip show dv-tui
```

Expected output:
- Name: dv-tui
- Version: 0.1.0
- Description: A curses-based TUI for viewing JSON/CSV data with nvim integration

### 3. Verify Version Access

Verify the version is accessible from Python:

```bash
python -c "import dv_tui; print(dv_tui.__version__)"
```

Expected output: `0.1.0`

### 4. Verify Package Structure

Verify the package modules are importable:

```bash
python -c "from dv_tui import TableUI, TUI, Table, Config, load_config; print('All imports successful')"
```

### 5. Run Tests with Installed Package

After installation, run tests to ensure the package works correctly:

```bash
pytest tests/ -v
```

Expected: All tests pass (197 tests in test suite)

### 6. Test Basic Functionality

Test basic usage with sample data:

```bash
# Test with JSON file
dv tests/data/work_tasks.json

# Test with CSV file
dv tests/data/mixed_tasks.csv

# Test with multiple files
dv tests/data/work_tasks.json tests/data/study_tasks.json
```

### 7. Test Single-Select Mode

```bash
dv -s tests/data/work_tasks.json
```

### 8. Verify Library Usage

Test the library API:

```bash
python -c "
from dv_tui import TableUI
data = [{'name': 'Alice', 'status': 'active'}]
tui = TableUI(data)
print('TableUI created successfully')
"
```

## Dependencies Verification

### Check for External Dependencies

```bash
pip show dv-tui | grep -i requires
```

Expected: No external dependencies (only Python standard library)

### Verify Curses Availability

```bash
python -c "import curses; print('curses module is available')"
```

If curses is not available on Linux:
- Ubuntu/Debian: `sudo apt-get install python3-curses`
- Fedora: `sudo dnf install python3-curses`

## Files to Verify

After installation, verify these files exist:

1. **pyproject.toml** - Package metadata and build configuration
2. **LICENSE** - MIT License file
3. **CHANGELOG.md** - Version history and changes
4. **README.md** - Documentation with installation instructions

## Build Verification (For Distribution)

To prepare for PyPI distribution:

```bash
# Install build tools
pip install build twine

# Build source distribution and wheel
python -m build

# Check the distribution
twine check dist/*
```

Expected: No warnings or errors from twine check

## Common Issues and Solutions

### Issue: "externally-managed-environment" error

**Solution**: Use `--break-system-packages` flag or create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Issue: `dv` command not found

**Solution**: Check that pip installed the script to your PATH

```bash
# Find where dv was installed
which dv
# or
where dv  # on Windows
```

### Issue: Curses module not available

**Solution**: Install curses package for your Linux distribution

- Ubuntu/Debian: `sudo apt-get install python3-curses`
- Fedora: `sudo dnf install python3-curses`

## Test Summary

- [ ] Package installs in editable mode
- [ ] Package installs in regular mode
- [ ] `dv --help` works
- [ ] `pip show dv-tui` shows correct metadata
- [ ] `import dv_tui; print(dv_tui.__version__)` works
- [ ] All imports work
- [ ] All tests pass (197 tests)
- [ ] Basic functionality works with test data
- [ ] No external dependencies required
- [ ] LICENSE file exists
- [ ] CHANGELOG.md exists and is formatted correctly
