# Enum Implementation Status & Troubleshooting

## Current Implementation

### Features Implemented
1. ✅ EnumChoiceDialog - Popup dialog with arrow key navigation
2. ✅ Three enum sources: inline, inferred, external
3. ✅ Color cycling for ALL enum fields (not just status)
4. ✅ Key bindings:
   - `e` - Cycle to next enum value (cell mode only)
   - `E` - Cycle to previous enum value (cell mode only)
   - `Ctrl+e` - Open enum picker popup (cell mode only)
5. ✅ Value update after selection
6. ✅ Trigger support for on_change events

### Important Requirements
**You MUST be in CELL MODE for enum functionality to work.**
- Press `c` to toggle between row and cell mode
- The footer should indicate which mode you're in

### Column Configuration
Only columns with enum configuration will have:
- Color cycling
- e/E cycling
- Ctrl+e popup

Check your config file - each field that should have enum support needs to be listed:
```json
{
  "enum": {
    "status": { "source": "inline", "values": [...] },
    "priority": { "source": "inline", "values": [...] }
  }
}
```

## Troubleshooting Keys Not Working

### Step 1: Check Your Mode
- Are you in CELL mode? (Press `c` to toggle)
- The footer should say "cell mode" not "row mode"

### Step 2: Check Key Codes
Run this to see what keys are being detected:
```bash
tail -f /tmp/dv_keys.txt
```

Expected codes:
- `Ctrl+e` → `5`
- `e` → `101`
- `E` → `69`

### Step 3: Check Debug Logs
When you press enum keys, check the log for:
- `Processing key 5` (or 101/69)
- `-> is_enum_picker_key` or `-> is_enum_cycle_key`
- `_handle_enum_picker called` or similar

### Step 4: Check for Skip Messages
If you see `SKIPPED` messages in the log:
- `SKIPPED: mode=row` → You're in row mode, press `c`
- `SKIPPED: no enum_config for field_name` → Column has no enum config
- `SKIPPED: no options` → Enum source returned no values

### Step 5: Test with Debug Script
```bash
./test_enum_debug.sh
```

This will show you a summary of what happened after you quit.

## Terminal Issues

### Terminal Intercepting Keys
Some terminals or terminal emulators might intercept certain key combinations:

**Try alternative ways to press Ctrl+e:**
- `Ctrl + e` (hold Ctrl, press e)
- `Ctrl + E` (hold Ctrl, shift+e)
- `Ctrl + e` in a different terminal (e.g., xterm, gnome-terminal, konsole)

**Alternative: Use e/E for cycling instead**
If Ctrl+e doesn't work, just use:
- `e` for next value
- `E` for previous value

### Check Terminal Support
Some terminals don't support all key codes. Test in a fresh terminal:
```bash
# Test key detection
read -n1 key
echo "Key code: ${key}"
```

Test with Ctrl+e, e, E to see what codes you get.

## Test Data

The current test data has these columns:
- `id` - No enum config
- `priority` - Has enum config (inline: low, medium, high, critical)
- `status` - Has enum config (inline: todo, in-progress, done, cancelled)
- `summary` - No enum config

Only `priority` and `status` columns should have:
- Color cycling
- e/E cycling
- Ctrl+e popup

## What to Report

If things aren't working, please report:
1. The exact key codes from `/tmp/dv_keys.txt` when you press enum keys
2. Any "SKIPPED" messages in the log
3. Whether you're in cell mode or row mode
4. Which column is selected (id, priority, status, summary)
5. Your terminal type (bash, zsh, xterm, etc.)

This will help identify the specific issue.
