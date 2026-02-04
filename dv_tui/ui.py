import curses
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path


def draw_header(stdscr, y: int, text: str, width: int, color: int = 0) -> None:
    """Draw a header line."""
    header_text = text.ljust(width)[:width]
    try:
        stdscr.addstr(y, 0, header_text, color)
    except curses.error:
        pass


def draw_footer(stdscr, y: int, text: str, width: int) -> None:
    """Draw a footer line with hints."""
    footer_text = text[:width]
    try:
        stdscr.addstr(y, 0, footer_text, curses.A_DIM)
    except curses.error:
        pass


def draw_tabs(stdscr, y: int, tabs: List[Tuple[str, bool]], width: int) -> None:
    """Draw tabs with active tab highlighted."""
    x = 0
    for tab_text, is_active in tabs:
        display_text = tab_text
        if x + len(display_text) > width:
            display_text = display_text[:width - x]
        
        if is_active:
            try:
                stdscr.addstr(y, x, display_text, curses.A_REVERSE)
            except curses.error:
                pass
        else:
            try:
                stdscr.addstr(y, x, display_text)
            except curses.error:
                pass
        
        x += len(display_text)
        if x < width - 3:
            try:
                stdscr.addstr(y, x, " | ")
            except curses.error:
                pass
            x += 3


def draw_dialog(stdscr, title: str, message: str, width: Optional[int] = None, height: Optional[int] = None) -> int:
    """
    Draw a dialog box and wait for user input.
    Returns the key pressed.
    """
    if height is None:
        height, max_width = stdscr.getmaxyx()
        lines = message.split('\n')
        content_height = len(lines) + 2  # +2 for title and padding
        height = min(content_height + 4, height - 2)
    
    if width is None:
        _, max_width = stdscr.getmaxyx()
        title_width = len(title) + 4
        msg_width = max(len(line) for line in message.split('\n')) + 4
        width = min(max(title_width, msg_width), max_width - 4)
    
    screen_h, screen_w = stdscr.getmaxyx()
    start_y = (screen_h - height) // 2
    start_x = (screen_w - width) // 2
    
    window = curses.newwin(height, width, start_y, start_x)
    window.box()
    
    try:
        window.addstr(0, 2, title, curses.A_BOLD)
    except curses.error:
        pass
    
    y = 1
    for line in message.split('\n'):
        if y < height - 2:
            try:
                window.addstr(y, 2, line[:width - 4])
            except curses.error:
                pass
            y += 1
    
    window.refresh()
    
    key = window.getch()
    del window
    stdscr.touchwin()
    stdscr.refresh()
    
    return key


def draw_status_bar(stdscr, y: int, width: int, status_items: List[Tuple[str, int]]) -> None:
    """
    Draw a status bar with multiple colored items.
    
    status_items: list of (text, color_pair) tuples
    """
    x = 0
    for text, color_pair in status_items:
        remaining_width = width - x
        if remaining_width <= 0:
            break
        
        display_text = text[:remaining_width]
        try:
            stdscr.addstr(y, x, display_text, color_pair)
        except curses.error:
            pass
        x += len(display_text)


def init_color_pairs() -> None:
    """Initialize all standard color pairs."""
    curses.start_color()
    curses.use_default_colors()
    
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_BLUE, -1)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(8, curses.COLOR_RED, -1)
    
    curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(14, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_RED)
    
    colors_to_use = [curses.COLOR_RED, curses.COLOR_BLUE, curses.COLOR_YELLOW, curses.COLOR_CYAN]
    for i, color in enumerate(colors_to_use):
        curses.init_pair(9 + i, color, -1)
