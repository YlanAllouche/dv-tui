#!/usr/bin/env python3
"""
Simple curses-based TUI for JSON files with nvim integration
"""

import json
import os
import subprocess
import curses
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple
import time
import re

# ANSI color codes
class Colors:
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

def beautify_filename(filename: str) -> str:
    """Beautify filename by removing extension, capitalizing, and replacing -/_ with spaces"""
    # Remove extension
    name = Path(filename).stem

    # Replace - and _ with spaces
    name = name.replace('-', ' ').replace('_', ' ')

    # Capitalize first letter of each word
    name = ' '.join(word.capitalize() for word in name.split())

    return name

def fuzzy_match(query: str, text: str) -> Tuple[bool, float]:
    """
    Perform fuzzy matching between query and text.
    Returns (matched, score) where score is lower for better matches.
    
    The algorithm finds all characters of query in text in order,
    and scores based on how compact the match is.
    """
    query = query.lower()
    text = text.lower()
    
    if not query:
        return True, 0.0
    
    # Track position in text
    text_pos = 0
    score = 0.0
    
    for char in query:
        # Find next occurrence of char in text
        found_pos = text.find(char, text_pos)
        if found_pos == -1:
            # Character not found, no match
            return False, float('inf')
        
        # Add distance penalty (characters skipped)
        distance = found_pos - text_pos
        score += distance
        
        # Move position forward
        text_pos = found_pos + 1
    
    return True, score

def fuzzy_filter(items: List[Dict[str, Any]], query: str, search_field: str = "summary") -> List[Dict[str, Any]]:
    """
    Filter items by fuzzy matching on a specific field.
    Returns items sorted by match quality.
    """
    if not query:
        return items
    
    matches = []
    for item in items:
        field_value = str(item.get(search_field, ""))
        matched, score = fuzzy_match(query, field_value)
        if matched:
            matches.append((item, score))
    
    # Sort by score (lower is better) then by original order
    matches.sort(key=lambda x: x[1])
    return [item for item, score in matches]

def sanitize_display_string(text: str, max_length: Union[int, None] = None) -> str:
    """
    Sanitize a string for curses display by:
    1. Replacing newlines and other control characters with spaces
    2. Collapsing multiple spaces into single spaces
    3. Truncating to max_length if specified
    4. Stripping leading/trailing whitespace
    """
    if not text:
        return ""

    # Convert to string if not already
    text = str(text)

    # Replace newlines, tabs, and other control characters with spaces
    # Control characters are in range 0-31 (excluding space which is 32)
    sanitized = ''.join(
        ' ' if ord(c) < 32 else c
        for c in text
    )

    # Collapse multiple spaces into single space
    import re
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    # Truncate if max_length specified
    if max_length is not None and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized

