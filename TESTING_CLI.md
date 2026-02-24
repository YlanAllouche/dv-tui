# CLI Testing Guide - dv-tui Configuration System

This guide provides comprehensive manual testing scenarios for the configuration system using the CLI interface.

## Test Data Location

All test data files are located in `tests/data/`:
- `work_tasks.json`, `study_tasks.json` - Standard test data
- `test_inline_*.json` - Files with inline `_config` sections
- `test_external_config.json` - External config file
- `test_invalid_config.json` - Invalid config for validation testing

---

## 1. CLI Flag Testing

### 1.1 Basic Configuration Flags

#### Test: Columns Filtering
**Purpose:** Verify `--columns` flag filters and reorders columns

**Commands:**
```bash
# Show only type and status columns
python -m dv_tui.cli tests/data/work_tasks.json --columns "type,status"

# Show summary and status (reordered)
python -m dv_tui.cli tests/data/work_tasks.json --columns "summary,status"

# Single column only
python -m dv_tui.cli tests/data/work_tasks.json --columns "summary"
```

**Expected Behavior:**
- Only specified columns are displayed
- Columns appear in the order specified
- Column widths adjust automatically
- Header row shows filtered columns

**Verification:**
- Count visible columns (should match number in --columns)
- Check column order matches command
- Navigate through data to ensure all fields are accessible

---

#### Test: External Config File
**Purpose:** Verify `--config` flag loads external configuration

**Commands:**
```bash
# Load external config
python -m dv_tui.cli tests/data/work_tasks.json --config tests/data/test_external_config.json

# Verify external config takes precedence over defaults
python -m dv_tui.cli tests/data/work_tasks.json --config tests/data/test_external_config.json --columns "type"
```

**Expected Behavior:**
- External config is loaded and applied
- Config from file overrides defaults
- CLI flags override file config (second example)

**Verification:**
- Column order should be: status, summary, type (from external config)
- Column widths should reflect external config settings
- In second example, CLI `--columns "type"` should override external config

---

#### Test: Refresh Settings
**Purpose:** Verify refresh-related flags work correctly

**Commands:**
```bash
# Enable auto-refresh with custom interval
python -m dv_tui.cli tests/data/test_inline_refresh.json --refresh --refresh-interval 2.0

# Disable auto-refresh
python -m dv_tui.cli tests/data/work_tasks.json --no-refresh

# Use command for data generation
echo '[{"type":"test","status":"active","summary":"generated"}]' | python -m dv_tui.cli -c "cat tests/data/work_tasks.json" --refresh
```

**Expected Behavior:**
- Auto-refresh enabled with specified interval (first example)
- Auto-refresh disabled when `--no-refresh` is used
- Command flag provides data source for refresh

**Verification:**
- Monitor file modification detection (change external file, watch for reload)
- Check that refresh interval matches `--refresh-interval` value
- Verify command execution for data refresh

---

#### Test: Single-Select Mode
**Purpose:** Verify `-s` flag exits after selection

**Commands:**
```bash
# Single-select mode
python -m dv_tui.cli -s tests/data/work_tasks.json
```

**Expected Behavior:**
- TUI launches normally
- Pressing Enter on an item opens it
- TUI exits immediately after opening

**Verification:**
- Select any item and press Enter
- Confirm TUI exits without further interaction
- Verify selected item was opened correctly

---

## 2. Inline Configuration Testing

### 2.1 Columns Configuration

#### Test: Inline Columns Filter
**Purpose:** Verify inline `_config.columns` filters columns

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_columns.json
```

**Expected Behavior:**
- Only `type` and `summary` columns are shown
- `status` column is not displayed
- Column width for `type` is 10 characters

**Verification:**
- Count visible columns (should be 2: type, summary)
- Try to access `status` column (should not exist)
- Check `type` column width matches config

---

#### Test: CLI Overrides Inline
**Purpose:** Verify CLI flags override inline config

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_columns.json --columns "status,type"
```

**Expected Behavior:**
- CLI `--columns` takes precedence
- `status` and `type` columns shown (not `summary`)
- Inline config columns ignored

**Verification:**
- Visible columns: status, type
- Inline config's `summary` column not shown
- Column widths calculated from CLI values

---

### 2.2 Keybinds Configuration

