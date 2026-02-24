import curses
from typing import List, Dict, Any, Callable, Optional, Union
from .utils import sanitize_display_string, Colors


class Table:
    """Table rendering and data management."""
    
    def __init__(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None,
                 enum_config: Optional[Any] = None):
        self.data = data
        
        self.value_color_map = {}
        self.available_color_pairs = [9, 10, 11, 12]
        self.next_color_idx = 0
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.selected_column = 0
        self.selection_mode = 'row'
        
        # Store enum configuration for color cycling
        self.enum_config = enum_config
        self.enum_fields = set()
        if enum_config:
            for attr_name in dir(enum_config):
                if not attr_name.startswith('_'):
                    attr_value = getattr(enum_config, attr_name)
                    if attr_value is not None:
                        self.enum_fields.add(attr_name)
        
        # Detect or use provided columns
        self.columns = self._detect_columns(data, columns)
        
        # Cache column widths for performance (avoid recalc on every render)
        self._cached_column_widths = None
        self._cached_width_for = 0
    
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
    
    def _invalidate_column_cache(self) -> None:
        """Invalidate cached column widths (call when data changes)."""
        self._cached_column_widths = None
        self._cached_width_for = 0
    
    def get_field_color(self, field_name: str, value: Any) -> int:
        """Get color for a specific field using dynamic color cycling."""
        return self.get_dynamic_color(field_name, str(value))
    
    def get_type_color(self, type_val: Any) -> int:
        """Get color for type column (legacy compatibility)."""
        return self.get_dynamic_color("type", str(type_val))
    
    def get_status_color(self, status: str) -> int:
        """Get color for status column (legacy compatibility)."""
        return self.get_dynamic_color("status", str(status))
    
    def get_enum_color(self, field_name: str, value: str) -> int:
        """Get color for enum fields using dynamic color cycling."""
        # Use dynamic color cycling for enum fields
        if field_name in self.enum_fields:
            return self.get_dynamic_color(field_name, str(value))
        
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
        # Use cached widths if available and terminal width hasn't changed
        if self._cached_column_widths is not None and self._cached_width_for == available_width:
            return self._cached_column_widths
        
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
                display_val = sanitize_display_string(str(value))
                max_content_len = max(max_content_len, len(display_val))
            
            max_widths.append(max(max_content_len, min_width))
        
        # Calculate proportional widths
        total_max = sum(max_widths)
        if total_max + total_spacing <= available_width:
            # All columns fit, use max widths
            self._cached_column_widths = max_widths
        else:
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
            
            self._cached_column_widths = widths
        
        self._cached_width_for = available_width
        return self._cached_column_widths
    
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
                display_str = sanitize_display_string(str(value), max_length=col_width - 1).ljust(col_width)
                
                # Use dynamic color cycling for all columns
                color = self.get_dynamic_color(col, str(value))
                
                try:
                    stdscr.addstr(y, x, display_str, color)
                except curses.error:
                    pass
                
                x += col_width + 1
    
    def is_drillable(self, row_index: int, col_index: int) -> bool:
        """Check if a cell contains drillable data (array or object)."""
        if not (0 <= row_index < len(self.data)):
            return False
        if not (0 <= col_index < len(self.columns)):
            return False
        
        value = self.data[row_index].get(self.columns[col_index])
        return isinstance(value, (list, dict))
    
    def render_headers(self, stdscr, y: int, headers: List[str],
                      column_widths: List[int], header_colors: List[int]) -> None:
        """Render column headers."""
        x = 0
        for i, (header, col_width) in enumerate(zip(headers, column_widths)):
            # Cycle through header colors if there are more columns than colors
            color = header_colors[i % len(header_colors)]
            header_str = header.ljust(col_width)
            try:
                stdscr.addstr(y, x, header_str, color)
            except curses.error:
                pass
            x += col_width + 1
