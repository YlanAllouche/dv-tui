import curses
from typing import List, Dict, Any, Callable, Optional, Union
from .utils import sanitize_display_string, Colors


class Table:
    """Table rendering and data management."""
    
    def __init__(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None):
        self.data = data
        
        self.value_color_map = {}
        self.available_color_pairs = [9, 10, 11, 12]
        self.next_color_idx = 0
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.selected_column = 0
        self.selection_mode = 'row'
        
        # Column-specific color configurations
        self.field_colors = {
            "work": (5, True),
            "study": (6, True),
        }
        
        self.field_status_colors = {
            "focus": (2, True),
            "active": (3, True),
        }
        
        # Detect or use provided columns
        self.columns = self._detect_columns(data, columns)
    
    def _detect_columns(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> List[str]:
        """Detect columns from data or use provided column list for filtering/reordering."""
        all_columns = set()
        for item in data:
            all_columns.update(item.keys())
        
        detected = sorted(all_columns)
        
        if columns is None:
            return detected
        else:
            # Filter: only include columns that exist in the data
            filtered = [col for col in columns if col in detected]
            # If filter removes all columns, fall back to detected columns
            return filtered if filtered else detected
    
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
    
    def get_field_color(self, field_name: str, value: Any) -> int:
        """Get color for a specific field based on configured rules."""
        if isinstance(value, int):
            return curses.color_pair(1)
        
        val_lower = str(value).lower()
        key = (field_name, val_lower)
        
        if key in self.field_colors:
            pair_num, bold = self.field_colors[key]
            return curses.color_pair(pair_num) | (curses.A_BOLD if bold else 0)
        
        if field_name == "status" and val_lower in self.field_status_colors:
            pair_num, bold = self.field_status_colors[val_lower]
            return curses.color_pair(pair_num) | (curses.A_BOLD if bold else 0)
        
        if field_name == "status" and "2025-" in str(value):
            return curses.color_pair(4)
        
        return curses.color_pair(1)
    
    def get_type_color(self, type_val: Any) -> int:
        """Get color for type column (legacy compatibility)."""
        return self.get_field_color("type", type_val)
    
    def get_status_color(self, status: str) -> int:
        """Get color for status column (legacy compatibility)."""
        status_lower = str(status).lower()
        
        if status_lower in self.field_status_colors:
            pair_num, bold = self.field_status_colors[status_lower]
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
    
    def calculate_column_widths(self, headers: List[str], available_width: int) -> List[int]:
        """Calculate column widths based on content and available space."""
        num_cols = len(self.columns)
        if num_cols == 0:
            return []
        
        # Minimum width per column (for small displays)
        min_width = 8
        spacing = 1  # Space between columns
        total_spacing = (num_cols - 1) * spacing
        
        # Calculate maximum needed width for each column
        max_widths = []
        for col in self.columns:
            header_len = len(col)
            max_content_len = header_len
            
            for item in self.data:
                value = item.get(col, "")
                if isinstance(value, int) and col == "type":
                    # Duration in seconds, convert to minutes display
                    display_val = f"{round(value / 60)}m"
                else:
                    display_val = sanitize_display_string(str(value))
                
                max_content_len = max(max_content_len, len(display_val))
            
            max_widths.append(max(max_content_len, min_width))
        
        # Calculate proportional widths
        total_max = sum(max_widths)
        if total_max + total_spacing <= available_width:
            # All columns fit, use max widths
            return max_widths
        
        # Distribute available space proportionally
        widths = []
        remaining_width = available_width - total_spacing
        
        for i, max_w in enumerate(max_widths):
            if i == num_cols - 1:
                # Last column gets remaining space
                widths.append(max(remaining_width, min_width))
            else:
                prop_width = int((max_w / total_max) * remaining_width)
                widths.append(max(prop_width, min_width))
                remaining_width -= widths[i]
        
        return widths
    
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
                
                if isinstance(value, int) and col == "type":
                    minutes = round(value / 60)
                    display_str = f"{minutes}m".ljust(col_width)
                else:
                    display_str = sanitize_display_string(str(value), max_length=col_width - 1).ljust(col_width)
                
                color = curses.A_NORMAL
                if col == "type":
                    color = self.get_field_color(col, value)
                elif col == "status":
                    status_color = self.get_status_color(value)
                    if status_color == curses.A_NORMAL:
                        color = self.get_dynamic_color(col, str(value))
                    else:
                        color = status_color
                
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
