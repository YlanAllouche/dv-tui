# Enum Choice Tool Testing Guide

This guide provides CLI examples to test enum choice tool functionality.

## Quick Start with Debugging

**IMPORTANT**: Use the debug test script to see what's happening:

```bash
./test_enum_debug.sh
```

This will:
1. Start dv-tui with enum configuration
2. Show instructions for testing
3. After you quit, show the key log with enum-related key presses

**To see key presses in real-time** (in another terminal):
```bash
tail -f /tmp/dv_keys.txt
```

## Expected Key Codes

When you press enum-related keys, you should see these codes in the log:
- **Ctrl+e** → key code `5`
- **e** → key code `101`
- **E** → key code `69`

## Step-by-Step Testing

### 1. Enter Cell Mode
Press `c` to toggle from row mode to cell mode.

**How to check**: The footer should show "cell mode" and selected column should be highlighted.

### 2. Navigate to Enum Column
Use `h`/`l` to navigate to a column with enum configuration (status or priority).

**How to check**: The selected cell should be on the status or priority column.

### 3. Test Enum Picker (Ctrl+e)
Press `Ctrl+e` to open the enum picker popup.

**Expected**: A popup dialog should appear with the enum options.
**If it doesn't work**: Check the key log - you should see key code `5` and "enum_picker" or "SKIPPED" messages.

### 4. Test Enum Cycling (e/E)
Press `e` to cycle to next value, `E` to cycle to previous value.

**Expected**: The cell value should change immediately.
**If it doesn't work**: Check the key log - you should see key code `101` or `69` and "enum_cycle" messages.

### 5. Check Color Cycling
Navigate through different rows and observe the colors of the status and priority columns.

**Expected**: Each unique value should have its own color.
**How to verify**: All "todo" values should be the same color, all "in-progress" values should be another color, etc.

## Test Files Created

1. `test_enum_tasks.json` - Simple task list with status/priority fields
2. `test_enum_comprehensive.json` - More complex data with multiple status values
3. `test_enum_priority_source.sh` - External command script for priority enums
4. `test_enum_config_inline.json` - Config with inline enum values (status & priority)
5. `test_enum_config_inferred.json` - Config with inferred enum source
6. `test_enum_config_external.json` - Config with external enum source
7. `test_enum_config_mixed.json` - Config demonstrating all three enum sources
8. `test_enum_debug.sh` - Debug test script with key logging

## Test Scenarios

### 1. Inline Enum Source (Predefined Values)

Test enum cycling with hardcoded values from config:

```bash
python dv.py test_enum_tasks.json -c test_enum_config_inline.json
```

**Testing Steps:**
1. Press `c` to switch to cell mode
2. Navigate to the `status` or `priority` column
3. Press `e` to cycle to next enum value
4. Press `E` to cycle to previous enum value
5. The cell value should update immediately
6. Colors should cycle dynamically for each unique value
7. Press `ctrl-e` to open popup dialog with all options

**Expected Behavior:**
- Status enum options: todo → in-progress → done → cancelled → todo (wraps)
- Priority enum options: low → medium → high → critical → low (wraps)
- Each unique value gets its own color
- Footer shows "e/E cycle enum | ^E popup" in cell mode

### 2. Inferred Enum Source (Scan Column Values)

Test enum cycling that automatically extracts unique values from the column:

```bash
python dv.py test_enum_comprehensive.json -c test_enum_config_inferred.json
```

**Testing Steps:**
1. Press `c` to switch to cell mode
2. Navigate to the `status` column
3. Press `e` to cycle through all unique status values

**Expected Behavior:**
- Status enum options cycle through: planning → development → bugfix → documentation → review → testing → done → planning (sorted alphabetically)
- Priority enum options: low → medium → high → critical → low (sorted)
- Type enum options: bug → docs → feature → security → testing → bug (sorted)
- All values in each column get color cycling

### 3. External Enum Source (Command-Based)

Test enum cycling that fetches values from an external command:

```bash
python dv.py test_enum_tasks.json -c test_enum_config_external.json
```

**Testing Steps:**
1. Press `c` to switch to cell mode
2. Navigate to the `priority` column
3. Press `e` to cycle through values from the external script

**Expected Behavior:**
- Status enum options: todo → in-progress → done → cancelled → todo (inline source)
- Priority enum options cycle through: low → medium → high → critical → blocker → low (from external script)

### 4. Mixed Enum Sources

Test all three enum source types in a single config:

```bash
python dv.py test_enum_comprehensive.json -c test_enum_config_mixed.json
```

