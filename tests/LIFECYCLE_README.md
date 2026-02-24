# Lifecycle Triggers - Quick Start

## What's New

Three new trigger events have been added to dv-tui:

1. **on_startup** - Fires when TUI starts (once per session)
2. **on_drilldown** - Fires when drilling into nested data
3. **on_backup** - Fires when backing up from drill-down level

## Quick Test

```bash
# Run the automated test script
./tests/test_trigger_lifecycle.sh

# Or run manually
python dv.py tests/trigger_lifecycle_data.json --config tests/trigger_lifecycle_config.json
```

## Test Scenario

The test data includes three rows with different nested structures:

1. **Row 0 (Project Alpha)**: Has a `tasks` array → drillable `[]`
2. **Row 1 (Project Beta)**: Has a `settings` object → drillable `{}`
3. **Row 2 (Project Gamma)**: Has a `tags` array → drillable `[]`

### Steps to Test

1. **Startup test:**
   - Run dv-tui
   - ✅ Should see "TUI Started" notification with data source path

2. **Drill-down test (row 0):**
   - Press 'c' to enter cell mode
   - Navigate to `tasks[]` column
   - Press Enter to drill down
   - ✅ Should see "Drill Down" notification (field=tasks, depth=0)

3. **Backup test:**
   - Press ESC to back up
   - ✅ Should see "Backup" notification (backup_level=0)

4. **Drill-down test (row 1):**
   - Navigate to row 1
   - Press 'c' for cell mode
   - Navigate to `settings{}` column
   - Press Enter to drill down
   - ✅ Should see "Drill Down" notification (field=settings, depth=1)

5. **Backup test (depth):**
   - Press ESC to back up
   - ✅ Should see "Backup" notification (backup_level=1)

## Context Variables

Each event provides special context variables:

### on_startup
- `$DV_DATA_SOURCE` - File path being loaded
- `$DV_CONFIG_FILE` - Config file path (if specified)

### on_drilldown
- `$DV_DRILL_DEPTH` - Current navigation depth (0, 1, 2...)
- `$DV_DRILL_FIELD` - Field name being drilled into
- `$DV_DRILL_VALUE` - JSON string of the drilled value
- `$DV_PARENT_DATA` - JSON string of parent row data

### on_backup
- `$DV_BACKUP_DEPTH` - Depth after backing up
- `$DV_BACKUP_TO` - JSON string of the backed-up context

## Documentation

See `tests/LIFECYCLE_TRIGGERS.md` for complete documentation including:
- Detailed event descriptions
- All available context variables
- Priority system (cell > row > table)
- Real-world examples
- Migration guide from `on_enter`

## Files

- `tests/trigger_lifecycle_data.json` - Test data with nested structures
- `tests/trigger_lifecycle_config.json` - Config with lifecycle triggers
- `tests/test_trigger_lifecycle.sh` - Automated test script
- `tests/LIFECYCLE_TRIGGERS.md` - Full documentation
