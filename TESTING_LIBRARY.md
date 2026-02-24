# Library Testing Guide - dv-tui Configuration System

This guide provides comprehensive manual testing scenarios for configuration system using dv-tui as a Python library.

## Test Data Location

All test data files are located in `tests/data/`:
- `work_tasks.json`, `study_tasks.json` - Standard test data
- `test_inline_*.json` - Files with inline `_config` sections
- `test_external_config.json` - External config file
- `test_invalid_config.json` - Invalid config for validation testing

---

## Library API Overview

```python
from dv_tui import Config, load_config, load_file, TUI

# Config management
config = load_config()                    # Load default config
config = load_config(config_path="path")  # Load from file
config = load_config(cli_config={"columns": ["type"]})  # CLI config

# Data loading
data = load_file("tests/data/work_tasks.json")

# TUI creation
tui = TUI(files=["data.json"], single_select=False, config=config)
```

---

## 1. Configuration Dataclass Testing

### 1.1 Default Configuration

#### Test: Create Default Config
**Purpose:** Verify Config dataclass with defaults

**Test Script:**
```python
from dv_tui import Config

config = Config()

# Verify defaults
assert config.columns == ["type", "status", "summary"]
assert config.column_widths == {"type": 8, "status": 12}
assert config.keybinds is not None
assert config.colors is not None
assert config.triggers is None
assert config.enum is None
assert config.drill_down is None
assert config.refresh is None
assert config.tabs is None
assert config.config_file is None
assert config.single_select == False
assert config.stdin_timeout is None

print("✓ Default config initialized correctly")
```

**Expected Behavior:**
- Config object created with all defaults
- Optional fields are None
- Required fields have default values

---

#### Test: Serialize Config to Dict
**Purpose:** Verify `to_dict()` method works

**Test Script:**
```python
from dv_tui import Config

config = Config(columns=["type", "summary"])
config_dict = config.to_dict()

# Verify serialization
assert isinstance(config_dict, dict)
assert config_dict["columns"] == ["type", "summary"]
assert "keybinds" in config_dict
assert "colors" in config_dict

print("✓ Config serialized to dict correctly")
print(f"  Columns: {config_dict['columns']}")
```

**Expected Behavior:**
- Config converted to dictionary
- All fields present in output
- Optional fields included when set

---

### 1.2 Subclass Configuration

#### Test: KeybindConfig
**Purpose:** Verify KeybindConfig dataclass

**Test Script:**
```python
from dv_tui.config import KeybindConfig, ModeKeybinds

# Test individual keybind config
keybind = KeybindConfig()
assert keybind.j == "down"
assert keybind.k == "up"
assert keybind.leader == ord(';')

# Test mode keybinds
mode_keybinds = ModeKeybinds()
assert mode_keybinds.normal is not None
assert mode_keybinds.search is not None
assert mode_keybinds.cell is None

# Convert to dict
keybind_dict = keybind.to_dict()
assert "leader" in keybind_dict
assert "quit" in keybind_dict

print("✓ KeybindConfig initialized correctly")
```

**Expected Behavior:**
- KeybindConfig has all default keybinds
- ModeKeybinds has normal and search modes
- to_dict() produces backward-compatible format

---

#### Test: ColorsConfig
**Purpose:** Verify ColorsConfig dataclass

**Test Script:**
```python
from dv_tui.config import ColorsConfig

colors = ColorsConfig()
assert colors.type == {"work": (5, True), "study": (6, True)}
assert colors.status == {"focus": (2, True), "active": (3, True)}
assert colors.date == {"prefix": "2025-", "color": 4}

colors_dict = colors.to_dict()
assert "type" in colors_dict
assert "status" in colors_dict
assert "date" in colors_dict

print("✓ ColorsConfig initialized correctly")
```

**Expected Behavior:**
- Color mappings loaded correctly
- to_dict() produces expected format

---

#### Test: TriggerConfig
**Purpose:** Verify TriggerConfig dataclass

