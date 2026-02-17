# Lifecycle Triggers - Complete Implementation

## Summary

Successfully implemented three new trigger events that fire at key points in the TUI lifecycle:

- ✅ **on_startup** - Fires when TUI loads (once per session)
- ✅ **on_drilldown** - Fires when drilling down into nested data
- ✅ **on_backup** - Fires when backing up from drill-down level

All events:
- Available at table/row/cell levels
- Follow priority system (cell > row > table)
- Default to async execution (non-blocking)
- Pass all context variables correctly as environment variables

## Quick Start

```bash
# Run the automated test script
./tests/test_trigger_lifecycle.sh

# Or run manually
python dv.py tests/trigger_lifecycle_data.json --config tests/trigger_lifecycle_config.json
```

## Expected Behavior

### 1. on_startup Trigger

**When:** TUI starts and loads initial data

**Notification:**
```
TUI Started
Data source: tests/trigger_lifecycle_data.json
```

**Context variables available:**
- `$DV_DATA_SOURCE` - File path being loaded
- `$DV_CONFIG_FILE` - Config file path
- Standard variables (`DV_SELECTED_INDEX`, etc.)

---

### 2. on_drilldown Trigger

**When:** Pressing Enter on a drillable cell (arrays `[]` or objects `{}`)

**Notification:**
```
Drill Down
Field: tasks, Depth: 0
```

**Context variables available:**
- `$DV_DRILL_DEPTH` - Current navigation depth (0, 1, 2...)
- `$DV_DRILL_FIELD` - Field name being drilled into
- `$DV_DRILL_VALUE` - JSON string of drilled value
- `$DV_PARENT_DATA` - JSON string of parent row data
- Standard variables

---

### 3. on_backup Trigger

**When:** Pressing ESC to back up from drill-down level

**Notification:**
```
Backup
Backing up from level 1 to context with {"selected_index": 0, "parent_context": ...}
```

**Context variables available:**
- `$DV_BACKUP_DEPTH` - Depth after backing up (stack size)
- `$DV_BACKUP_TO` - JSON string of backed-up context
- Standard variables (for the restored view)

---

## Test Data Structure

The test file includes three different nested structures:

1. **Row 0 (Project Alpha)**: Has `tasks` array → `[]` drillable
2. **Row 1 (Project Beta)**: Has `settings` object → `{}` drillable
3. **Row 2 (Project Gamma)**: Has `tags` array → `[]` drillable

This allows testing different drill-down scenarios.

## Documentation

- **`tests/LIFECYCLE_TRIGGERS.md`** - Comprehensive documentation with all details
- **`tests/LIFECYCLE_README.md`** - Quick start guide
- **`tests/IMPLEMENTATION_SUMMARY.md`** - Technical implementation details
- **`tests/CONTEXT_VARS_FIX.md`** - Explanation of context variable fix

## Files Modified

| File | Lines Changed | Description |
|-------|---------------|-------------|
| `dv_tui/config.py` | ~50 | Added new trigger fields and schema |
| `dv_tui/handlers.py` | ~40 | Added trigger loading and execution methods |
| `dv_tui/core.py` | ~20 | Integrated triggers at lifecycle points |
| `dv_tui/triggers.py` | ~30 | Updated environment building for new vars |

## Files Created

| File | Purpose |
|-------|---------|
| `tests/trigger_lifecycle_data.json` | Test data with nested structures |
| `tests/trigger_lifecycle_config.json` | Config with lifecycle triggers |
| `tests/test_trigger_lifecycle.sh` | Automated test script |
| `tests/LIFECYCLE_TRIGGERS.md` | Full documentation |
| `tests/LIFECYCLE_README.md` | Quick start guide |
| `tests/IMPLEMENTATION_SUMMARY.md` | Implementation details |
| `tests/CONTEXT_VARS_FIX.md` | Context variable fix explanation |

## Critical Fix

**Issue:** Context variables were not being passed to triggers (notifications appeared but without data)

**Solution:** Updated `_build_environment()` to dynamically add all `DV_` prefixed context variables

**Result:** All lifecycle triggers now receive their full context correctly

## Testing

All tests pass:
- ✅ Module imports work
- ✅ TriggerConfig has new fields
- ✅ Config loading works
- ✅ KeyHandler loads triggers
- ✅ Environment variables passed correctly
- ✅ Trigger execution works
- ✅ Python files compile without errors
- ✅ Schema validation passes

## Priority System

All three new events follow the existing priority system:

1. **Cell trigger** - If cell-specific trigger exists for selected cell
2. **Row trigger** - If row-specific trigger exists for selected row
3. **Table trigger** - Default/fallback trigger

## Use Cases

- **Session logging** with `on_startup`
- **Navigation analytics** with `on_drilldown` and `on_backup`
- **Dynamic data loading** when drilling into specific fields
- **Context restoration** on navigation history
- **Notification system** for lifecycle events

## Next Steps

The implementation is complete and tested. Consider:

1. Run the test script to verify in your environment
2. Try different data structures
3. Test with notify-send or your preferred notification tool
4. Explore priority system with table/row/cell triggers
5. Integrate into your workflow

---

## Notes

- All lifecycle triggers default to `async_: true` (non-blocking)
- `on_startup` only fires once per TUI session (not on tab switch)
- Context variables use `$DV_...` syntax for shell commands
- Python function triggers (library usage) receive context as a dict
- The `on_enter` event still exists and fires on Enter key press
- Lifecycle triggers are additive, not replacements for existing events
