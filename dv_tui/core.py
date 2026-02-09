import curses
import json
import os
import sys
import tempfile
import time
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field

from .table import Table
from .handlers import KeyHandler, Mode
from .config import Config, load_config, load_config_from_inline_json, get_column_widths
from .data_loaders import (
    load_file, get_file_mtime,
    DataLoader, JsonDataLoader, CsvDataLoader, StdinDataLoader,
    create_loader, detect_source
)
from .ui import init_color_pairs, draw_tabs, draw_footer
from .actions import select_item, play_locator
from .utils import beautify_filename


@dataclass
class Tab:
    """Tab state management with data, selection, and scroll state."""
    
    name: str
    source: str
    data: List[Dict[str, Any]] = field(default_factory=list)
    table: Optional[Table] = None
    selected_index: int = 0
    scroll_offset: int = 0
    selection_mode: str = 'row'
    selected_column: int = 0
    last_mtime: Optional[float] = None
    config: Optional[Config] = None


class TUI:
    """TUI engine with curses wrapper."""
    
    def __init__(self, files: List[str], single_select: bool = False, config: Optional[Config] = None, 
                 config_path: Optional[str] = None, delimiter: str = ',', tab_field: str = '_config.tabs'):
        self.files = files
        self.active_tab = 0
        self.single_select = single_select
        self.delimiter = delimiter
        self.tab_field = tab_field
        self.tab_name = config.tab_name if config else None
        self.selected_output = None
        
        self.tabs: List[Tab] = []
        self.last_check_time = 0
        self.check_cooldown = 0.5
        
        self.key_handler: Optional[KeyHandler] = None
        self.loaders: List[DataLoader] = []
        
        if config is None:
            self.config = load_config(config_path=config_path)
        else:
            self.config = config
        
        self.terminal_height = 0
        self.stdscr = None
        self.output_file = None
        
        self.debug_file = open('/tmp/dv_keys.txt', 'a')
        self.debug_file.write("=== Session Start ===\n")
        self.debug_file.flush()
    
    @property
    def current_tab(self) -> Tab:
        """Get the current active tab."""
        if 0 <= self.active_tab < len(self.tabs):
            return self.tabs[self.active_tab]
        return self.tabs[0] if self.tabs else None
    
    @property
    def table(self) -> Optional[Table]:
        """Get the current tab's table."""
        return self.current_tab.table if self.current_tab else None
    
    @property
    def current_file(self) -> str:
        """Get the current active file."""
        return self.files[self.active_tab]
    
    def _init_loaders(self) -> None:
        """Initialize data loaders and tabs for all files."""
        stdin_timeout = self.config.stdin_timeout
        for i, file_path in enumerate(self.files):
            try:
                loader = create_loader(file_path, stdin_timeout=stdin_timeout, delimiter=self.delimiter)
                self.loaders.append(loader)
                
                # Create tab name
                if self.tab_name and i == 0:
                    tab_name = self.tab_name
                else:
                    tab_name = beautify_filename(Path(file_path).name)
                
                tab = Tab(name=tab_name, source=file_path, config=self.config)
                self.tabs.append(tab)
            except Exception as e:
                raise Exception(f"Failed to create loader for {file_path}: {e}")
    
    def load_data(self) -> None:
        """Load data for all tabs and apply inline config if present."""
        if not self.loaders:
            self._init_loaders()
        
        if self.active_tab >= len(self.tabs):
            return
        
        tab = self.tabs[self.active_tab]
        loader = self.loaders[self.active_tab]
        
        tab.data = loader.load()
        
        inline_config = load_config_from_inline_json(tab.data)
        if inline_config:
            tab_config = load_config(
                config_path=self.config.config_file,
                inline_config=inline_config,
                cli_config={},
            )
            tab.config = tab_config
        else:
            tab.config = self.config
        
        tab.last_mtime = get_file_mtime(self.current_file)
        
        # Use configured columns if set, otherwise auto-detect from data
        columns = tab.config.columns if tab.config else self.config.columns
        tab.table = Table(tab.data, columns)
        tab.table.selected_index = tab.selected_index
        tab.table.scroll_offset = tab.scroll_offset
        tab.table.selection_mode = tab.selection_mode
        tab.table.selected_column = tab.selected_column
    
    def check_and_reload(self) -> bool:
        """Check if file has been modified and reload if necessary."""
        current_time = time.time()
        
        if current_time - self.last_check_time < self.check_cooldown:
            return False
        
        self.last_check_time = current_time
        
        if not self.current_tab:
            return False
        
        current_mtime = get_file_mtime(self.current_file)
        if self.current_tab.last_mtime is not None and current_mtime != self.current_tab.last_mtime:
            self.load_data()
            return True
        return False
    
    def init_curses(self, stdscr) -> None:
        """Initialize curses settings."""
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.timeout(100)
        init_color_pairs()
        
        self.key_handler = KeyHandler(self.config)
        self._setup_custom_handlers()
    
    def cleanup_curses(self) -> None:
        """Cleanup curses and restore terminal."""
        if self.stdscr:
            try:
                self.stdscr.keypad(False)
                curses.echo()
                curses.nocbreak()
                curses.endwin()
            except curses.error:
                pass
    
    def _setup_custom_handlers(self) -> None:
        """Setup custom key handlers."""
        def ctrl_p_handler(key):
            if key == 16:
                if 0 <= self.table.selected_index < len(self.data):
                    play_locator(self.data[self.table.selected_index])
            return None
        
        def leader_p_handler(key):
            if self.key_handler.leader_pending and (key == ord('p') or key == ord('P')):
                if 0 <= self.table.selected_index < len(self.data):
                    play_locator(self.data[self.table.selected_index])
            return None
        
        self.key_handler.register_handler(16, ctrl_p_handler)
        self.key_handler.register_handler(ord('p'), leader_p_handler)
        self.key_handler.register_handler(ord('P'), leader_p_handler)
    
    def tab_left(self) -> None:
        """Navigate to previous tab."""
        if len(self.tabs) > 1:
            # Save current tab state
            if self.current_tab and self.table:
                self.current_tab.selected_index = self.table.selected_index
                self.current_tab.scroll_offset = self.table.scroll_offset
                self.current_tab.selection_mode = self.table.selection_mode
                self.current_tab.selected_column = self.table.selected_column
            
            self.active_tab = max(0, self.active_tab - 1)
            self.load_data()
    
    def tab_right(self) -> None:
        """Navigate to next tab."""
        if len(self.tabs) > 1:
            # Save current tab state
            if self.current_tab and self.table:
                self.current_tab.selected_index = self.table.selected_index
                self.current_tab.scroll_offset = self.table.scroll_offset
                self.current_tab.selection_mode = self.table.selection_mode
                self.current_tab.selected_column = self.table.selected_column
            
            self.active_tab = min(len(self.tabs) - 1, self.active_tab + 1)
            self.load_data()
    
    def create_tab_from_data(self, name: str, data: List[Dict[str, Any]]) -> None:
        """
        Create a new tab from the provided data.
        
        Args:
            name: Name for the new tab
            data: Data to display in the new tab
        """
        tab = Tab(name=name, source="inline", data=data, config=self.config)
        
        # Use configured columns if set, otherwise auto-detect from data
        columns = self.config.columns
        tab.table = Table(tab.data, columns)
        
        self.tabs.append(tab)
        self.loaders.append(None)  # No loader for inline data
        
        # Save current tab state
        if self.current_tab and self.table:
            self.current_tab.selected_index = self.table.selected_index
            self.current_tab.scroll_offset = self.table.scroll_offset
            self.current_tab.selection_mode = self.table.selection_mode
            self.current_tab.selected_column = self.table.selected_column
        
        # Switch to the new tab
        self.active_tab = len(self.tabs) - 1
    
    def render(self) -> None:
        """Render the TUI."""
        self.stdscr.clear()
        
        height, width = self.stdscr.getmaxyx()
        self.terminal_height = height
        
        viewport_height = height - 4
        start_y = 2
        
        if not self.table:
            return
        
        columns = self.table.columns
        headers = [c.capitalize() for c in columns]
        column_widths = self.table.calculate_column_widths(headers, width)
        
        tabs = []
        for i, tab in enumerate(self.tabs):
            display_name = tab.name
            
            if i == self.active_tab:
                if self.key_handler.mode == Mode.SEARCH:
                    tab_text = f"{display_name} - {len(self.key_handler.filtered_indices)}/{len(tab.data)} items [SEARCH]"
                else:
                    tab_text = f"{display_name} - {len(tab.data)} items"
            else:
                tab_text = display_name
            tabs.append((tab_text, i == self.active_tab))
        
        draw_tabs(self.stdscr, 0, tabs, width)
        
        if self.key_handler.mode == Mode.SEARCH:
            search_display = f"Search: {self.key_handler.search_query}"
            try:
                self.stdscr.addstr(1, 0, search_display, curses.A_BOLD | curses.color_pair(3))
            except curses.error:
                pass
        else:
            header_colors = [
                curses.color_pair(13) | curses.A_BOLD,
                curses.color_pair(14) | curses.A_BOLD,
                curses.color_pair(15) | curses.A_BOLD,
            ]
            self.table.render_headers(self.stdscr, 1, headers, column_widths, header_colors)
        
        display_indices = self.key_handler.filtered_indices if self.key_handler.mode == Mode.SEARCH else list(range(len(self.current_tab.data)))
        
        self._render_rows(start_y, viewport_height, width, display_indices, column_widths)
        
        self._render_footer(height, width)
        
        self.stdscr.refresh()
    
    def _render_rows(self, start_y: int, viewport_height: int, width: int, 
                     display_indices: List[int], column_widths: List[int]) -> None:
        """Render data rows."""
        if not self.current_tab:
            return
            
        for display_row in range(viewport_height):
            display_index = self.table.scroll_offset + display_row
            
            if display_index >= len(display_indices):
                break
            
            item_index = display_indices[display_index]
            item = self.current_tab.data[item_index]
            y = start_y + display_row
            
            is_selected = False
            if self.key_handler.mode == Mode.SEARCH:
                is_selected = (display_index == self.key_handler.search_selected_index)
            else:
                is_selected = (item_index == self.table.selected_index)
            
            x = 0
            for col_idx, (col, col_width) in enumerate(zip(self.table.columns, column_widths)):
                value = item.get(col, "")
                
                if col == "type" and isinstance(value, int):
                    minutes = round(value / 60)
                    display_str = f"{minutes}m".ljust(col_width)
                else:
                    from .utils import sanitize_display_string
                    display_str = sanitize_display_string(str(value), max_length=col_width - 1).ljust(col_width)
                
                is_cell_selected = (self.table.selection_mode == 'cell' and 
                                    is_selected and 
                                    col_idx == self.table.selected_column)
                
                if is_selected and self.table.selection_mode == 'row':
                    full_line = display_str + " "
                    try:
                        self.stdscr.addstr(y, x, full_line, curses.A_REVERSE)
                    except curses.error:
                        pass
                elif is_cell_selected:
                    full_line = display_str + " "
                    try:
                        self.stdscr.addstr(y, x, full_line, curses.A_REVERSE)
                    except curses.error:
                        pass
                else:
                    color = curses.A_NORMAL
                    if col == "type":
                        color = self.table.get_type_color(value)
                    elif col == "status":
                        color = self.table.get_status_color(value)
                        if color == curses.A_NORMAL:
                            color = self.table.get_dynamic_color("status", str(value))
                    
                    try:
                        self.stdscr.addstr(y, x, display_str, color)
                    except curses.error:
                        pass
                
                x += col_width + 1
    
    def _render_footer(self, height: int, width: int) -> None:
        """Render footer with keybind hints."""
        footer_y = height - 1
        if self.key_handler.mode == Mode.SEARCH:
            keybind_hints = "Type to filter | Tab/S-Tab navigate | ESC exit search | Enter select"
        elif self.table.selection_mode == 'cell':
            if len(self.tabs) > 1:
                keybind_hints = "j/↓ down | k/↑ up | h/← left cell | l/→ right cell | Enter select cell | c: row mode | / search | q quit"
            else:
                keybind_hints = "j/↓ down | k/↑ up | h/← left cell | l/→ right cell | Enter select cell | c: row mode | / search | q quit"
        else:
            if len(self.tabs) > 1:
                keybind_hints = "j/↓ down | k/↑ up | h/← prev tab | l/→ next tab | Enter select row | c: cell mode | / search | q quit"
            else:
                keybind_hints = "j/↓ down | k/↑ up | Enter select row | c: cell mode | / search | q quit"
        draw_footer(self.stdscr, footer_y, keybind_hints, width)
    
    def run(self, stdscr) -> None:
        """Run the TUI."""
        self.init_curses(stdscr)
        self.load_data()
        
        if not self.current_tab or not self.current_tab.data:
            stdscr.addstr(0, 0, "0 items")
            stdscr.getch()
            return
        
        while True:
            self.check_and_reload()
            self.render()
            
            key = stdscr.getch()
            
            self.debug_file.write(f"Key: {key:4d}\n")
            self.debug_file.flush()
            
            if key == -1:
                self.key_handler.update_leader_timeout()
                continue
            
            if self.key_handler.is_left_key(key) and self.table.selection_mode != 'cell':
                self.tab_left()
            elif self.key_handler.is_right_key(key) and self.table.selection_mode != 'cell':
                self.tab_right()
            else:
                should_exit, selected_item = self.key_handler.handle_key(key, self.table, self.terminal_height)
                
                if should_exit:
                    break
                
                if self.single_select and selected_item is not None:
                    if self.table.selection_mode == 'cell':
                        cell_value = self.table.data[self.table.selected_index].get(
                            self.table.columns[self.table.selected_column]
                        )
                        self.selected_output = {
                            "field": self.table.columns[self.table.selected_column],
                            "value": cell_value
                        }
                    else:
                        self.selected_output = selected_item
                    
                    # Write to output file to bypass curses stdout interference
                    if self.output_file:
                        with open(self.output_file, 'w') as f:
                            json.dump(self.selected_output, f, indent=2)
                            f.write('\n')
                    
                    break
        
        self.debug_file.close()
        self.cleanup_curses()
        return self.selected_output