**Test Script:**
```python
from dv_tui.config import TriggerConfig, TriggersConfig

# Test single trigger
trigger = TriggerConfig(
    on_enter="echo test",
    on_select="echo selected",
    data="row",
    async_=True
)
assert trigger.on_enter == "echo test"
assert trigger.data == "row"
assert trigger.async_ == True

# Test triggers config
triggers = TriggersConfig()
triggers.table = TriggerConfig(on_enter="table_enter.sh")
triggers.rows = {"focus": TriggerConfig(on_select="focus_row.sh")}
triggers.cells = {"type": TriggerConfig(on_change="type_change.sh")}

assert triggers.table is not None
assert "focus" in triggers.rows
assert "type" in triggers.cells

print("✓ TriggerConfig initialized correctly")
```

**Expected Behavior:**
- TriggerConfig stores all trigger properties
- `async_` field avoids Python keyword conflict
- TriggersConfig supports table/rows/cells

---

#### Test: EnumConfig
**Purpose:** Verify EnumConfig dataclass

**Test Script:**
```python
from dv_tui.config import EnumSourceConfig, EnumConfig

# Test enum source
source_inline = EnumSourceConfig(
    source="inline",
    values=["active", "pending", "done"]
)
assert source_inline.source == "inline"
assert source_inline.values == ["active", "pending", "done"]

source_inferred = EnumSourceConfig(source="inferred")
assert source_inferred.source == "inferred"

source_external = EnumSourceConfig(
    source="external",
    command="get_options.sh"
)
assert source_external.command == "get_options.sh"

# Test enum config
enum = EnumConfig()
enum.status = source_inline
enum.priority = source_inferred
enum.type = source_external

assert enum.status is not None
assert enum.priority is not None
assert enum.type is not None

print("✓ EnumConfig initialized correctly")
```

**Expected Behavior:**
- EnumSourceConfig supports all three sources
- EnumConfig can configure multiple fields
- Different enum sources work correctly

---

#### Test: DrillDownConfig
**Purpose:** Verify DrillDownConfig dataclass

**Test Script:**
```python
from dv_tui.config import DrillDownConfig

drill = DrillDownConfig(
    enabled=True,
    field_name="items",
    inherit_flags=True,
    extra_flags=["--filtered"],
    new_tab=False
)

assert drill.enabled == True
assert drill.field_name == "items"
assert drill.inherit_flags == True
assert drill.extra_flags == ["--filtered"]
assert drill.new_tab == False

print("✓ DrillDownConfig initialized correctly")
```

**Expected Behavior:**
- All drill-down options set correctly
- `field_name` used instead of `field` to avoid conflict

---

#### Test: RefreshConfig
**Purpose:** Verify RefreshConfig dataclass

**Test Script:**
```python
from dv_tui.config import RefreshConfig

refresh = RefreshConfig(
    enabled=True,
    on_trigger=True,
    interval=2.0,
    command="regenerate.sh"
)

assert refresh.enabled == True
assert refresh.on_trigger == True
assert refresh.interval == 2.0
assert refresh.command == "regenerate.sh"

print("✓ RefreshConfig initialized correctly")
```

**Expected Behavior:**
- All refresh options set correctly
- Float interval works
- Command can be None or string

---

## 2. Config Loader Testing

### 2.1 Load Default Config

#### Test: Load with No Arguments
**Purpose:** Verify default config loads correctly

**Test Script:**
```python
from dv_tui import load_config

config = load_config()

# Verify it's a Config object, not dict
assert hasattr(config, 'columns')
assert hasattr(config, 'keybinds')
assert hasattr(config, 'colors')

# Verify defaults
assert config.columns == ["type", "status", "summary"]
assert config.single_select == False

print("✓ Default config loaded correctly")
print(f"  Columns: {config.columns}")
print(f"  Single select: {config.single_select}")
```

**Expected Behavior:**
- Config object returned
- All defaults applied
- No errors thrown

