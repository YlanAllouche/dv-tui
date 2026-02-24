# Change: Implement Refresh System

## Why
Define how data is refreshed after triggers to keep views up-to-date.

## What Changes
- Add refresh configuration (enabled, on_trigger, interval, command)
- Implement refresh logic for file input (reload from disk)
- Implement refresh logic for stdin with -c command (re-run command)
- Implement refresh logic for stdin without command (warning message)
- Add CLI flags: --refresh, --no-refresh, --refresh-interval
- Preserve selection and scroll position after refresh

## Impact
- Affected specs: None (new capability)
- Affected code: data_loaders.py, actions.py modules
