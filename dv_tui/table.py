import curses
from typing import List, Dict, Any, Callable
from .utils import sanitize_display_string, Colors


class Table:
    """Table rendering and data management."""
    
    def __init__(self, data: List[Dict[str, Any]], columns: List[str]):
        self.data = data
        self.columns = columns
        self.selected_index = 0
        self.scroll_offset = 0
        
        self.value_color_map = {}
        self.available_color_pairs = [9, 10, 11, 12]
        self.next_color_idx = 0
        
        self.type_colors = {
            "work": (5, True),
            "study": (6, True),
        }
        
        self.status_colors = {
            "focus": (2, True),
            "active": (3, True),
        }
    
    @property
    def row_count(self) -> int:
        """Get the number of rows in the table."""
        return len(self.data)
    
    @property
    def selected_item(self) -> Dict[str, Any]:
        """Get the currently selected item."""
        if 0 <= self.selected_index < len(self.data):
            return self.data[self.selected_index]
        return {}
    
    def scroll_down(self) -> None:
        """Scroll down one row."""
        self.selected_index = min(len(self.data) - 1, self.selected_index + 1)
    
    def scroll_up(self) -> None:
        """Scroll up one row."""
        self.selected_index = max(0, self.selected_index - 1)
    
    def get_type_color(self, type_val: Any) -> int:
        """Get color for type column."""
        if isinstance(type_val, int):
            return curses.color_pair(1)
        
        type_lower = str(type_val).lower()
        if type_lower in self.type_colors:
            pair_num, bold = self.type_colors[type_lower]
            return curses.color_pair(pair_num) | (curses.A_BOLD if bold else 0)
        return curses.color_pair(1)
    
    def get_status_color(self, status: str) -> int:
        """Get color for status column."""
        status_lower = str(status).lower()
        
        if status_lower in self.status_colors:
            pair_num, bold = self.status_colors[status_lower]
            return curses.color_pair(pair_num) | (curses.A_BOLD if bold else 0)
        
        if "2025-" in str(status):
            return curses.color_pair(4)
        
        return curses.A_NORMAL
    
    def get_dynamic_color(self, field_name: str, value: str) -> int:
        """Get dynamic color cycling for unknown values."""
        key = (field_name, str(value))
        
        if key not in self.value_color_map:
            color_idx = self.next_color_idx % len(self.available_color_pairs)
            self.value_color_map[key] = self.available_color_pairs[color_idx]
            self.next_color_idx += 1
        
        pair_num = self.value_color_map[key]
        return curses.color_pair(pair_num) | curses.A_BOLD
    
    def render(self, stdscr, start_y: int, height: int, width: int, 
               headers: List[str], column_widths: List[int]) -> None:
        """
        Render the table to the curses window.
        
        Args:
            stdscr: Curses window
            start_y: Starting Y position
            height: Available height for rows
            width: Available width
            headers: Column headers
            column_widths: Column widths
        """
        viewport_height = height
        
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + viewport_height:
            self.scroll_offset = self.selected_index - viewport_height + 1
        
        for display_row in range(viewport_height):
            item_index = self.scroll_offset + display_row
            
            if item_index >= len(self.data):
                break
            
            item = self.data[item_index]
            y = start_y + display_row
            
            x = 0
            for i, (col, col_width) in enumerate(zip(self.columns, column_widths)):
                value = item.get(col, "")
                
                if col == "type" and isinstance(value, int):
                    minutes = round(value / 60)
                    display_str = f"{minutes}m".ljust(col_width)
                else:
                    display_str = sanitize_display_string(str(value), max_length=col_width - 1).ljust(col_width)
                
                color = curses.A_NORMAL
                if col == "type":
                    color = self.get_type_color(value)
                elif col == "status":
                    color = self.get_status_color(value)
                    if color == curses.A_NORMAL:
                        color = self.get_dynamic_color("status", str(value))
                
                try:
                    stdscr.addstr(y, x, display_str, color)
                except curses.error:
                    pass
                
                x += col_width + 1
    
    def render_headers(self, stdscr, y: int, headers: List[str], 
                      column_widths: List[int], header_colors: List[int]) -> None:
        """Render column headers."""
        x = 0
        for header, col_width, color in zip(headers, column_widths, header_colors):
            header_str = header.ljust(col_width)
            try:
                stdscr.addstr(y, x, header_str, color)
            except curses.error:
                pass
            x += col_width + 1
