# Keybind System Test Files

This directory contains test files for the new keybind system.

## Files

- `test_data.json` - Sample data for testing (10 items)
- `custom_config.json` - Config file with custom keybinds
- `inline_config.json` - JSON file with inline config (_config field)
- `verify_keybinds.py` - Automated verification tests
- `test_keybinds.sh` - Interactive test script

## Quick Start

### Run Verification Tests
```bash
PYTHONPATH=. python test_keybinds/verify_keybinds.py
```

### Run Interactive Tests
```bash
./test_keybinds/test_keybinds.sh
```

Or test manually:

### 1. Default Keybinds
```bash
dv test_keybinds/test_data.json
```
Keys:
- `j` / `J` / ↓ - move down
- `k` / `K` / ↑ - move up
- `h` / `H` / ← - move left (cell mode)
- `l` / `L` / → - move right (cell mode)
- `/` - enter search mode
- `c` - toggle row/cell mode
- `Enter` - select item
- `q` / `Q` - quit

### 2. Add/Override Keybinds
```bash
# Map 'n' to down movement (replaces all default down keys)
dv --bind 'n:down' test_keybinds/test_data.json

# Remove 'j' from default down keys (J and arrow still work)
dv --unbind 'j' test_keybinds/test_data.json

# Bind multiple keys to same action
dv --bind 'n:down' --bind 'arrow_down:down' test_keybinds/test_data.json

# Combine: bind custom keys and unbind default ones
dv --bind 'n:down' --bind 'p:up' --unbind 'j' test_keybinds/test_data.json
```

### 3. Use Custom Config File
```bash
dv --config test_keybinds/custom_config.json test_keybinds/test_data.json
```
Custom keys in config:
- Leader: `,` (not `;`)
- Search: `f` (not `/`)
- Down: `n` or `j`
- Up: `p` or `k`

### 4. Use Inline Config
```bash
dv test_keybinds/inline_config.json
```
Inline config overrides:
- Search: `s` (not `/`)
- Quit: only `Q` (not `q`)

### 5. Mode-Specific Keybinds
```bash
# Change quit key only in search mode
dv --bind 'search:x:quit' test_keybinds/test_data.json
# Press '/' to enter search, then 'x' to quit

# Change down key only in cell mode
dv --bind 'cell:arrow_down:down' test_keybinds/test_data.json
```

### 6. Test Precedence
CLI > inline config > file config > defaults

```bash
# Config sets search to 'f', CLI overrides to 'x'
dv --config test_keybinds/custom_config.json --bind 'x:search' test_keybinds/test_data.json
# Press 'x' to search (not 'f')
```

## Keybind Syntax

### Add/Override
```bash
--bind 'key:action'           # For normal mode
--bind 'mode:key:action'       # For specific mode
```

Examples:
- `--bind 'n:down'` - map 'n' to down action
- `--bind 'search:x:quit'` - map 'x' to quit in search mode
- `--bind 'cell:a:left'` - map 'a' to left in cell mode

### Unbind
```bash
--unbind 'key'           # For normal mode
--unbind 'mode:key'      # For specific mode
```

Examples:
- `--unbind 'j'` - remove 'j' binding
- `--unbind 'search:q'` - remove 'q' binding in search mode

## Config File Format

```json
{
  "keybinds": {
    "normal": {
      "leader": ",",
      "down": ["n", "j"],
      "up": ["p", "k"],
      "search": "f",
      "quit": ["Q"]
    },
    "search": {
      "enter": [10],
      "escape": "q"
    },
    "cell": {
      "left": ["h"],
      "right": ["l"]
    }
  }
}
```

## Tips

1. **Keys can be single characters, named keys, or integers**:
   - Characters: `'j'`, `'q'`, `'Enter'`
   - Named keys: `'arrow_down'`, `'arrow_up'`, `'escape'`, `'backspace'`, `'tab'`
   - Integers: `258` (curses key codes)

2. **Binding behavior**:
   - `--bind 'n:down'` replaces ALL default keys for the down action
   - To keep default keys and add new ones, bind them all: `--bind 'j:down' --bind 'n:down'`
   - Multiple bindings accumulate: `--bind 'n:down' --bind 'arrow_down:down'` creates `[n, arrow_down]`

3. **Unbinding behavior**:
   - `--unbind 'j'` removes 'j' from the action's key list
   - If all keys are unbound, the action has no keybind
   - Unbinding removes keys at ALL layers (CLI, inline, file, defaults)

4. **Precedence order**: CLI > inline config > file config > defaults

5. **Mode-specific bindings**:
   - `--bind 'search:x:quit'` - only affects search mode
   - `--unbind 'search:q'` - only unbinds 'q' in search mode
