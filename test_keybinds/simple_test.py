#!/usr/bin/env python3
"""Simple test to isolate the unbind issue."""

from dv_tui.handlers import KeyHandler
from dv_tui.config import load_config

print("Creating config with unbind...")
config = load_config(cli_config={'unbinds': [{'key': 'j', 'mode': 'normal'}]})
print(f"Config unbinds: {config.unbinds}")

print("\nCreating KeyHandler...")
kh = KeyHandler(config)
print(f"KM unbinds: {kh.keybind_manager.unbinds}")

print("\nGetting down keybind directly (call 1)...")
down1 = kh.keybind_manager.get_keybind('down')
print(f"Down keybind (direct call 1): {down1}")

print("\nGetting down keybind directly (call 2)...")
down2 = kh.keybind_manager.get_keybind('down')
print(f"Down keybind (direct call 2): {down2}")

print("\nCalling is_down_key(ord('j'))...")
result = kh.is_down_key(ord('j'))
print(f"is_down_key(ord('j')): {result}")

print("\nGetting down keybind directly (call 3)...")
down3 = kh.keybind_manager.get_keybind('down')
print(f"Down keybind (direct call 3): {down3}")

print("\nKM mode:", kh.keybind_manager.get_mode())
print("KM mode value:", kh.keybind_manager.get_mode().value)
print("KM unbinds['normal']:", kh.keybind_manager.unbinds['normal'])
