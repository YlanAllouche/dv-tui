#!/usr/bin/env python3
"""Minimal test to verify the main loop structure doesn't crash."""
import curses

def test_loop(stdscr):
    """Test the basic loop structure."""
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.timeout(100)
    
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    counter = 0
    
    while True:
        stdscr.clear()
        
        # Display counter
        stdscr.addstr(0, 0, f"Loop iteration: {counter}")
        stdscr.addstr(2, 0, "Press Ctrl+e, e, E, or q to quit")
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == -1:
            continue
        
        if key == ord('q') or key == ord('Q'):
            break
        
        if key == 5:  # Ctrl+e
            stdscr.clear()
            stdscr.addstr(0, 0, "✓ Ctrl+e pressed!", curses.color_pair(1))
            stdscr.refresh()
            counter += 1
        elif key == ord('e'):
            stdscr.clear()
            stdscr.addstr(0, 0, "✓ e pressed!", curses.color_pair(1))
            stdscr.refresh()
            counter += 1
        elif key == ord('E'):
            stdscr.clear()
            stdscr.addstr(0, 0, "✓ E pressed!", curses.color_pair(1))
            stdscr.refresh()
            counter += 1

if __name__ == "__main__":
    print("Starting loop test...")
    curses.wrapper(test_loop)
    print(f"✓ Loop completed! Total iterations: {counter}")