---

### 2.2 Load from File

#### Test: Load External Config File
**Purpose:** Verify external config file loads and merges

**Test Script:**
```python
from dv_tui import load_config

config = load_config(config_path="tests/data/test_external_config.json")

# Verify external config loaded
assert config.columns == ["status", "summary", "type"]
assert config.column_widths == {"status": 15, "type": 10}

# Verify defaults still present for missing options
assert config.triggers is None  # Not in external config

print("✓ External config loaded correctly")
print(f"  Columns: {config.columns}")
print(f"  Column widths: {config.column_widths}")
```

**Expected Behavior:**
- External config loaded and applied
- Config from file merged with defaults
- Missing options use defaults

---

### 2.3 Load from Inline Config

#### Test: Load Inline Config from Data
**Purpose:** Verify inline `_config` is extracted and merged

**Test Script:**
```python
from dv_tui import load_file, load_config_from_inline_json

data = load_file("tests/data/test_inline_columns.json")
inline_config = load_config_from_inline_json(data)

# Verify inline config extracted
assert inline_config is not None
assert inline_config["columns"] == ["type", "summary"]
assert inline_config["column_widths"] == {"type": 10}

print("✓ Inline config extracted correctly")
print(f"  Columns: {inline_config['columns']}")
```

**Expected Behavior:**
- Inline config extracted from first item
- Only `_config` field extracted
- Data items remain intact

---

#### Test: No Inline Config
**Purpose:** Verify behavior when no inline config present

**Test Script:**
```python
from dv_tui import load_file, load_config_from_inline_json

data = load_file("tests/data/work_tasks.json")
inline_config = load_config_from_inline_json(data)

# Verify no inline config found
assert inline_config == {}

print("✓ No inline config handled correctly")
```

**Expected Behavior:**
- Empty dict returned
- No errors thrown

---

### 2.4 Load from CLI Config

#### Test: CLI Config Only
**Purpose:** Verify CLI-only config works

**Test Script:**
```python
from dv_tui import load_config

cli_config = {
    "columns": ["type"],
    "single_select": True
}

config = load_config(cli_config=cli_config)

# Verify CLI config applied
assert config.columns == ["type"]
assert config.single_select == True

print("✓ CLI config loaded correctly")
print(f"  Columns: {config.columns}")
print(f"  Single select: {config.single_select}")
```

**Expected Behavior:**
- CLI config overrides defaults
- Only specified options changed
- Other options use defaults

---

### 2.5 Config Merging

#### Test: CLI Overrides Inline
**Purpose:** Verify CLI config has highest priority

**Test Script:**
```python
from dv_tui import load_config, load_file

data = load_file("tests/data/test_inline_columns.json")
inline_config = load_config_from_inline_json(data)

cli_config = {"columns": ["status"]}

config = load_config(
    inline_config=inline_config,
    cli_config=cli_config
)

# CLI should win
assert config.columns == ["status"]  # From CLI
# Column widths from inline should still apply
assert config.column_widths == {"type": 10}  # From inline

print("✓ CLI overrides inline config correctly")
print(f"  Columns (CLI): {config.columns}")
print(f"  Column widths (inline): {config.column_widths}")
```

**Expected Behavior:**
- CLI config takes precedence
- Inline config merged where not overridden
- Defaults fill in remaining

---

#### Test: Inline Overrides File
**Purpose:** Verify inline config has medium priority

**Test Script:**
```python
from dv_tui import load_config, load_file

data = load_file("tests/data/test_inline_columns.json")
inline_config = load_config_from_inline_json(data)

config = load_config(
    config_path="tests/data/test_external_config.json",
    inline_config=inline_config
)

# Inline should override file
assert config.columns == ["type", "summary"]  # From inline

print("✓ Inline overrides file config correctly")
print(f"  Columns: {config.columns}")
```

**Expected Behavior:**
- Inline config overrides file config
- File config merges where not overridden
- Defaults fill in remaining

