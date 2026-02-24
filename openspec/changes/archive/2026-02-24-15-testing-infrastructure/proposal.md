# Change: Implement Testing Infrastructure

## Why
Provide unit tests for core logic and E2E scenarios to ensure code quality and prevent regressions.

## What Changes
- Set up test framework (pytest)
- Create tests/ directory structure
- Implement unit tests for config loading, data loaders, fuzzy match, triggers, clipboard
- Mock curses for TUI testing
- Create test scenarios for key features

## Impact
- Affected specs: None (new capability)
- Affected code: tests/ directory