#### Test: Custom Keybinds
**Purpose:** Verify inline keybinds are loaded correctly

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_keybinds.json
```

**Expected Behavior:**
- Leader key is semicolon (`;`)
- Down works with `j` or `↓`
- Up works with `k` or `↑`

**Verification:**
- Press `j` - should move down
- Press `k` - should move up
- Press arrow keys - should also work
- Press `;` - should enter leader mode

---

### 2.3 Triggers Configuration

#### Test: Table-Level Triggers
**Purpose:** Verify table triggers execute on events

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_triggers.json
```

**Expected Behavior:**
- `on_enter` trigger executes when TUI starts
- Triggers should be async (non-blocking)
- Commands should execute in background

**Verification:**
- Check `/tmp/` for trigger output logs
- Ensure TUI remains responsive during trigger execution
- Verify table triggers execute on load

---

#### Test: Row-Level Triggers
**Purpose:** Verify row triggers execute on row selection

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_triggers.json
```

**Expected Behavior:**
- Select a row with `status: focus`
- `on_select` trigger for "focus" executes

**Verification:**
- Navigate to row with "focus" status
- Press Enter to select
- Check for trigger execution log
- Row data should be passed as environment variable

---

#### Test: Cell-Level Triggers
**Purpose:** Verify cell triggers execute on cell changes

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_triggers.json
```

**Expected Behavior:**
- `on_change` trigger executes when `type` cell changes
- Cell data passed to trigger command

**Verification:**
- (Note: Cell editing may not be fully implemented yet)
- Check trigger config in data file
- Verify trigger commands are defined

---

### 2.4 Enum Configuration

#### Test: Inline Enum Values
**Purpose:** Verify enum picker shows inline values

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_enum.json
```

**Expected Behavior:**
- `status` field has predefined values: focus, active, pending, done, blocked
- `priority` field has: high, medium, low
- Enum picker shows these values when triggered

**Verification:**
- Open enum picker (may need to implement this feature first)
- Verify available values match config
- Check multiple enum fields work independently

---

### 2.5 Drill-Down Configuration

#### Test: Drill-Down to Nested Data
**Purpose:** Verify drill-down navigates to nested arrays

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_drilldown.json
```

**Expected Behavior:**
- `items` field contains arrays
- Drill-down is enabled
- Can navigate into nested items

**Verification:**
- Select a row with `items` array
- Press Enter on `items` cell (if in cell mode)
- View nested items as new data set
- Check back navigation works

---

### 2.6 Refresh Configuration

#### Test: Inline Refresh Settings
**Purpose:** Verify inline refresh config works

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_refresh.json
```

**Expected Behavior:**
- Refresh enabled
- Refresh interval: 1.0 second
- Command specified for data generation

**Verification:**
- Modify external file while TUI is running
- Watch for data reload after 1 second
- Verify `last_updated` field changes

---

### 2.7 Tabs Configuration

#### Test: Inline Tabs
**Purpose:** Verify inline tabs load external files

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_tabs.json
```

**Expected Behavior:**
- First tab: `work_tasks.json`
- Second tab: `study_tasks.json`
- Use `h`/`l` to switch between tabs

**Verification:**
- Check tab titles match file names
- Navigate between tabs with arrow keys
- Verify each tab shows correct data

---

## 3. Validation Testing

### 3.1 Invalid Configuration

#### Test: Schema Validation
**Purpose:** Verify invalid configs are rejected with clear error

**Commands:**
```bash
# Invalid inline config
python -m dv_tui.cli tests/data/test_invalid_config.json

# Invalid external config
echo '{"columns":"wrong","drill_down":{"enabled":"no"}}' > /tmp/bad_config.json
python -m dv_tui.cli tests/data/work_tasks.json --config /tmp/bad_config.json
```

**Expected Behavior:**
- Error message displayed
- TUI does not start
- Error indicates what's invalid

**Verification:**
- Read error message carefully
- Confirm it mentions the invalid field and expected type
- No TUI window opens

---

## 4. Config Priority Testing

### 4.1 CLI > Inline > File > Defaults

#### Test: Full Priority Chain
**Purpose:** Verify config merging follows correct priority

**Setup:**
```bash
# 1. Create default config (defaults are built-in)
# 2. Create external config
cat tests/data/test_external_config.json
# 3. Use inline config file
# 4. Apply CLI flag
```

**Command:**
```bash
python -m dv_tui.cli tests/data/test_inline_columns.json \
  --config tests/data/test_external_config.json \
  --columns "type"
```

