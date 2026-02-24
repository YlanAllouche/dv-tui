# Tab Management Testing Guide

## Quick Start

Run the interactive test script:
```bash
./test_tabs.sh
```

## Test Data Files

1. **test_data_projects.json** - Sample project data (3 items)
2. **test_data_tasks.json** - Sample task data (5 items)
3. **test_with_tabs.json** - Config file with `_config.tabs` defined
   - Contains inline config in first item (filtered out from data)
   - Defines tabs for projects and tasks files
4. **test_custom_tab_field.json** - Config file with custom tab field `myTabs`

## Feature Tests

### 1. Tabs from JSON Config
Load tabs defined in `_config.tabs` field:

```bash
dv test_with_tabs.json
```

**What to test:**
- Two tabs should appear (projects and tasks)
- Press `h` or ← to go to previous tab
- Press `l` or → to go to next tab
- Navigate and select items, then switch tabs - state should be preserved

### 2. Custom Tab Field Name
Use `--tab-field` to specify custom field name:

```bash
dv --tab-field myTabs test_custom_tab_field.json
```

**What to test:**
- Tabs load from `myTabs` field instead of default `_config.tabs`

### 3. Multiple Files as Tabs (CLI Args)
Specify multiple files directly as CLI arguments:

```bash
dv test_data_projects.json test_data_tasks.json
```

**What to test:**
- Each file becomes a tab
- Tab names derived from filenames

### 4. Per-Tab State Preservation
In any multi-tab view:

1. Select row 5 in first tab
2. Scroll down a few rows
3. Press `l` to switch to second tab
4. Navigate in second tab (select different row)
5. Press `h` to return to first tab

**Expected behavior:**
- First tab remembers your selection position
- First tab remembers scroll offset
- Each tab has independent state

## Keybinds

| Key | Action |
|-----|--------|
| `h` or ← | Previous tab |
| `l` or → | Next tab |
| `q` | Quit |
| `j` or ↓ | Down |
| `k` or ↑ | Up |
| `Enter` | Select item |
| `/` | Search |

## Config Options

### Inline JSON Config
```json
[
  {
    "_config": {
      "tabs": ["file1.json", "file2.json"],
      "columns": ["name", "status"],
      "tab_name": "My Data"
    }
  },
  { "name": "Item 1", "status": "active" }
]
```

### CLI Flag for Custom Tab Field
```bash
dv --tab-field myCustomTabs config.json
```

### External Config File
Create `~/.config/dv/config.json`:
```json
{
  "_config": {
    "tabs": ["~/data/file1.json", "~/data/file2.json"]
  }
}
```

Then simply:
```bash
dv
```

## Advanced Usage

### Ignore CLI Files When Tabs Defined
When `_config.tabs` is present, CLI file arguments are ignored:

```bash
# This loads tabs from test_with_tabs.json, ignoring other_files.json
dv test_with_tabs.json other_files.json
```

### Tab Name Customization
Use `--tab-name` or inline config to set custom tab name:
```bash
dv --tab-name "Projects" test_data_projects.json
```

### Per-Tab Columns
Each file can have its own inline config with different columns:
```json
[
  {
    "_config": {
      "columns": ["name", "status"]
    }
  },
  { "name": "Item 1", "status": "active" }
]
```

## Fixes Applied

### Header Visibility Issue (Fixed)
Previously, when using columns like `["name", "type", "status", "summary"]`, the "type" and "summary" column headers would be invisible. This was caused by the `zip()` function truncating to the shortest list - only 3 header colors were defined, so only the first 3 column headers were rendered.

**Fix:** Updated `render_headers()` to cycle through colors using modulo (`i % len(header_colors)`), ensuring all column headers are rendered regardless of the number of columns.

### Empty Row Issue (Fixed)
Previously, when using `-s` flag with a config file containing `_config` as the first item, an empty row would appear under the header. This was because:

1. Config was loaded from filtered data (missing `_config` item)
2. Config-only items were displayed as data rows

**Fix:** Config is now loaded from the raw JSON file before data filtering, and config-only items are automatically filtered out from data.

### Tab Name Truncation (Fixed)
Previously, tab names were truncated even when there was enough room to display them fully.

**Fix:** Tab names are now displayed in full when the total width of all tabs fits within the available terminal width. Truncation only occurs when tabs exceed available space.

## Troubleshooting

### Tabs Not Loading
- Verify the config file is valid JSON
- Check that the tab field name is correct (use `--tab-field` if custom)
- Ensure files referenced in tabs exist

### State Not Preserved
- Verify you're navigating with `h`/`l` (tab navigation keys)
- In cell mode, `h`/`l` navigate cells, not tabs

### Custom Tab Field Not Working
- Ensure `--tab-field` matches the field name in config
- Example: `--tab-field myTabs` for `"myTabs": [...]`
