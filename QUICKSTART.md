# Quick Start

The `dv` command is now installed and available globally in your PATH.

## Usage

```bash
# View test data (single file)
dv tests/data/work_tasks.json

# View multiple files with tab navigation (use h/l to switch)
dv tests/data/work_tasks.json tests/data/study_tasks.json

# Test CSV support
dv tests/data/mixed_tasks.csv

# Single-select mode (exits after selection)
dv -s tests/data/work_tasks.json
```

## Test with Any Data

```bash
# Interactive selection from ~/share/_tmp/ (if directory exists)
dv

# View specific file
dv /path/to/your/data.json

# Multiple files as tabs
dv file1.json file2.json file3.json
```

## File Formats Supported

- **JSON**: `.json` files with array of objects
- **CSV**: `.csv` files with headers

## Keyboard Shortcuts

| Key | Action |
|------|--------|
| `j/k` or `↓/↑` | Navigate up/down |
| `h/l` or `←/→` | Previous/Next tab (multiple files) |
| `/` | Enter search mode |
| Type | Filter items (in search mode) |
| `Enter` | Select/open item |
| `Tab`/`S-Tab` | Next/Prev result (search mode) |
| `ESC` | Exit search mode |
| `Backspace` | Delete (search mode) |
| `q` or `Q` | Quit |

## Installation Details

- **Command location**: `/home/ylan/.local/bin/dv`
- **Package version**: 0.1.0
- **Installation type**: Editable (symlinked to source)
- **Python**: 3.14

## Troubleshooting

If you see "ord() expected string of length 1" errors:
1. Clear Python cache: `rm -rf dv_tui/__pycache__`
2. Reinstall: `pip install -e . --break-system-packages`

## Testing

Run basic functionality tests:
```bash
python test_basic.py
```
