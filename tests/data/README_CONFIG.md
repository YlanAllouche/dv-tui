# Test Data for dv-tui Configuration System

This directory contains test data files for manual and automated testing of the configuration system.

---

## Test Data Files

### Standard Test Data

| File | Description | Format |
|------|-------------|---------|
| `work_tasks.json` | Sample work and study tasks | JSON |
| `study_tasks.json` | Study-focused tasks | JSON |
| `mixed_tasks.csv` | CSV format test data | CSV |

### Configuration Test Data

| File | Description | Purpose |
|------|-------------|---------|
| `test_inline_columns.json` | Inline columns configuration | Test columns filtering |
| `test_inline_keybinds.json` | Inline keybinds configuration | Test custom keybinds |
| `test_inline_triggers.json` | Inline triggers configuration | Test table/row/cell triggers |
| `test_inline_enum.json` | Inline enum configuration | Test enum value sources |
| `test_inline_drilldown.json` | Inline drill-down configuration | Test nested data navigation |
| `test_inline_refresh.json` | Inline refresh configuration | Test refresh settings |
| `test_inline_tabs.json` | Inline tabs configuration | Test tab loading |
| `test_invalid_config.json` | Invalid configuration | Test schema validation |
| `test_external_config.json` | External config file | Test config file loading |

---

## Test File Details

### test_inline_columns.json

Tests inline columns configuration:
- Filters columns to show only `type` and `summary`
- Sets custom column width for `type` (10 chars)
- Hides `status` column

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_inline_columns.json
```

**Expected:** Only 2 columns displayed (type, summary)

---

### test_inline_keybinds.json

Tests inline keybinds configuration:
- Sets leader key to semicolon (`;`)
- Configures down/up keys
- Defines normal mode keybinds

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_inline_keybinds.json
```

**Expected:** Custom keybinds work (j/k for navigation, ; for leader)

---

### test_inline_triggers.json

Tests inline triggers configuration:
- Table-level trigger: `on_enter` with `data: "table"`
- Row-level trigger: `on_select` for "focus" status
- Cell-level trigger: `on_change` for "type" field
- All triggers set to async execution

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_inline_triggers.json
```

**Expected:** Triggers configured (execution depends on trigger implementation)

---

### test_inline_enum.json

Tests inline enum configuration:
- Status enum with 5 inline values
- Priority enum with 3 inline values
- Multiple enum fields supported

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_inline_enum.json
```

**Expected:** Enum values defined for status and priority fields

---

### test_inline_drilldown.json

Tests inline drill-down configuration:
- Drill-down enabled
- `items` field as drill-down target
- Configured to inherit flags and add extra flags
- New tab disabled

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_inline_drilldown.json
```

**Expected:** Can navigate into `items` arrays

---

### test_inline_refresh.json

Tests inline refresh configuration:
- Refresh enabled
- Refresh interval: 1.0 second
- Command specified for data generation
- Refresh on trigger enabled

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_inline_refresh.json
```

**Expected:** Data reloads after 1 second when file modified

---

### test_inline_tabs.json

Tests inline tabs configuration:
- Loads `work_tasks.json` as first tab
- Loads `study_tasks.json` as second tab
- Defines columns for tabs

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_inline_tabs.json
```

**Expected:** Two tabs with external file data

---

### test_invalid_config.json

Tests schema validation:
- Invalid `columns` type (string instead of array)
- Invalid `drill_down.enabled` type (string instead of boolean)

**Usage:**
```bash
python -m dv_tui.cli tests/data/test_invalid_config.json
```

**Expected:** Validation error, TUI does not start

---

### test_external_config.json

External configuration file for testing:
- Defines column order: status, summary, type
- Sets custom column widths
- Configures keybinds
- Defines color mappings

**Usage:**
```bash
python -m dv_tui.cli tests/data/work_tasks.json --config tests/data/test_external_config.json
```

**Expected:** Config loaded and applied to TUI

---

## Testing Scenarios

### 1. Basic Configuration

```bash
# Test default columns
python -m dv_tui.cli tests/data/work_tasks.json

# Test external config
python -m dv_tui.cli tests/data/work_tasks.json --config tests/data/test_external_config.json

# Test inline config
python -m dv_tui.cli tests/data/test_inline_columns.json
```

### 2. Config Priority

```bash
# CLI > Inline > File > Defaults
python -m dv_tui.cli tests/data/test_inline_columns.json \
  --config tests/data/test_external_config.json \
  --columns "type"