---

#### Test: Full Priority Chain
**Purpose:** Verify complete priority: CLI > Inline > File > Defaults

**Test Script:**
```python
from dv_tui import load_config, load_file

data = load_file("tests/data/test_inline_columns.json")
inline_config = load_config_from_inline_json(data)

cli_config = {
    "columns": ["type"],
    "single_select": True
}

config = load_config(
    config_path="tests/data/test_external_config.json",
    inline_config=inline_config,
    cli_config=cli_config
)

# Verify each level
assert config.columns == ["type"]  # CLI
assert config.column_widths == {"type": 10}  # Inline
assert config.keybinds is not None  # From external file
assert config.colors is not None  # From defaults

print("✓ Full priority chain works correctly")
print(f"  Columns (CLI): {config.columns}")
print(f"  Column widths (inline): {config.column_widths}")
```

**Expected Behavior:**
- Each config level contributes
- Lower levels merge where not overridden
- Final config is complete

---

## 3. Schema Validation Testing

### 3.1 Valid Configuration

#### Test: Valid Config Passes
**Purpose:** Verify valid configs pass validation

**Test Script:**
```python
from dv_tui.config import validate_config, Config

# Default config
config_dict = Config().to_dict()
error = validate_config(config_dict)
assert error is None

# External config
import json
with open("tests/data/test_external_config.json") as f:
    ext_config = json.load(f)
error = validate_config(ext_config)
assert error is None

print("✓ Valid configs pass validation")
```

**Expected Behavior:**
- No validation errors
- Returns None for valid configs

---

### 3.2 Invalid Configuration

#### Test: Invalid Type Detection
**Purpose:** Verify schema validation catches type errors

**Test Script:**
```python
from dv_tui.config import validate_config

# Invalid columns type
invalid_config = {
    "columns": "not_an_array"
}
error = validate_config(invalid_config)
assert error is not None
assert "columns" in error.lower()
assert "array" in error.lower()

# Invalid boolean type
invalid_config = {
    "drill_down": {
        "enabled": "not_boolean"
    }
}
error = validate_config(invalid_config)
assert error is not None
assert "drill_down" in error.lower()
assert "boolean" in error.lower()

print("✓ Invalid types detected correctly")
print(f"  Columns error: {error}")
```

**Expected Behavior:**
- Validation error returned
- Error message includes field name
- Error message indicates expected type

---

#### Test: Invalid Config from File
**Purpose:** Verify invalid file config is rejected

**Test Script:**
```python
from dv_tui import load_file, load_config_from_inline_json
from dv_tui.config import validate_config

data = load_file("tests/data/test_invalid_config.json")
inline_config = load_config_from_inline_json(data)

error = validate_config(inline_config)
assert error is not None

print("✓ Invalid config from file rejected")
print(f"  Error: {error}")
```

**Expected Behavior:**
- Validation error returned
- Error message is descriptive

---

## 4. TUI Integration Testing

### 4.1 Create TUI with Config

#### Test: TUI with Default Config
**Purpose:** Verify TUI uses config correctly

**Test Script:**
```python
from dv_tui import Config, TUI

config = Config()
tui = TUI(
    files=["tests/data/work_tasks.json"],
    single_select=False,
    config=config
)

# Verify TUI initialized
assert tui.config is config
assert tui.single_select == False
assert tui.files == ["tests/data/work_tasks.json"]

print("✓ TUI created with config correctly")
```

**Expected Behavior:**
- TUI object created
- Config assigned correctly
- All options applied

---

#### Test: TUI with Custom Config
**Purpose:** Verify custom config applied to TUI

**Test Script:**
```python
from dv_tui import load_config, TUI

config = load_config(config_path="tests/data/test_external_config.json")
config.single_select = True

tui = TUI(
    files=["tests/data/work_tasks.json"],
    single_select=True,
    config=config
)

# Verify custom config
assert tui.config.columns == ["status", "summary", "type"]
assert tui.single_select == True

print("✓ TUI created with custom config")
print(f"  Columns: {tui.config.columns}")
```

