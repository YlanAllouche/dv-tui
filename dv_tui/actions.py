import subprocess
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .table import Table
    from .handlers import KeyHandler
    from .data_loaders import DataLoader


class Clipboard:
    """Clipboard utility with auto-detection of xclip/wl-copy/pbcopy."""
    
    def __init__(self):
        self._available_tool: Optional[str] = None
        self._detect_tool()
    
    def _detect_tool(self) -> None:
        """Detect available clipboard tool."""
        for tool in ["wl-copy", "xclip", "pbcopy"]:
            try:
                subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    check=True,
                    text=True
                )
                self._available_tool = tool
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    
    def copy(self, text: str) -> bool:
        """
        Copy text to system clipboard.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._available_tool:
            return False
        
        try:
            if self._available_tool == "wl-copy":
                subprocess.run(
                    ["wl-copy"],
                    input=text.encode(),
                    check=True
                )
            elif self._available_tool == "xclip":
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode(),
                    check=True
                )
            elif self._available_tool == "pbcopy":
                subprocess.run(
                    ["pbcopy"],
                    input=text.encode(),
                    check=True
                )
            return True
        except Exception:
            return False
    
    def get_tool_name(self) -> str:
        """Get the name of the detected clipboard tool."""
        return self._available_tool if self._available_tool else "none"


_global_clipboard = Clipboard()


def scroll_up(table: "Table") -> None:
    """Scroll up one row."""
    table.scroll_up()


def scroll_down(table: "Table") -> None:
    """Scroll down one row."""
    table.scroll_down()


def select_row(table: "Table", row_index: int) -> None:
    """Select a specific row."""
    table.selected_index = max(0, min(len(table.data) - 1, row_index))


def select_cell(table: "Table", row_index: int, column_index: int) -> None:
    """Select a specific cell."""
    select_row(table, row_index)
    table.selected_column = max(0, min(len(table.columns) - 1, column_index))


def toggle_selection_mode(table: "Table") -> None:
    """Toggle between row and cell selection mode."""
    if table.selection_mode == 'row':
        table.selection_mode = 'cell'
        table.selected_column = 0
    else:
        table.selection_mode = 'row'


def enter_search(key_handler: "KeyHandler", table: "Table") -> None:
    """Enter search mode."""
    key_handler.enter_search_mode(table)


def exit_search(key_handler: "KeyHandler", table: "Table") -> None:
    """Exit search mode."""
    key_handler.exit_search_mode(table)


def search_navigate(key_handler: "KeyHandler", direction: str = "down") -> None:
    """Navigate through search results."""
    if direction == "up":
        key_handler.search_selected_index = max(0, key_handler.search_selected_index - 1)
    elif direction == "down":
        max_index = len(key_handler.filtered_indices) - 1
        if max_index >= 0:
            key_handler.search_selected_index = min(max_index, key_handler.search_selected_index + 1)


def yank_cell(table: "Table") -> bool:
    """
    Yank (copy) the value of the selected cell to clipboard.
    
    Returns:
        True if successful, False otherwise
    """
    if table.selection_mode == 'cell':
        cell_value = table.data[table.selected_index].get(table.columns[table.selected_column])
    else:
        cell_value = str(table.selected_item)
    
    return _global_clipboard.copy(str(cell_value) if cell_value is not None else "")


def show_message(stdscr: Any, message: str, timeout: float = 2.0) -> None:
    """
    Show a temporary message popup.
    
    Args:
        stdscr: Curses window object
        message: Message to display
        timeout: Time to display message in seconds
    """
    try:
        height, width = stdscr.getmaxyx()
        
        lines = message.split('\n')
        max_line_len = max(len(line) for line in lines)
        
        popup_height = len(lines) + 2
        popup_width = max_line_len + 4
        
        y = (height - popup_height) // 2
        x = (width - popup_width) // 2
        
        import curses
        import time
        
        try:
            stdscr.addstr(y, x, " " * popup_width, curses.A_REVERSE)
            for i, line in enumerate(lines):
                padded_line = line.center(popup_width - 2)
                stdscr.addstr(y + i + 1, x + 1, padded_line, curses.A_REVERSE)
            stdscr.addstr(y + len(lines) + 1, x, " " * popup_width, curses.A_REVERSE)
            stdscr.refresh()
            time.sleep(timeout)
        except curses.error:
            pass
    except Exception:
        pass


def refresh_data(loader: "DataLoader") -> List[Dict[str, Any]]:
    """
    Refresh data from data source.
    
    Args:
        loader: DataLoader instance
        
    Returns:
        Refreshed data
        
    Raises:
        Exception: If refresh is not supported
    """
    if loader.can_refresh():
        return loader.refresh()
    else:
        raise Exception("Refresh not supported for this data source")


def quit_tui() -> bool:
    """
    Quit the TUI.
    
    Returns:
        Always returns True to signal exit
    """
    return True


def select_item(item: Dict[str, Any], single_select: bool = False) -> bool:
    """
    Generic select action (no-op for generic data).
    Returns False to indicate no exit.
    
    Note: This function previously had nvim-specific behavior that has been removed.
    Custom nvim integration can be implemented using custom handlers.
    """
    return False


def play_locator(item: Dict[str, Any]) -> None:
    """Run jelly_play_yt on the content of the 'locator' field."""
    locator = item.get("locator", "")
    if not locator:
        return
    
    with open('/tmp/dv_play.log', 'a') as f:
        f.write(f"play_locator called. Locator: '{locator}'\n")
    
    cmd = [str(Path.home() / ".local" / "bin" / "jelly_play_yt"), str(locator)]
    with open('/tmp/dv_play.log', 'a') as f:
        f.write(f"  -> Running: {' '.join(cmd)}\n")
    
    try:
        subprocess.Popen(cmd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       start_new_session=True, close_fds=True)
        with open('/tmp/dv_play.log', 'a') as f:
            f.write(f"  -> Process spawned\n")
    except Exception as e:
        with open('/tmp/dv_play.log', 'a') as f:
            f.write(f"  -> Error: {e}\n")


def copy_to_clipboard(text: str) -> None:
    """Copy text to system clipboard."""
    _global_clipboard.copy(text)


def execute_command(cmd: List[str], async_exec: bool = True) -> None:
    """Execute a shell command."""
    try:
        if async_exec:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           start_new_session=True, close_fds=True)
        else:
            subprocess.run(cmd)
    except Exception:
        pass
