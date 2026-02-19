#!/usr/bin/env python3
"""Minimal test to verify enum key detection works in curses."""
import curses
import time

def test_curses_keys(stdscr):
    """Test if enum keys are detected by curses."""
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.timeout(100)
    
    # Start curses colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    while True:
        stdscr.clear()
        
        # Instructions
        instructions = [
            "Curses Key Detection Test",
            "",
            "Press these keys to test detection:",
            "1. Ctrl+e (should show: Ctrl+e pressed!)",
            "2. e (should show: e pressed!)",
            "3. E (should show: E pressed!)",
            "4. j or k (should show navigation)",
            "5. q to quit",
        ]
        
        for i, line in enumerate(instructions):
            try:
                stdscr.addstr(i, 0, line)
            except curses.error:
                pass
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == -1:
            # Timeout
            continue
        elif key == ord('q') or key == ord('Q'):
            break
        elif key == 5:  # Ctrl+e
            stdscr.clear()
            stdscr.addstr(0, 0, "✓ Ctrl+e pressed! (key code: 5)", curses.color_pair(1))
            stdscr.refresh()
            time.sleep(1)
        elif key == ord('e'):
            stdscr.clear()
            stdscr.addstr(0, 0, "✓ e pressed! (key code: 101)", curses.color_pair(1))
            stdscr.refresh()
            time.sleep(1)
        elif key == ord('E'):
            stdscr.clear()
            stdscr.addstr(0, 0, "✓ E pressed! (key code: 69)", curses.color_pair(1))
            stdscr.refresh()
            time.sleep(1)
        elif key in [ord('j'), ord('k'), curses.KEY_DOWN, curses.KEY_UP]:
            stdscr.clear()
            stdscr.addstr(0, 0, f"✓ Navigation key pressed! (key code: {key})", curses.color_pair(1))
            stdscr.refresh()
            time.sleep(1)
        else:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Unknown key: {key} ({chr(key) if 32 <= key < 127 else 'non-printable'})")
            stdscr.refresh()
            time.sleep(1)

if __name__ == "__main__":
    curses.wrapper(test_curses_keys)
