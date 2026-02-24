#!/usr/bin/env python3
"""Test key detection without curses to verify terminal behavior."""
import sys
import tty
import termios

def get_key():
    """Read a single key from stdin."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

print("Key Detection Test")
print("Press the following keys and I'll show the detected codes:")
print("1. Ctrl+e (should be code 5)")
print("2. e (should be code 101)")
print("3. E (should be code 69)")
print("4. q to quit")
print("")

while True:
    key = get_key()
    
    # Get the byte value
    key_code = ord(key)
    
    # Check what it is
    if key_code == 5:
        print(f"✓ Ctrl+e detected (code {key_code})")
    elif key_code == 101:
        print(f"✓ e detected (code {key_code})")
    elif key_code == 69:
        print(f"✓ E detected (code {key_code})")
    elif key_code == ord('q'):
        print("Quitting...")
        break
    else:
        print(f"  Key code {key_code} ('{key if key.isprintable() else repr(key)}')")