**Expected Behavior:**
- Custom config loaded
- All options applied to TUI

---

### 4.2 Data Loading with Config

#### Test: Load Data with Inline Config
**Purpose:** Verify inline config extracted when loading data

**Test Script:**
```python
from dv_tui import TUI

tui = TUI(
    files=["tests/data/test_inline_columns.json"],
    single_select=False
)

tui.load_data()

# Verify inline config applied
assert tui.config.columns == ["type", "summary"]

print("✓ Inline config applied when loading data")
print(f"  Columns: {tui.config.columns}")
```

**Expected Behavior:**
- Data loaded successfully
- Inline config extracted and merged
- TUI config updated

---

### 4.3 Column Widths Calculation

#### Test: Calculate Column Widths
**Purpose:** Verify `get_column_widths` works correctly

**Test Script:**
```python
from dv_tui.config import get_column_widths, Config

config = Config(
    columns=["type", "status", "summary"],
    column_widths={"type": 10, "status": 15}
)

# Calculate for 80-char terminal
widths = get_column_widths(config, 80)

# Verify fixed widths
assert widths[0] == 10  # type
assert widths[1] == 15  # status

# Verify remaining width goes to last column
remaining = 80 - 10 - 15 - 3  # subtract 2 columns + 2 separators + margin
assert widths[2] == remaining  # summary

print("✓ Column widths calculated correctly")
print(f"  Widths: {widths}")
```

**Expected Behavior:**
- Fixed columns use specified widths
- Last column gets remaining space
- Widths sum to terminal width

---

## 5. Advanced Configuration Testing

### 5.1 Nested Configuration

#### Test: Triggers Config Structure
**Purpose:** Verify nested trigger config works

**Test Script:**
```python
from dv_tui import load_config, load_file

data = load_file("tests/data/test_inline_triggers.json")
config = load_config(inline_config=data[0].get("_config", {}))

# Verify nested structure
assert config.triggers is not None
assert config.triggers.table is not None
assert config.triggers.rows is not None
assert config.triggers.cells is not None

# Verify trigger properties
assert config.triggers.table.on_enter is not None
assert "focus" in config.triggers.rows
assert "type" in config.triggers.cells

print("✓ Nested triggers config works")
print(f"  Table trigger: {config.triggers.table.on_enter}")
```

**Expected Behavior:**
- Nested config parsed correctly
- All trigger levels accessible
- Trigger commands stored

---

#### Test: Enum Config Structure
**Purpose:** Verify nested enum config works

**Test Script:**
```python
from dv_tui import load_config, load_file

data = load_file("tests/data/test_inline_enum.json")
config = load_config(inline_config=data[0].get("_config", {}))

# Verify enum config
assert config.enum is not None
assert config.enum.status is not None
assert config.enum.priority is not None

# Verify enum sources
assert config.enum.status.source == "inline"
assert config.enum.status.values == ["focus", "active", "pending", "done", "blocked"]

print("✓ Nested enum config works")
print(f"  Status enum values: {config.enum.status.values}")
```

**Expected Behavior:**
- Nested enum config parsed correctly
- Multiple enum fields supported
- Enum values stored

---

### 5.2 Complex Merging

#### Test: Merge Multiple Config Sources
**Purpose:** Verify complex merging scenarios

**Test Script:**
```python
from dv_tui import load_config

# All three sources
cli_config = {
    "columns": ["type"],
    "single_select": True
}

file_config_path = "tests/data/test_external_config.json"
inline_config = {
    "column_widths": {"type": 15, "status": 20},
    "drill_down": {"enabled": True}
}

config = load_config(
    config_path=file_config_path,
    inline_config=inline_config,
    cli_config=cli_config
)

# Verify final merged config
assert config.columns == ["type"]  # CLI
assert config.column_widths == {"type": 15, "status": 20}  # Inline
assert config.drill_down is not None  # Inline
assert config.keybinds is not None  # File
assert config.colors is not None  # File or default
assert config.single_select == True  # CLI
assert config.refresh is None  # Not in any source

print("✓ Complex merging works correctly")
print(f"  Final columns: {config.columns}")
```

