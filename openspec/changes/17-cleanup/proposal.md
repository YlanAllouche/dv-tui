# Change: Clean Up Codebase and Remove Hardcoded Specifics

## Why
Remove hardcoded assumptions and specific integrations to make the tool truly generic and maintainable.

## What Changes
- Remove nvim integration (move to example config)
- Remove play_locator integration (move to example config)
- Remove hardcoded field expectations (type, status, summary)
- Remove hardcoded color mappings (make configurable)
- Remove debug logging (/tmp/dv_keys.txt, /tmp/dv_play.log)
- Improve error messages and handling
- Add type hints throughout
- Improve variable naming for clarity
- Remove unused code and imports

## Impact
- Affected specs: None (new capability)
- Affected code: All modules across the package