**Expected Behavior:**
- `--columns "type"` (CLI) - HIGHEST PRIORITY → Shows only `type`
- Inline config - MEDIUM → `type, summary`
- External config - LOW → `status, summary, type`
- Defaults - LOWEST → `type, status, summary`

**Verification:**
- Only `type` column is shown
- Inline and external configs are overridden
- Verify CLI flag wins

---

#### Test: Partial Config Override
**Purpose:** Verify only specified options are overridden

**Command:**
```bash
python -m dv_tui.cli tests/data/test_external_config.json --columns "type,status"
```

**Expected Behavior:**
- Columns from CLI flag (priority 1)
- Column widths from external config (not overridden)
- Keybinds from external config (not overridden)

**Verification:**
- Check columns: type, status (from CLI)
- Check widths: should match external config
- Check keybinds: leader key is `;` (from external)

---

## 5. Multi-File Testing

### 5.1 Multiple Tabs

#### Test: Multiple Files as Tabs
**Purpose:** Verify tab switching works with multiple files

**Commands:**
```bash
# Two files
python -m dv_tui.cli tests/data/work_tasks.json tests/data/study_tasks.json

# Three files
python -m dv_tui.cli tests/data/work_tasks.json tests/data/study_tasks.json tests/data/mixed_tasks.csv
```

**Expected Behavior:**
- Each file is a separate tab
- Tab names are beautified file names
- `h`/`l` switch between tabs
- Each tab maintains its own scroll position

**Verification:**
- Count tabs at top of screen
- Navigate to different tabs
- Verify data changes per tab
- Check scroll position is preserved per tab

---

### 5.2 Mixed File Types

#### Test: JSON + CSV
**Purpose:** Verify different file types work together

**Command:**
```bash
python -m dv_tui.cli tests/data/work_tasks.json tests/data/mixed_tasks.csv
```

**Expected Behavior:**
- JSON file loads correctly
- CSV file loads correctly
- Both display in tabs

**Verification:**
- Switch between JSON and CSV tabs
- Verify JSON shows data correctly
- Verify CSV shows data correctly
- Check column detection works for both

---

## 6. Help and Documentation

### 6.1 Help Text

#### Test: Comprehensive Help
**Purpose:** Verify help text is complete and accurate

**Command:**
```bash
python -m dv_tui.cli --help
```

**Expected Behavior:**
- Shows all CLI flags
- Shows usage examples
- Shows flag descriptions

**Verification:**
- Check all new flags are documented
- Verify descriptions are accurate
- Check examples are helpful

---

## Test Checklist

### Core Functionality
- [ ] CLI flags parse correctly
- [ ] External config loads from file
- [ ] Inline config loads from data
- [ ] Config merges with correct priority
- [ ] Invalid config shows clear error

### Configuration Options
- [ ] Columns filter and reorder
- [ ] Column widths apply correctly
- [ ] Keybinds load and work
- [ ] Triggers execute (when implemented)
- [ ] Enum values defined (when implemented)
- [ ] Drill-down enabled (when implemented)
- [ ] Refresh settings apply
- [ ] Tabs load from config

### Multi-Source Testing
- [ ] CLI overrides inline config
- [ ] Inline overrides external config
- [ ] External overrides defaults
- [ ] Partial configs merge correctly

### File Handling
- [ ] Single JSON file loads
- [ ] Single CSV file loads
- [ ] Multiple files as tabs
- [ ] Mixed file types (JSON + CSV)

### User Experience
- [ ] Help text is complete
- [ ] Error messages are clear
- [ ] Defaults are sensible
- [ ] Configuration is flexible

---

## Debugging Tips

If tests fail, check:

1. **Config Loading Issues:**
   ```bash
   # Debug config loading
   python -c "from dv_tui import load_config; print(load_config())"
   ```

2. **Schema Validation Issues:**
   ```bash
   # Check validation errors
   python -c "from dv_tui.config import validate_config; print(validate_config(your_config))"
   ```

3. **File Loading Issues:**
   ```bash
   # Test data loading directly
   python -c "from dv_tui import load_file; print(load_file('tests/data/work_tasks.json'))"
   ```

4. **Log Files:**
   - Check `/tmp/dv_keys.txt` for key press logs
   - Check stderr for error messages

---

## Next Steps

After completing CLI tests, proceed to:
- `TESTING_LIBRARY.md` - Library API testing
- Implement any missing features revealed by tests
- Add automated tests based on manual test scenarios
