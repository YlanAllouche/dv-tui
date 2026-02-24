# Debug Testing Instructions

## Running with Full Debug

To diagnose the issues with enum functionality, run this:

```bash
./test_dv_debug.sh
```

This will:
1. Start dv-tui with the test configuration
2. Log all activity to `/tmp/dv_keys.txt`
3. After you quit, show a summary of what happened

## What to Test

### Step 1: Verify Basic Functionality
- Can you navigate with `j`/`k`/`h`/`l`?
- Can you switch to cell mode with `c`?
- Can you quit with `q`?

**Check in log**: Look for "Processing key" messages for these keys.

### Step 2: Test Enum Keys
- In cell mode, press `Ctrl+e`
- In cell mode, press `e` and `E`
- In cell mode, navigate to status or priority column

**Check in log**: Look for:
- "Key: 5" (Ctrl+e)
- "Key: 101" (e)
- "Key: 69" (E)
- "Processing key 5/101/69" messages
- "enum_picker" or "enum_cycle" messages
- Any SKIPPED messages (will tell you why it skipped)

### Step 3: Test Color Cycling
- Navigate through different rows
- Look at the status and priority columns

**Expected**: Each unique value should have its own color.

## Analyzing the Log

After quitting, the script will show:

1. **Key codes for 5, 101, 69**
   - If you see these codes, keys are being detected
   - If you don't see them, terminal issue

2. **Enum function calls**
   - "enum_picker" - Popup dialog was called
   - "enum_cycle" - Cycling was called
   - SKIPPED messages - Why it skipped (mode, no config, no options)

3. **Render calls**
   - "render() called" - Render was invoked
   - "After render" - Render completed
   - If you see one but not the other, crash occurred

4. **Errors/exceptions**
   - Any errors or tracebacks that occurred

## Expected Debug Output

When you press Ctrl+e, e, or E, you should see:

```
Loop start
After check_and_reload
render() called
After render
Key: 5           (or 101 or 69)
Processing key 5      (or 101 or 69)
-> is_enum_picker_key (or is_enum_cycle_key)
_handle_enum_picker called (or _handle_enum_cycle)
```

## If You Don't See This

### Case 1: No "Processing key" messages
**Problem**: Code is crashing or returning early in the loop.

**Solution**: Check for:
- "render() returning early" - Table is None
- No render messages at all - Crash during initialization

### Case 2: Keys detected but handlers not called
**Problem**: Key handlers aren't being triggered.

**Solution**: Check for:
- "SKIPPED" messages - Will say why (mode, no config, etc.)
- Verify you're in cell mode
- Verify column has enum config

### Case 3: No key codes detected
**Problem**: Terminal isn't sending the keys.

**Solution**: Run `python test_curses_keys.py` to verify terminal key detection.

## Minimal Test

If dv-tui is crashing, try a minimal version:

```bash
python test_loop_structure.py
```

This tests just the loop structure without all the complex rendering logic.

## What to Report

Please provide:
1. The output from `./test_dv_debug.sh` after you quit
2. Any "SKIPPED" messages in the log
3. Whether you're in cell mode when testing enum keys
4. Which column is selected when pressing enum keys
5. Your terminal type (from env: `echo $TERM`)

This will help identify the exact issue.
