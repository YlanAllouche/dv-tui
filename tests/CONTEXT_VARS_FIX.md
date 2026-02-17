# Fix: Context Variables Not Being Passed to Triggers

## Problem

When testing the lifecycle triggers (`on_startup`, `on_drilldown`, `on_backup`), notifications were appearing but **no data was being substituted** into the environment variables.

For example, this command:
```json
{
  "command": "notify-send \"TUI Started\" \"Data source: $DV_DATA_SOURCE\""
}
```

Was showing: "Data source: " instead of "Data source: tests/trigger_lifecycle_data.json"

## Root Cause

The `_build_environment()` method in `dv_tui/triggers.py` only explicitly handled 4 standard context variables:
- `DV_SELECTED_CELL`
- `DV_SELECTED_ROW`
- `DV_SELECTED_INDEX`
- `DV_SELECTED_COLUMN`

When we added new context variables for lifecycle triggers:
- `DV_DATA_SOURCE`
- `DV_CONFIG_FILE`
- `DV_DRILL_DEPTH`
- `DV_DRILL_FIELD`
- `DV_DRILL_VALUE`
- `DV_PARENT_DATA`
- `DV_BACKUP_DEPTH`
- `DV_BACKUP_TO`

These were being passed in the `context` dict to the trigger executor, but **not being set as environment variables** for the subprocess.

## Solution

Updated `_build_environment()` method to automatically add **all** context variables that start with `DV_` prefix to the environment.

### Before (dv_tui/triggers.py:159-180)

```python
def _build_environment(self, context: Dict[str, Any], additional_env: Dict[str, str]) -> Dict[str, str]:
    """Build environment variables from context and additional env."""
    process_env = os.environ.copy()

    selected_cell = context.get("selected_cell")
    if selected_cell is not None:
        process_env["DV_SELECTED_CELL"] = str(selected_cell)

    selected_row = context.get("selected_row")
    if selected_row is not None:
        process_env["DV_SELECTED_ROW"] = json.dumps(selected_row)

    selected_index = context.get("selected_index")
    if selected_index is not None:
        process_env["DV_SELECTED_INDEX"] = str(selected_index)

    selected_column = context.get("selected_column")
    if selected_column is not None:
        process_env["DV_SELECTED_COLUMN"] = str(selected_column)

    process_env.update(additional_env)
    return process_env
```

**Problem:** Only 4 hardcoded variables were set.

### After (dv_tui/triggers.py:159-181)

```python
def _build_environment(self, context: Dict[str, Any], additional_env: Dict[str, str]) -> Dict[str, str]:
    """Build environment variables from context and additional env."""
    process_env = os.environ.copy()

    selected_cell = context.get("selected_cell")
    if selected_cell is not None:
        process_env["DV_SELECTED_CELL"] = str(selected_cell)

    selected_row = context.get("selected_row")
    if selected_row is not None:
        process_env["DV_SELECTED_ROW"] = json.dumps(selected_row)

    selected_index = context.get("selected_index")
    if selected_index is not None:
        process_env["DV_SELECTED_INDEX"] = str(selected_index)

    selected_column = context.get("selected_column")
    if selected_column is not None:
        process_env["DV_SELECTED_COLUMN"] = str(selected_column)

    # Add all additional context variables as environment variables
    for key, value in context.items():
        # Skip the standard ones we already handled
        if key not in ["selected_cell", "selected_row", "selected_index", "selected_column"]:
            # Only add if key starts with DV_ prefix (to avoid adding internal context vars)
            if key.startswith("DV_"):
                process_env[key] = str(value)

    process_env.update(additional_env)
    return process_env
```

**Solution:** Dynamically adds all context variables starting with `DV_` prefix.

## Benefits

1. **Automatic**: Any new context variable added to the dict will automatically be available as an environment variable
2. **Safe**: Only variables starting with `DV_` prefix are added, avoiding internal context keys
3. **Backward Compatible**: Existing 4 standard variables still work exactly as before
4. **Future-Proof**: Adding new context variables doesn't require updating `_build_environment()`

## Verification

### Test Case 1: Standard Variables
```python
context = {
    'selected_index': 5,
    'selected_cell': 'My Value'
}
env = executor._build_environment(context, {})
assert env['DV_SELECTED_INDEX'] == '5'
assert env['DV_SELECTED_CELL'] == 'My Value'
```
✅ Works

### Test Case 2: Lifecycle Variables
```python
context = {
    'DV_DATA_SOURCE': 'data.json',
    'DV_DRILL_DEPTH': '2',
    'DV_DRILL_FIELD': 'tasks'
}
env = executor._build_environment(context, {})
assert env['DV_DATA_SOURCE'] == 'data.json'
assert env['DV_DRILL_DEPTH'] == '2'
assert env['DV_DRILL_FIELD'] == 'tasks'
```
✅ Works

### Test Case 3: Mixed Variables
```python
context = {
    'selected_index': 0,
    'DV_DATA_SOURCE': 'test.json',
    'DV_CONFIG_FILE': 'config.json',
    'DV_DRILL_VALUE': '[{"key": "value"}]'
}
env = executor._build_environment(context, {})
assert 'DV_SELECTED_INDEX' in env
assert 'DV_DATA_SOURCE' in env
assert 'DV_CONFIG_FILE' in env
assert 'DV_DRILL_VALUE' in env
```
✅ Works

## Impact

This fix ensures that:
- ✅ `on_startup` triggers receive `DV_DATA_SOURCE` and `DV_CONFIG_FILE`
- ✅ `on_drilldown` triggers receive `DV_DRILL_DEPTH`, `DV_DRILL_FIELD`, `DV_DRILL_VALUE`, `DV_PARENT_DATA`
- ✅ `on_backup` triggers receive `DV_BACKUP_DEPTH` and `DV_BACKUP_TO`
- ✅ All standard variables continue to work as before
- ✅ Future context variables will work automatically

## Files Changed

- `dv_tui/triggers.py:159-181` - Updated `_build_environment()` method