**Expected Behavior:**
- All sources merged correctly
- Priority order respected
- No data lost in merge

---

## 6. Error Handling Testing

### 6.1 Invalid Config File

#### Test: Handle Invalid Config File
**Purpose:** Verify graceful handling of invalid file

**Test Script:**
```python
from dv_tui import load_config
import sys
from io import StringIO

# Capture stderr
old_stderr = sys.stderr
sys.stderr = StringIO()

try:
    config = load_config(config_path="tests/data/test_invalid_config.json")
    print("ERROR: Should have raised exception")
except Exception as e:
    error_msg = str(e)
    assert "config" in error_msg.lower() or "validation" in error_msg.lower()
    print(f"✓ Invalid config handled correctly: {error_msg}")

# Restore stderr
sys.stderr = old_stderr
```

**Expected Behavior:**
- Exception raised for invalid config
- Error message is descriptive
- No crash

---

### 6.2 Missing Config File

#### Test: Handle Missing Config File
**Purpose:** Verify behavior when config file doesn't exist

**Test Script:**
```python
from dv_tui import load_config

# Non-existent file should use defaults
config = load_config(config_path="/nonexistent/config.json")

# Should return defaults
assert config is not None
assert config.columns == ["type", "status", "summary"]

print("✓ Missing config file handled correctly (defaults used)")
```

**Expected Behavior:**
- No exception thrown
- Defaults returned
- Warning may be logged

---

## 7. Backward Compatibility Testing

### 7.1 Dict-Based Config

#### Test: Config from Dict
**Purpose:** Verify dict-based config still works (for legacy code)

**Test Script:**
```python
from dv_tui.config import merge_configs, DEFAULT_CONFIG

# Old-style config dict
old_config = {
    "columns": ["type", "summary"],
    "column_widths": {"type": 10}
}

# Merge with defaults
merged = merge_configs(DEFAULT_CONFIG.copy(), old_config)

# Verify merging
assert merged["columns"] == ["type", "summary"]
assert merged["column_widths"]["type"] == 10
assert "keybinds" in merged  # From defaults

print("✓ Dict-based config works (backward compatible)")
```

**Expected Behavior:**
- Dict merging works
- DEFAULT_CONFIG available as dict
- Legacy code still functional

---

## 8. Type Safety Testing

### 8.1 Type Annotations

#### Test: Config Type Checking
**Purpose:** Verify type hints are correct

**Test Script:**
```python
from dv_tui import Config, load_config
from typing import get_type_hints

# Check Config type hints
hints = get_type_hints(Config)
assert "columns" in hints
assert "keybinds" in hints
assert "triggers" in hints
assert "enum" in hints
assert "drill_down" in hints

print("✓ Type annotations are correct")
print(f"  Type hints: {hints}")
```

**Expected Behavior:**
- All fields have type hints
- Type hints are accurate
- IDE autocomplete works

---

## Test Checklist

### Config Dataclass
- [ ] Default config initialized correctly
- [ ] to_dict() works for all configs
- [ ] Subclass configs (KeybindConfig, ColorsConfig, etc.) work
- [ ] Optional fields can be None
- [ ] Required fields have defaults

### Config Loading
- [ ] Default config loads
- [ ] External config file loads
- [ ] Inline config extracted from data
- [ ] CLI config parsed correctly
- [ ] All sources merge with correct priority

### Schema Validation
- [ ] Valid configs pass validation
- [ ] Invalid configs rejected with clear error
- [ ] Type errors detected
- [ ] Required field errors detected

### TUI Integration
- [ ] TUI accepts Config object
- [ ] TUI applies config correctly
- [ ] Inline config extracted during data loading
- [ ] Column widths calculated correctly