**Testing Steps:**
1. Test `status` column (inline source) - cycles through predefined values
2. Test `priority` column (inferred source) - cycles through extracted values
3. Test `type` column (inferred source) - cycles through extracted values

**Expected Behavior:**
- Status: Uses predefined inline values with color cycling
- Priority: Auto-extracted from data with color cycling
- Type: Auto-extracted from data with color cycling

## Keyboard Shortcuts

### Enum Cycling (Cell Mode Only)
- `e` - Cycle to next enum value in current cell
- `E` - Cycle to previous enum value in current cell
- `ctrl-e` - Open enum picker popup dialog with all options

**Important**: Must be in cell mode (press `c` to toggle)

### Popup Dialog Navigation
- `↑` or `k` - Move up in list
- `↓` or `j` - Move down in list
- `Enter` - Select highlighted value
- `ESC` - Cancel without selecting

### Navigation in dv-tui:
- `c` - Toggle between row and cell mode
- `j`/`↓` - Move down
- `k`/`↑` - Move up
- `h`/`←` - Move left (in cell mode) or previous tab (in row mode)
- `l`/`→` - Move right (in cell mode) or next tab (in row mode)
- `/` - Search
- `q` - Quit

## Color Cycling

- **Enum fields only**: Color cycling applies to any field with enum configuration
- **Dynamic colors**: Each unique enum value gets its own color automatically
- **Consistent**: Same value always has the same color across all rows
- **Custom colors**: Predefined field colors (e.g., "work", "study") take precedence

## Verification Checklist

- [ ] Press `c` to enter cell mode
- [ ] Navigate to a column with enum configuration
- [ ] Footer shows "e/E cycle enum | ^E popup"
- [ ] `e` cycles to next enum value
- [ ] `E` cycles to previous enum value
- [ ] Values wrap correctly (last → first, first → last)
- [ ] `ctrl-e` opens popup dialog
- [ ] Popup shows all enum options
- [ ] Arrow keys navigate in popup
- [ ] Enter selects value in popup
- [ ] ESC cancels popup without changes
- [ ] Each unique enum value has its own color
- [ ] Colors are consistent for the same value
- [ ] Footer shows "e/E cycle enum | ^E popup" in cell mode
- [ ] Inferred source captures all unique column values
- [ ] External source executes command correctly
- [ ] Inline source uses configured values
- [ ] Only works in cell mode (not row mode)

## Troubleshooting

**Enum cycling doesn't work:**
- Verify you're in cell mode (press `c`)
- Check that current column has enum configuration
- Ensure enum config field name matches the column name exactly
- Check footer shows "e/E cycle enum | ^E popup"

**No options shown:**
- For inferred: Check that column has data
- For external: Verify command is executable and returns output
- For inline: Verify values array is properly formatted

**Colors not cycling:**
- Verify field has enum configuration
- Check that enum values are consistent (same value always same color)
- Custom field colors (like "work", "study") override dynamic cycling

**Popup doesn't open (ctrl-e):**
- Some terminals may require different key combinations
- Try: `Ctrl+e`, `Ctrl+E` (shift matters)
- If still not working, use `e`/`E` for cycling instead
- Check `/tmp/dv_keys.txt` for debug output showing which keys are being pressed

**Keys not responding:**
- Check if terminal supports the keys (try in a regular shell first)
- Some terminal emulators intercept certain key combinations
- Verify you're pressing the lowercase `e` for next and uppercase `E` for previous

**Debug key presses:**
- The application logs all key presses to `/tmp/dv_keys.txt`
- Run `tail -f /tmp/dv_keys.txt` in another terminal to see what keys are being detected
- Press `e`/`E`/`Ctrl+e` and check the key codes in the log
- ASCII codes: `e`=101, `E`=69, `Ctrl+e`=5

## Advanced Configuration

### Keybind Customization

You can customize the enum keybinds in your config file:

```json
{
  "keybinds": {
    "cell": {
      "enum_cycle_next": "e",
      "enum_cycle_prev": "E",
      "enum_picker": 5
    }
  }
}
```

Note: 5 is the ASCII code for ctrl-e.

### Multiple Enum Fields

The config supports multiple enum fields with different sources:

```json
{
  "enum": {
    "status": {
      "source": "inline",
      "values": ["todo", "in-progress", "done"]
    },
    "priority": {
      "source": "inferred"
    },
    "type": {
      "source": "external",
      "command": "./get_types.sh"
    }
  }
}
```

Each field can use a different source type!
