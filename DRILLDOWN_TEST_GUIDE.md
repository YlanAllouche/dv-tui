# Drill-Down System - Test Examples

This directory contains test data files for demonstrating the drill-down system.

## Test Data Files

### 1. `test_drilldown_nested_array.json`
Projects with nested arrays of tasks. Each project has a `tasks` array containing task objects.

**Example structure:**
```json
{
  "id": 1,
  "name": "Project Alpha",
  "tasks": [
    {"id": 1, "title": "Design phase", "status": "complete"},
    {"id": 2, "title": "Implementation", "status": "in_progress"}
  ]
}
```

**How to test:**
1. Run: `dv test_drilldown_nested_array.json`
2. Press `c` to enter cell mode
3. Navigate to the `tasks` column (marked with `[]`)
4. Press Enter to drill down into the tasks array
5. View individual task items
6. Press ESC to go back

### 2. `test_drilldown_nested_object.json`
Features with nested metadata objects. Each feature has a `metadata` object containing creation date, priority, and owner.

**Example structure:**
```json
{
  "id": 1,
  "name": "User Management",
  "metadata": {
    "created": "2025-01-01",
    "priority": "high",
    "owner": "Alice"
  }
}
```

**How to test:**
1. Run: `dv test_drilldown_nested_object.json`
2. Press `c` to enter cell mode
3. Navigate to the `metadata` column (marked with `{}`)
4. Press Enter to drill down into the metadata object
5. View metadata as key-value pairs
6. Press ESC to go back

### 3. `test_drilldown_multi_level.json`
Multi-level nesting with objects containing arrays containing objects. Tests deeper drill-down levels.

**Example structure:**
```json
{
  "id": 1,
  "name": "Multi-level Project",
  "structure": {
    "phases": [
      {"name": "Phase 1", "duration": 30}
    ],
    "team": {
      "lead": "Alice",
      "members": ["Bob", "Charlie"]
    }
  }
}
```

**How to test:**
1. Run: `dv test_drilldown_multi_level.json`
2. Press `c` to enter cell mode
3. Navigate to `structure` (marked with `{}`) and press Enter
4. Navigate to `phases` (marked with `[]`) and press Enter
5. Notice "Level 2" in header
6. Press ESC twice to return to top level

## Quick Start

Run the test script to try all examples:

```bash
./test_drilldown.sh
```

Or run individual examples:

```bash
# Test nested arrays
dv test_drilldown_nested_array.json

# Test nested objects
dv test_drilldown_nested_object.json

# Test multi-level nesting
dv test_drilldown_multi_level.json
```

## Navigation Guide

| Key | Action |
|-----|--------|
| `c` | Toggle between row and cell mode |
| `j`/`k` or `↓`/`↑` | Navigate up/down |
| `h`/`l` or `←`/`→` | Navigate left/right in cell mode |
| `Enter` | Select row or drill into drillable cell |
| `ESC` | Go back to previous drill-down level |
| `/` | Search mode |
| `q` | Quit |

## Visual Indicators

- `[]` - Cell contains an array (drillable)
- `{}` - Cell contains an object (drillable)
- Bold text - Drillable cell
- "Level X" in header - Current drill-down depth
