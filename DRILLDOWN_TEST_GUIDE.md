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

### 4. `test_drilldown_named_array.json`
Named arrays - objects containing a single top-level array field. The field name is displayed as `[fieldname]` instead of `{}`.

**Example structure:**
```json
{
  "id": 1,
  "name": "Feature with named array",
  "metadata": {"Click to know more": [1, 2, 3]}
}
```

**How to test:**
1. Run: `dv test_drilldown_named_array.json`
2. Press `c` to enter cell mode
3. Navigate to `metadata` column (marked with `[Click to know more]`)
4. Press Enter to drill down
5. View the array values [1, 2, 3] as rows
6. Press ESC to go back

### 5. `test_drilldown_new_tab.json` (config-based)
Uses inline config to open drill-down in a new tab instead of replacing current view.

**How to test:**
1. Run: `dv test_drilldown_new_tab.json`
2. Drill down to create a new tab
3. Switch between tabs to compare data

### 6. `test_drilldown_comprehensive.json` (all permutations)
Contains 15 different test cases covering every combination of drillable data types.

**Test cases included:**
| # | Type | Description |
|---|------|-------------|
| 1 | Simple Array | Basic array `[1, 2, 3]` |
| 2 | Simple Object | Basic object with key-value pairs |
| 3 | Array of Objects | Arrays containing nested objects with more arrays |
| 4 | Named Array | Object with single top-level array field |
| 5 | Nested Object | Multi-level object nesting |
| 6 | Multi-Level Array | Arrays containing arrays |
| 7 | Mixed Object | Object with arrays and objects mixed |
| 8 | Deep Object Nesting | 4+ levels of object nesting |
| 9 | Deep Array Nesting | Arrays containing objects containing arrays |
| 10 | Array of Arrays | Matrix-style data |
| 11 | Empty Array | Tests empty array handling |
| 12 | Empty Object | Tests empty object handling |
| 13 | Mixed Drill Path | Complex navigation through different types |
| 14 | Named Single Value | Named array with single value |
| 15 | Complex Mixed Structure | Real-world complex nested data |

**How to test:**
1. Run: `dv test_drilldown_comprehensive.json`
2. Navigate through different rows to test each type
3. Try deep nesting on rows 8 and 9 to test depth limits
4. Test empty structures on rows 11 and 12

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

# Test named arrays
dv test_drilldown_named_array.json

# Test new tab drill-down
dv test_drilldown_new_tab.json

# Test all drillable types (comprehensive)
dv test_drilldown_comprehensive.json
```

## Drill-Down Depth

### Depth Limits
- **No hard limit** on drill-down depth
- Practically limited by available memory (100+ levels possible)
- Each level saves state to navigation stack for restoration

### Navigation Behavior
```
Level 1 (top level)
    ↓ drill down into []
Level 2
    ↓ drill down into {}
Level 3
    ↓ drill down into []
Level 4
    ...
```

- Press ESC to go back **one level at a time**
- Continue pressing ESC to return to top level
- Header shows `Level X` indicating current depth

### Deep Nesting Examples

**Deep object nesting** (row 8 in comprehensive test):
```
root {}
  ↓ drill down
    level1 {}
      ↓ drill down
        level2 {}
          ↓ drill down
            level3 {}
              ↓ drill down
                level4 {}
                  ↓ drill down
                    data: "You reached the bottom!"
```

**Deep array nesting** (row 9 in comprehensive test):
```
chain []
  ↓ drill down
    [Object] with items []
      ↓ drill down
        items [1, 2, 3]
```

## Single-Select Mode (-s flag)

When using the `-s` flag, drill-down behavior changes:

1. **Drillable cells**: Pressing Enter drills down (does NOT return to stdout)
2. **Non-drillable cells**: Pressing Enter outputs the value to stdout and exits
3. **Row mode**: Pressing Enter outputs the entire row to stdout and exits

**Example workflow:**
```bash
dv -s test_drilldown_nested_array.json

# User:
# 1. Press 'c' for cell mode
# 2. Navigate to tasks[] cell, press Enter → drills down (no return)
# 3. Navigate to status cell, press Enter → outputs {"field": "status", "value": "complete"}
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
- `[fieldname]` - Object contains single array field with name (drillable)
- Bold text - Drillable cell
- "Level X" in header - Current drill-down depth