class SimpleInitiativeTUI:
    def __init__(self, json_files: Union[str, List[str]], single_select: bool = False):
        # Support both single file (legacy) and multiple files
        if isinstance(json_files, str):
            json_files = [json_files]
        
        self.json_files = json_files
        self.active_tab = 0  # Index of currently active tab
        self.initiatives: List[Dict[str, Any]] = []
        self.selected_index = 0
        self.single_select = single_select
        self.last_mtime = None
        self.scroll_offset = 0  # Viewport offset for scrolling
        self.last_check_time = 0  # Debounce file checks
        self.check_cooldown = 0.5  # Only check file every 500ms to avoid flickering
        
        # Dynamic value-to-color mapping for fields
        # Uses colors that aren't used elsewhere: RED (1), BLUE (4)
        # YELLOW (3) available too if needed
        self.value_color_map = {}  # maps (field_name, value) -> color_pair_number
        self.available_color_pairs = [9, 10, 11, 12]  # Color pairs reserved for dynamic colors
        self.next_color_idx = 0
        
        # Leader key state for keybindings
        self.leader_pending = False
        self.leader_timeout = 0
        self.LEADER_KEY = ord(';')  # semicolon as leader key (reliable alternative to ctrl+x)
        
        # Search/filter mode state
        self.search_mode = False
        self.search_query = ""
        self.filtered_indices: List[int] = []  # Indices of filtered items in original list
        self.search_selected_index = 0  # Index within filtered results
        self.pre_search_selected_index = 0  # Position before entering search
        self.pre_search_scroll_offset = 0  # Scroll position before entering search
        self.terminal_height = 0  # Will be set during display_list
    
    @property
    def json_file(self) -> str:
        """Get current active JSON file"""
        return self.json_files[self.active_tab]
        
    def load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.json_file, 'r') as f:
                self.initiatives = json.load(f)
            # Update modification time after successful load
            # File descriptors (e.g., /dev/fd/63 from process substitution) may not support stat
            try:
                self.last_mtime = os.stat(self.json_file).st_mtime
            except (OSError, IOError):
                self.last_mtime = None
        except FileNotFoundError:
            raise Exception(f"{self.json_file} not found")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in {self.json_file}")
    
    def check_and_reload_data(self):
        """Check if file has been modified and reload if necessary"""
        current_time = time.time()
        
        # Debounce: only check file every N seconds to avoid flickering
        if current_time - self.last_check_time < self.check_cooldown:
            return False
        
        self.last_check_time = current_time
        
        try:
            current_mtime = os.stat(self.json_file).st_mtime
            if self.last_mtime is not None and current_mtime != self.last_mtime:
                # File has been modified, reload data
                self.load_data()
                # Reset selected index if it's out of bounds
                self.selected_index = min(self.selected_index, len(self.initiatives) - 1)
                return True
        except (FileNotFoundError, OSError):
            pass
        return False
    
    def init_colors(self):
        """Initialize color pairs"""
        curses.start_color()
        curses.use_default_colors()
        
        # Basic color pairs
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
        
        # Dynamic color pairs for value cycling (pairs 9-12)
        colors_to_use = [curses.COLOR_RED, curses.COLOR_BLUE, curses.COLOR_YELLOW, curses.COLOR_CYAN]
        for i, color in enumerate(colors_to_use):
            curses.init_pair(9 + i, color, -1)
        
    def get_dynamic_color(self, field_name: str, value: str):
        """
        Get color pair for a value, cycling through available colors.
        Same unique value always gets the same color across the display.
        """
        key = (field_name, str(value))
        
        if key not in self.value_color_map:
            # Assign next available color
            color_idx = self.next_color_idx % len(self.available_color_pairs)
            self.value_color_map[key] = self.available_color_pairs[color_idx]
            self.next_color_idx += 1
        
        pair_num = self.value_color_map[key]
        return curses.color_pair(pair_num) | curses.A_BOLD
    
    def display_list(self, stdscr):
        """Display items in curses with full line inversion for selection"""
        self.stdscr = stdscr
        stdscr.clear()
        curses.curs_set(0)
        
        height, width = stdscr.getmaxyx()
        self.terminal_height = height  # Store for use in key handling
        
        # Calculate viewport size (available rows for items)
        # 1 for title/tabs, 1 for header, 1 for keybind hints at bottom
        viewport_height = height - 4 if height > 4 else 1
        
        # Update scroll offset to keep selected item visible
        if self.search_mode:
            # In search mode, use search_selected_index
            if self.search_selected_index < self.scroll_offset:
                self.scroll_offset = self.search_selected_index
            elif self.search_selected_index >= self.scroll_offset + viewport_height:
                self.scroll_offset = self.search_selected_index - viewport_height + 1
        else:
            # Normal mode, use selected_index
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
            elif self.selected_index >= self.scroll_offset + viewport_height:
                self.scroll_offset = self.selected_index - viewport_height + 1
        
        # Build tabs line with count and file names
        tabs_parts = []
        for i, json_file in enumerate(self.json_files):
            beautified_name = beautify_filename(Path(json_file).name)
            
            if i == self.active_tab:
                # Current active tab with item count
                if self.search_mode:
                    tab_text = f"{beautified_name} - {len(self.filtered_indices)}/{len(self.initiatives)} items [SEARCH]"
                else:
                    tab_text = f"{beautified_name} - {len(self.initiatives)} items"
            else:
                # Inactive tabs show just the name
                tab_text = beautified_name
            
            tabs_parts.append((tab_text, i == self.active_tab))
        
        # Display tabs on first line
        x = 0
        for tab_text, is_active in tabs_parts:
            if is_active:
                # Active tab with reverse colors
                stdscr.addstr(0, x, tab_text, curses.A_REVERSE)
            else:
                # Inactive tabs normal
                stdscr.addstr(0, x, tab_text)
            
            x += len(tab_text)
            # Add separator between tabs if not the last one
            if x < width:
                stdscr.addstr(0, x, " | ")
                x += 3
        
        # Display search query if in search mode
        if self.search_mode:
            search_display = f"Search: {self.search_query}"
            try:
                stdscr.addstr(1, 0, search_display, curses.A_BOLD | curses.color_pair(3))
            except curses.error:
                pass
            start_y = 2
            # Use filtered indices for display
            display_indices = self.filtered_indices
        else:
            # Detect columns from data dynamically
            all_columns = set()
            for item in self.initiatives:
                all_columns.update(item.keys())
            headers = sorted(all_columns)
            
            # Calculate column widths (distribute evenly)
            num_cols = len(headers)
            if num_cols > 0:
                spacing = 1
                total_spacing = (num_cols - 1) * spacing
                col_widths = []
                available_width = width - total_spacing
                for i, header in enumerate(headers):
                    if i == num_cols - 1:
                        # Last column gets remaining space
                        col_widths.append(max(1, available_width))
                    else:
                        # Distribute evenly
                        col_width = max(8, available_width // num_cols)
                        col_widths.append(col_width)
                        available_width -= col_width
            else:
                col_widths = []
            
            x = 0
            for i, (header, w) in enumerate(zip(headers, col_widths)):
                color = curses.color_pair(13) | curses.A_BOLD
                stdscr.addstr(1, x, header.ljust(w), color)
                x += w + 1
            
            start_y = 2
            # Use all indices for display
            display_indices = list(range(len(self.initiatives)))
        
        # Use calculated column widths
        col_widths = [8, 12, width - 22] if not self.search_mode else []
        
        for display_row in range(viewport_height):
            # Get the index into display_indices
            display_index = self.scroll_offset + display_row
            
            # Stop if we've run out of items
            if display_index >= len(display_indices):
                break
            
            # Get actual index in self.initiatives
            item_index = display_indices[display_index]
            initiative = self.initiatives[item_index]
            y = start_y + display_row
            
            # Get content for each column dynamically
            display_values = []
            for col, col_width in zip(headers, col_widths):
                value = initiative.get(col, "")
                if isinstance(value, int):
                    # Convert duration to minutes
                    minutes = round(value / 60)
                    display_str = f"{minutes}m"
                else:
                    display_str = sanitize_display_string(str(value), max_length=col_width - 1)
                display_values.append(display_str.ljust(col_width))
            
            # Build the full line content
            full_line = " ".join(display_values)
            full_line = full_line.ljust(width - 1)  # Fill to edge
            
            # For selected item, use full line inversion
            # In search mode, check against search_selected_index
            is_selected = False
            if self.search_mode:
                # In search mode, compare display_index with search_selected_index
                is_selected = (display_index == self.search_selected_index)
            else:
                # Normal mode, compare item_index with selected_index
                is_selected = (item_index == self.selected_index)
            
            if is_selected:
                stdscr.addstr(y, 0, full_line, curses.A_REVERSE)
            else:
                # Normal display without hardcoded field-specific colors
                x = 0
                for col, display_str in zip(headers, display_values):
                    # Use dynamic color cycling for all columns
                    value = initiative.get(col, "")
                    color = self.get_dynamic_color(col, str(value))
                    stdscr.addstr(y, x, display_str, color)
                    x += len(display_str) + 1
        
        # Display keybind hints at the bottom
        footer_y = height - 1
        if self.search_mode:
            keybind_hints = "Type to filter | Tab/S-Tab navigate | ESC exit search | Enter select"
        elif len(self.json_files) > 1:
            keybind_hints = "j/↓ down | k/↑ up | h/← prev tab | l/→ next tab | / search | Enter select | q quit"
        else:
            keybind_hints = "j/↓ down | k/↑ up | / search | Enter select | q quit"
        try:
            stdscr.addstr(footer_y, 0, keybind_hints, curses.A_DIM)
        except curses.error:
            pass  # Ignore if we can't write to the last line
        
        stdscr.refresh()
    

    
    def run(self, stdscr):
        """Run the curses TUI"""
        self.load_data()
        
        # Initialize colors
        self.init_colors()
        
        if not self.initiatives:
            stdscr.addstr(0, 0, "0 items")
            stdscr.getch()
            return
        
        # Enable keypad mode for arrow keys
        stdscr.keypad(True)
        # Set non-blocking input with timeout (100ms)
        stdscr.timeout(100)
        

        
        while True:
            # Check if file has been modified and reload if necessary
            self.check_and_reload_data()
            
            self.display_list(stdscr)
            
            key = stdscr.getch()
            

            
            # -1 means no key was pressed (timeout occurred)
            if key == -1:
                # Check if leader key timeout has expired (500ms)
                if self.leader_pending:
                    current_time = time.time()
                    if current_time - self.leader_timeout > 0.5:
                        self.leader_pending = False
                continue
            
            # Handle leader key sequence (semicolon by default)
            if key == self.LEADER_KEY:  # leader key (;)
                self.leader_pending = True
                self.leader_timeout = time.time()
                continue
            
            # If we're waiting for the second key in a leader sequence
            if self.leader_pending:
                self.leader_pending = False
                continue
            
            # Handle search mode keybindings
            if self.search_mode:
                if key == 27:  # ESC key
                    # Restore position from before search
                    self.selected_index = self.pre_search_selected_index
                    self.scroll_offset = self.pre_search_scroll_offset
                    # Exit search mode
                    self.search_mode = False
                    self.search_query = ""
                    self.filtered_indices = []
                    self.search_selected_index = 0
                elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                    # Select the current filtered item and open it
                    if self.filtered_indices:
                        self.selected_index = self.filtered_indices[self.search_selected_index]
                    # Exit search mode
                    self.search_mode = False
                    self.search_query = ""
                    self.filtered_indices = []
                    self.search_selected_index = 0
                    self.scroll_offset = 0
                    # In single-select mode, exit after selection
                    if self.single_select:
                        break
                elif key == curses.KEY_UP or key == 353:  # UP arrow or Shift+Tab (KEY_BTAB)
                    self.search_selected_index = max(0, self.search_selected_index - 1)
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif key == curses.KEY_DOWN or key == 9:  # DOWN arrow or Tab
                    max_index = len(self.filtered_indices) - 1
                    if max_index >= 0:
                        self.search_selected_index = min(max_index, self.search_selected_index + 1)
                        viewport_height = self.terminal_height - 4
                        if self.search_selected_index >= self.scroll_offset + viewport_height:
                            self.scroll_offset = self.search_selected_index - viewport_height + 1
                elif 32 <= key < 127:  # Printable ASCII characters
                    # Add character to search query
                    self.search_query += chr(key)
                    # Refilter on first column
                    search_col = headers[0] if headers else "summary"
                    matched = fuzzy_filter(self.initiatives, self.search_query, search_col)
                    self.filtered_indices = [self.initiatives.index(item) for item in matched]
                    self.search_selected_index = 0
                    self.scroll_offset = 0
                elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
                    if self.search_query:
                        self.search_query = self.search_query[:-1]
                        # Refilter on first column
                        search_col = headers[0] if headers else "summary"
                        matched = fuzzy_filter(self.initiatives, self.search_query, search_col)
                        self.filtered_indices = [self.initiatives.index(item) for item in matched]
                        self.search_selected_index = min(self.search_selected_index, len(self.filtered_indices) - 1) if self.filtered_indices else 0
                        self.scroll_offset = 0
                continue
            
            # Regular keybindings
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('/'):  # Start search mode
                # Save current position before entering search
                self.pre_search_selected_index = self.selected_index
                self.pre_search_scroll_offset = self.scroll_offset
                # Enter search mode
                self.search_mode = True
                self.search_query = ""
                self.filtered_indices = list(range(len(self.initiatives)))
                self.search_selected_index = 0
                self.scroll_offset = 0
            elif key == curses.KEY_UP or key == ord('k') or key == ord('K'):
                self.selected_index = max(0, self.selected_index - 1)
            elif key == curses.KEY_DOWN or key == ord('j') or key == ord('J'):
                self.selected_index = min(len(self.initiatives) - 1, self.selected_index + 1)
            elif key == curses.KEY_LEFT or key == ord('h') or key == ord('H'):
                # Tab navigation: previous tab
                if len(self.json_files) > 1:
                    self.active_tab = max(0, self.active_tab - 1)
                    self.load_data()  # Load data from new tab
                    self.selected_index = 0  # Reset selection
                    self.scroll_offset = 0  # Reset scroll
            elif key == curses.KEY_RIGHT or key == ord('l') or key == ord('L'):
                # Tab navigation: next tab
                if len(self.json_files) > 1:
                    self.active_tab = min(len(self.json_files) - 1, self.active_tab + 1)
                    self.load_data()  # Load data from new tab
                    self.selected_index = 0  # Reset selection
                    self.scroll_offset = 0  # Reset scroll
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # In single-select mode, exit after selection
                if self.single_select:
                    break

if __name__ == "__main__":
    import sys
    
    # Parse arguments
    single_select = False
    json_files = []
    
    # Handle -s flag
    if '-s' in sys.argv:
        single_select = True
        sys.argv.remove('-s')
    
    if len(sys.argv) < 2:
        print("Error: No input file provided", file=sys.stderr)
        print("Usage: dv <file.json>", file=sys.stderr)
        sys.exit(1)
    
    # Accept multiple JSON files as arguments
    json_files = sys.argv[1:]
    
    try:
        tui = SimpleInitiativeTUI(json_files, single_select)
        curses.wrapper(tui.run)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        print(f"Please check the file path and try again.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)