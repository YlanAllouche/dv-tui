# Change: Implement Mode-Based Keybind System with Layering

## Why
Provide flexible, mode-aware keybinding with layering support to allow users to customize interactions.

## What Changes
- Define default keybinds for each mode (normal, search, cell)
- Implement `KeybindManager` to handle mode switching and keybind lookup
- Support keybind precedence (CLI > inline JSON > defaults)
- Support unbinding specific keybinds at different layers
- Support nested keybind syntax in config
- Allow CLI flags to add/remove keybinds

## Impact
- Affected specs: None (new capability)
- Affected code: handlers.py, config.py modules
