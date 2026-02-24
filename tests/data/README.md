# Test Data

This directory contains sample data for manual testing of dv-tui.

## Available Test Files

- `work_tasks.json` - Sample work and study tasks with various statuses
- `study_tasks.json` - Study-focused tasks
- `mixed_tasks.csv` - CSV format test data

## Testing Commands

### View a single JSON file
```bash
dv tests/data/work_tasks.json
```

### View multiple JSON files (tab navigation)
```bash
dv tests/data/work_tasks.json tests/data/study_tasks.json
```

### View CSV file
```bash
dv tests/data/mixed_tasks.csv
```

### Single-select mode (exits after selection)
```bash
dv -s tests/data/work_tasks.json
```

### Test all formats at once
```bash
dv tests/data/work_tasks.json tests/data/study_tasks.json tests/data/mixed_tasks.csv
```

## Keyboard Shortcuts

- `j/k` or `↓/↑` - Navigate up/down
- `h/l` or `←/→` - Switch tabs (multiple files)
- `/` - Enter search mode
- Type to filter in search mode
- `ESC` - Exit search mode
- `Enter` - Select and open item
- `q` or `Q` - Quit
- `C-p` or `;+p` - Play locator (if available)

## Testing Features

1. **Tab Navigation**: Open multiple files and use `h/l` to switch between them
2. **Search**: Press `/` and type to filter items (e.g., "python", "focus", "work")
3. **Color Coding**: Observe different colors for type, status, and dates
4. **File Formats**: Test both JSON and CSV loading
5. **Scrolling**: Navigate through long lists
6. **Single-Select Mode**: Test `-s` flag for exit after selection