### Advanced Features
- [ ] Nested configs (triggers, enum) work
- [ ] Complex merging scenarios work
- [ ] Partial configs merge correctly

### Error Handling
- [ ] Invalid config files handled gracefully
- [ ] Missing config files use defaults
- [ ] Validation errors are descriptive

### Backward Compatibility
- [ ] Dict-based config merging works
- [ ] DEFAULT_CONFIG available as dict
- [ ] Legacy code still functional

---

## Integration Test Script

Complete integration test script:

```python
#!/usr/bin/env python3
"""
Integration test for dv-tui configuration system.
Run all library tests in sequence.
"""

import sys
from dv_tui import Config, load_config, load_file, TUI
from dv_tui.config import validate_config, get_column_widths

def test_defaults():
    """Test default configuration."""
    config = Config()
    assert config.columns == ["type", "status", "summary"]
    assert config.single_select == False
    return True

def test_external_config():
    """Test external config file."""
    config = load_config(config_path="tests/data/test_external_config.json")
    assert config.columns == ["status", "summary", "type"]
    return True

def test_inline_config():
    """Test inline config extraction."""
    data = load_file("tests/data/test_inline_columns.json")
    from dv_tui import load_config_from_inline_json
    inline = load_config_from_inline_json(data)
    assert inline["columns"] == ["type", "summary"]
    return True

def test_config_priority():
    """Test config priority chain."""
    cli_config = {"columns": ["type"]}
    inline_config = {"column_widths": {"type": 15}}
    config = load_config(inline_config=inline_config, cli_config=cli_config)
    assert config.columns == ["type"]  # CLI wins
    assert config.column_widths == {"type": 15}  # Inline wins
    return True

def test_validation():
    """Test schema validation."""
    # Valid config
    config = Config().to_dict()
    assert validate_config(config) is None
    
    # Invalid config
    invalid = {"columns": "not_array"}
    assert validate_config(invalid) is not None
    return True

def test_tui_integration():
    """Test TUI with config."""
    config = load_config(config_path="tests/data/test_external_config.json")
    tui = TUI(files=["tests/data/work_tasks.json"], config=config)
    assert tui.config is config
    return True

def main():
    tests = [
        ("Defaults", test_defaults),
        ("External Config", test_external_config),
        ("Inline Config", test_inline_config),
        ("Config Priority", test_config_priority),
        ("Validation", test_validation),
        ("TUI Integration", test_tui_integration),
    ]
    
    print("=" * 50)
    print("dv-tui Library Integration Tests")
    print("=" * 50)
    
    failed = []
    for name, test in tests:
        try:
            test()
            print(f"✓ PASS: {name}")
        except AssertionError as e:
            print(f"✗ FAIL: {name} - {e}")
            failed.append(name)
        except Exception as e:
            print(f"✗ ERROR: {name} - {e}")
            failed.append(name)
    
    print("=" * 50)
    if failed:
        print(f"Failed tests: {', '.join(failed)}")
        return 1
    else:
        print("All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## Debugging Tips

If tests fail, check:

1. **Config Loading:**
   ```python
   from dv_tui import load_config
   config = load_config()
   print(config.__dict__)
   ```

2. **Validation Errors:**
   ```python
   from dv_tui.config import validate_config
   error = validate_config(your_config)
   print(f"Validation error: {error}")
   ```

3. **Config Merging:**
   ```python
   from dv_tui.config import merge_configs
   result = merge_configs(base, override)
   print(f"Merged: {result}")
   ```

4. **Type Checking:**
   ```python
   from typing import get_type_hints
   from dv_tui import Config
   print(get_type_hints(Config))
   ```

---

## Next Steps

After completing library tests, proceed to:
- `TESTING_CLI.md` - CLI interface testing
- Implement any missing features revealed by tests
- Add automated tests based on manual test scenarios
- Update documentation for library API