```

### 3. Multi-File Tabs

```bash
# Test tabs
python -m dv_tui.cli tests/data/work_tasks.json tests/data/study_tasks.json

# Test inline tabs
python -m dv_tui.cli tests/data/test_inline_tabs.json
```

### 4. Validation

```bash
# Test invalid config (should error)
python -m dv_tui.cli tests/data/test_invalid_config.json
```

### 5. Advanced Features

```bash
# Test keybinds
python -m dv_tui.cli tests/data/test_inline_keybinds.json

# Test triggers
python -m dv_tui.cli tests/data/test_inline_triggers.json

# Test enum
python -m dv_tui.cli tests/data/test_inline_enum.json

# Test drill-down
python -m dv_tui.cli tests/data/test_inline_drilldown.json

# Test refresh
python -m dv_tui.cli tests/data/test_inline_refresh.json
```

---

## Library Usage Examples

### Loading Test Data

```python
from dv_tui import load_file

# Load standard test data
data = load_file("tests/data/work_tasks.json")

# Load inline config test
data = load_file("tests/data/test_inline_columns.json")
```

### Testing Config Loading

```python
from dv_tui import load_config

# Load default config
config = load_config()

# Load from external file
config = load_config(config_path="tests/data/test_external_config.json")

# Load with inline config
from dv_tui import load_file, load_config_from_inline_json
data = load_file("tests/data/test_inline_columns.json")
inline_config = load_config_from_inline_json(data)
config = load_config(inline_config=inline_config)
```

### Testing TUI with Config

```python
from dv_tui import TUI, load_config

# Load config and create TUI
config = load_config(config_path="tests/data/test_external_config.json")
tui = TUI(files=["tests/data/work_tasks.json"], config=config)

# Load data (may apply inline config)
tui.load_data()
```

---

## Creating Custom Test Data

### Inline Config Template

```json
[
  {
    "_config": {
      "columns": ["field1", "field2"],
      "column_widths": {"field1": 10},
      "keybinds": {
        "normal": {
          "leader": 59
        }
      },
      "triggers": {
        "table": {
          "on_enter": "command.sh",
          "data": "table",
          "async": true
        }
      },
      "enum": {
        "status": {
          "source": "inline",
          "values": ["value1", "value2"]
        }
      },
      "drill_down": {
        "enabled": true,
        "field": "items"
      },
      "refresh": {
        "enabled": true,
        "interval": 1.0
      }
    }
  },
  {
    "field1": "value1",
    "field2": "value2"
  }
]
```

### External Config Template

```json
{
  "columns": ["field1", "field2"],
  "column_widths": {"field1": 10, "field2": 15},
  "keybinds": {
    "normal": {
      "leader": 59,
      "down": [106, 258],
      "up": [107, 259]
    }
  },
  "colors": {
    "field1": {"value": (5, true)}
  },
  "triggers": {
    "table": {
      "on_enter": "command.sh"
    }
  },
  "enum": {
    "status": {
      "source": "inline",
      "values": ["active", "pending"]
    }
  },
  "drill_down": {
    "enabled": true,
    "field": "items"
  },
  "refresh": {
    "enabled": true,
    "interval": 1.0
  },
  "tabs": ["file1.json", "file2.json"]
}
```

---

## Testing Checklist

- [ ] Load and display standard test data files
- [ ] Apply external config from file
- [ ] Extract and apply inline config
- [ ] Test config priority (CLI > Inline > File > Defaults)
- [ ] Test columns filtering and reordering
- [ ] Test custom keybinds
- [ ] Test triggers (when implemented)
- [ ] Test enum configuration (when implemented)
- [ ] Test drill-down (when implemented)
- [ ] Test refresh settings
- [ ] Test inline tabs
- [ ] Test invalid config validation
- [ ] Test multi-file tabs
- [ ] Test mixed file types (JSON + CSV)
- [ ] Test library API with test data

---

## Notes

- Test data files use consistent structure: `type`, `status`, `summary`
- All inline config files use `_config` as the first field
- External config files use standard JSON format (no `_config` wrapper)
- Invalid config test should produce clear error messages
- Refresh test may need manual file modification to trigger

---

## Related Documentation

- `TESTING_CLI.md` - CLI testing guide with scenarios
- `TESTING_LIBRARY.md` - Library testing guide with examples
- `README.md` - General project documentation
- `openspec/changes/02-configuration-system/` - Configuration system change proposal
