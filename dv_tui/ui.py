import curses
import os
import subprocess
from typing import List, Dict, Any, Tuple, Optional, Callable
from pathlib import Path


class EnumChoiceDialog:
    """Popup dialog for selecting from enum values."""
    
    def __init__(self, stdscr, options: List[str], title: str = "Select Value"):
        """
        Initialize enum choice dialog.
        
        Args:
            stdscr: Main curses window
            options: List of enum options to display
            title: Dialog title
        """
        self.stdscr = stdscr
        self.options = options
        self.title = title
        self.selected_index = 0
        self.window = None
        self.selected_value = None
    
    def show(self) -> Optional[str]:
        """
        Show the enum choice dialog and wait for user selection.
        
        Returns:
            Selected value or None if cancelled
        """
        if not self.options:
            return None
        
        screen_h, screen_w = self.stdscr.getmaxyx()
        
        # Calculate dialog dimensions
        max_option_len = max(len(opt) for opt in self.options)
        width = min(max_option_len + 4, screen_w - 4)
        height = min(len(self.options) + 4, screen_h - 4)
        
        # Create window centered on screen
        start_y = (screen_h - height) // 2
        start_x = (screen_w - width) // 2
        
        self.window = curses.newwin(height, width, start_y, start_x)
        self.window.keypad(True)
        
        # Main input loop
        while True:
            self._render()
            key = self.window.getch()
            
            if key == curses.KEY_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif key == curses.KEY_DOWN:
                self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
            elif key in (curses.KEY_ENTER, ord('\n'), 10):
                self.selected_value = self.options[self.selected_index]
                break
            elif key == 27:  # ESC
                self.selected_value = None
                break
        
        # Clean up
        if self.window:
            del self.window
        self.stdscr.touchwin()
        self.stdscr.refresh()
        
        return self.selected_value
    
    def _render(self) -> None:
        """Render the dialog."""
        if not self.window:
            return
        
        self.window.clear()
        self.window.box()
        
        # Draw title
        try:
            self.window.addstr(0, 2, self.title, curses.A_BOLD)
        except curses.error:
            pass
        
        # Calculate viewport
        viewport_height = self.window.getmaxyx()[0] - 4
        start_row = max(0, min(self.selected_index - viewport_height // 2, 
                                len(self.options) - viewport_height))
        
        # Draw options
        for i in range(min(viewport_height, len(self.options) - start_row)):
            option_index = start_row + i
            option = self.options[option_index]
            y = i + 2
            
            try:
                if option_index == self.selected_index:
                    self.window.addstr(y, 2, f"> {option}", curses.A_REVERSE)
                else:
                    self.window.addstr(y, 2, f"  {option}")
            except curses.error:
                pass
        
        # Draw hints
        hint = "↑↓ navigate | Enter select | ESC cancel"
        hint_y = self.window.getmaxyx()[0] - 2
        try:
            self.window.addstr(hint_y, 2, hint[:self.window.getmaxyx()[1] - 4])
        except curses.error:
            pass
        
        self.window.refresh()


def get_enum_options(enum_config: Any, field_name: str, data: List[Dict[str, Any]], 
                    context: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Get enum options based on configuration.
    
    Args:
        enum_config: EnumSourceConfig object with source type and values
        field_name: Name of the field to get enum options for
        data: Table data (for inferred source)
        context: Context for external command execution
    
    Returns:
        List of enum option strings
    """
    if not enum_config:
        return []
    
    source = getattr(enum_config, 'source', 'inferred')
    
    if source == 'inline':
        values = getattr(enum_config, 'values', None)
        if values and isinstance(values, list):
            return [str(v) for v in values]
        return []
    
    elif source == 'inferred':
        if not data:
            return []
        
        unique_values = set()
        for item in data:
            if field_name in item:
                value = item[field_name]
                unique_values.add(str(value))
        
        return sorted(list(unique_values))
    
    elif source == 'external':
        command = getattr(enum_config, 'command', None)
        if not command:
            return []
        
        try:
            # Build environment with context variables
            env = None
            if context:
                env = os.environ.copy()
                for key, value in context.items():
                    env[f"DV_{key}"] = str(value)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode == 0:
                options = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return options
        except Exception:
            pass
        
        return []
    
    return []


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
    # Calculate total width needed for all tabs including separators
    separator = " | "
    total_width = sum(len(tab_text) for tab_text, _ in tabs)
    total_width += len(separator) * (len(tabs) - 1) if len(tabs) > 1 else 0
    
    # Use full tab names if they all fit
    use_full_names = total_width <= width
    
    x = 0
    for i, (tab_text, is_active) in enumerate(tabs):
        display_text = tab_text
        
        # Only truncate if necessary and not using full names
        if not use_full_names and x + len(display_text) > width:
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
        
        # Add separator if not last tab and there's room
        if i < len(tabs) - 1:
            if use_full_names or x + len(separator) <= width:
                try:
                    stdscr.addstr(y, x, separator)
                except curses.error:
                    pass
                x += len(separator)


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
        try:
            curses.init_pair(9 + i, color, -1)
        except curses.error:
            pass
