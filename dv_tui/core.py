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
from .config import (
    Config,
    load_config,
    load_config_from_inline_json,
    load_config_from_inline_json_file,
    get_column_widths,
)
from .data_loaders import (
    load_file, get_file_mtime,
    DataLoader, JsonDataLoader, CsvDataLoader, StdinDataLoader,
    create_loader, detect_source
)
from .ui import init_color_pairs, draw_tabs, draw_footer, EnumChoiceDialog, get_enum_options
from .actions import select_item
from .utils import beautify_filename, sanitize_display_string


@dataclass
class Tab:
    """
    Tab state management with data, selection, and scroll state.
    
    Attributes:
        name: Display name for the tab
        source: Source identifier (file path or "inline")
        data: List of data items for this tab
        table: Table object for rendering
        selected_index: Currently selected row index
        scroll_offset: Scroll position for viewport
        selection_mode: Selection mode ('row' or 'cell')
        selected_column: Currently selected column index (cell mode)
        last_mtime: Last modification time for file tracking
        config: Configuration for this tab
        parent_context: Parent data context for triggers/actions
        navigation_stack: Stack for drill-down navigation history
    """
    
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
    parent_context: Optional[Dict[str, Any]] = None
    navigation_stack: List[Dict[str, Any]] = field(default_factory=list)


class TUI:
    """
    TUI engine with curses wrapper.
    
    Main class for running dv-tui with curses interface. Handles file loading,
    tab management, user input, and rendering.
    """
    
    def __init__(
        self,
        files: List[str],
        single_select: bool = False,
        config: Optional[Config] = None,
        config_path: Optional[str] = None,
        delimiter: str = ',',
        skip_headers: bool = False,
        tab_field: str = '_config.tabs',
        cli_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize TUI with files and configuration.
        
        Args:
            files: List of file paths to load
            single_select: Exit after selection (default: False)
            config: Custom configuration (optional)
            config_path: Path to external config file (optional)
            delimiter: CSV delimiter (default: ',')
            skip_headers: Skip CSV headers (default: False)
            tab_field: Field name for tabs config in JSON (default: '_config.tabs')
        """
        self.files = files
        self.active_tab = 0
        self.single_select = single_select
        self.delimiter = delimiter
        self.skip_headers = skip_headers
        self.tab_field = tab_field
        self.tab_name = config.tab_name if config else None
        self.selected_output = None

        # Raw CLI config dict (used to re-apply CLI precedence when per-tab inline config exists)
        self.cli_config: Dict[str, Any] = cli_config or {}
        
        self.tabs: List[Tab] = []
        self.last_check_time = 0
        self.check_cooldown = 0.5
        self.last_refresh_time = 0
        
        self.key_handler: Optional[KeyHandler] = None
        self.loaders: List[DataLoader] = []
        
        if config is None:
            self.config = load_config(config_path=config_path, cli_config=self.cli_config)
        else:
            self.config = config
        
        self.terminal_height = 0
        self.stdscr = None
        self.output_file = None
    
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
        command = self.config.refresh.command if self.config.refresh else None
        delimiter = self.config.delimiter
        skip_headers = self.config.skip_headers
        for i, file_path in enumerate(self.files):
            try:
                loader = create_loader(file_path, stdin_timeout=stdin_timeout, delimiter=delimiter, command=command, skip_headers=skip_headers)
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
        
        inline_config: Dict[str, Any] = {}

        # Prefer extracting inline config from the source JSON file before data filtering.
        # This enables per-tab inline config without displaying the _config item.
        current_file = self.current_file
        is_fd_path = (
            current_file.startswith('/dev/fd/')
            or current_file.startswith('/proc/self/fd/')
            or (current_file.startswith('/proc/') and '/fd/' in current_file)
        )

        if (not is_fd_path) and current_file.lower().endswith('.json'):
            inline_config = load_config_from_inline_json_file(current_file)
        else:
            inline_config = load_config_from_inline_json(tab.data)

        if inline_config:
            tab_config = load_config(
                config_path=self.config.config_file,
                inline_config=inline_config,
                cli_config=self.cli_config,
            )
            tab.config = tab_config
        else:
            tab.config = self.config
        
        tab.last_mtime = get_file_mtime(self.current_file)
        
        # Use configured columns if set, otherwise auto-detect from data
        columns = tab.config.columns if tab.config else self.config.columns
        enum_config = tab.config.enum if tab.config else self.config.enum
        tab.table = Table(tab.data, columns, enum_config)
        tab.table.selected_index = tab.selected_index
        tab.table.scroll_offset = tab.scroll_offset
        tab.table.selection_mode = tab.selection_mode
        tab.table.selected_column = tab.selected_column
    
    def check_and_reload(self) -> bool:
        """
        Check if file has been modified and reload if necessary.
        
        Checks file modification time with cooldown to prevent excessive reloading.
        
        Returns:
            True if file was reloaded, False otherwise
        """
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
    
    def refresh_data(self, show_warning: bool = True) -> bool:
        """
        Refresh data from the current data source.
        
        Reloads data from the current tab's data loader, supporting
        command-based refresh and file-based sources.
        
        Args:
            show_warning: Whether to show a warning message if refresh is not supported
            
        Returns:
            True if refresh was successful, False otherwise
        """
        if not self.current_tab or self.active_tab >= len(self.loaders):
            return False
        
        loader = self.loaders[self.active_tab]
        if not loader:
            return False
        
        if not loader.can_refresh():
            if show_warning and self.stdscr:
                from .actions import show_message
                show_message(self.stdscr, "Cannot refresh piped data without command", timeout=2.0)
            return False
        
        try:
            tab = self.tabs[self.active_tab]
            tab.data = loader.refresh()
            
            inline_config: Dict[str, Any] = {}

            current_file = self.current_file
            is_fd_path = (
                current_file.startswith('/dev/fd/')
                or current_file.startswith('/proc/self/fd/')
                or (current_file.startswith('/proc/') and '/fd/' in current_file)
            )

            if (not is_fd_path) and current_file.lower().endswith('.json'):
                inline_config = load_config_from_inline_json_file(current_file)
            else:
                inline_config = load_config_from_inline_json(tab.data)

            if inline_config:
                tab_config = load_config(
                    config_path=self.config.config_file,
                    inline_config=inline_config,
                    cli_config=self.cli_config,
                )
                tab.config = tab_config
            else:
                tab.config = self.config
            
            tab.last_mtime = get_file_mtime(self.current_file)
            
            columns = tab.config.columns if tab.config else self.config.columns
            enum_config = tab.config.enum if tab.config else self.config.enum
            tab.table = Table(tab.data, columns, enum_config)
            tab.table.selected_index = tab.selected_index
            tab.table.scroll_offset = tab.scroll_offset
            tab.table.selection_mode = tab.selection_mode
            tab.table.selected_column = tab.selected_column
            return True
        except Exception as e:
            if show_warning and self.stdscr:
                from .actions import show_message
                show_message(self.stdscr, f"Refresh failed: {str(e)}", timeout=2.0)
            return False
    
    def _check_auto_refresh(self) -> None:
        """Check if auto-refresh should be triggered based on interval."""
        if not self.config.refresh or not self.config.refresh.enabled:
            return
        
        interval = self.config.refresh.interval
        if interval <= 0:
            return
        
        current_time = time.time()
        if current_time - self.last_refresh_time >= interval:
            self.last_refresh_time = current_time
            self.refresh_data(show_warning=False)
    
    def _on_trigger(self) -> None:
        """Callback for trigger events - refresh data if on_trigger is enabled."""
        if not self.current_tab or not self.current_tab.config:
            return
        
        tab_config = self.current_tab.config
        if not tab_config.refresh or not tab_config.refresh.on_trigger:
            return
        
        self.refresh_data(show_warning=False)
    
    def init_curses(self, stdscr) -> None:
        """Initialize curses settings."""
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.timeout(100)
        init_color_pairs()
        
        self.key_handler = KeyHandler(self.config, on_trigger_callback=self._on_trigger)
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
        pass
    
    def _handle_enum_picker(self) -> None:
        """
        Handle ctrl-e to open enum picker dialog.
        
        Opens a popup dialog allowing user to select from enum options
        for the current cell. Only works in cell mode with enum config.
        """
        if not self.current_tab or not self.table:
            return
        
        # Only work in cell mode with enum config for current column
        if self.table.selection_mode != 'cell' or self.table.selected_column >= len(self.table.columns):
            return
        
        field_name = self.table.columns[self.table.selected_column]
        enum_config = None
        
        if self.current_tab.config and self.current_tab.config.enum:
            enum_config = getattr(self.current_tab.config.enum, field_name, None)
        
        if not enum_config:
            return
        
        # Build context for external commands
        context = {
            "selected_index": self.table.selected_index,
            "selected_column": field_name,
            "selected_row": self.table.selected_item,
            "selected_cell": self.table.selected_item.get(field_name) if field_name else None,
        }
        
        # Get enum options
        options = get_enum_options(enum_config, field_name, self.current_tab.data, context)
        
        if not options:
            return
        
        # Re-render the main window before showing dialog
        self.stdscr.clear()
        self.stdscr.refresh()
        
        # Show enum picker dialog
        dialog = EnumChoiceDialog(self.stdscr, options, f"Select {field_name}")
        selected_value = dialog.show()
        
        if selected_value is not None:
            # Update cell value
            self.current_tab.data[self.table.selected_index][field_name] = selected_value
            
            # Trigger on_change event if configured
            self._trigger_enum_change_event(field_name, selected_value)
    
    def _handle_enum_cycle(self, key: int) -> None:
        """
        Handle e/E keys to cycle through enum values in current cell.
        
        Cycles through enum options for the current cell. 'e' cycles to next,
        'E' cycles to previous. Only works in cell mode with enum config.
        
        Args:
            key: Key code (ord('e') or ord('E'))
        """
        if not self.current_tab or not self.table:
            return
        
        # Only work in cell mode with enum config for current column
        if self.table.selection_mode != 'cell' or self.table.selected_column >= len(self.table.columns):
            return
        
        field_name = self.table.columns[self.table.selected_column]
        enum_config = None
        
        if self.current_tab.config and self.current_tab.config.enum:
            enum_config = getattr(self.current_tab.config.enum, field_name, None)
        
        if not enum_config:
            return
        
        # Build context for external commands
        context = {
            "selected_index": self.table.selected_index,
            "selected_column": field_name,
            "selected_row": self.table.selected_item,
            "selected_cell": self.table.selected_item.get(field_name) if field_name else None,
        }
        
        # Get enum options
        options = get_enum_options(enum_config, field_name, self.current_tab.data, context)
        
        if not options:
            return
        
        # Get current value
        current_value = str(self.current_tab.data[self.table.selected_index].get(field_name, ""))
        
        # Find current value index
        try:
            current_index = options.index(current_value)
        except ValueError:
            current_index = -1
        
        # Determine direction
        if self.key_handler.is_enum_cycle_next_key(key):
            # Cycle to next value (e key)
            new_index = (current_index + 1) % len(options)
        else:
            # Cycle to previous value (E key)
            new_index = (current_index - 1) % len(options)
        
        new_value = options[new_index]
        
        # Update cell value
        self.current_tab.data[self.table.selected_index][field_name] = new_value
        
        # Trigger on_change event if configured
        self._trigger_enum_change_event(field_name, new_value)
    
    def _trigger_enum_change_event(self, field_name: str, new_value: Any) -> None:
        """
        Trigger enum change event if configured.
        
        Fires the on_navigate_cell trigger when an enum value is changed,
        providing context about the field and new value.
        
        Args:
            field_name: Name of the field that changed
            new_value: New value selected for the field
        """
        if not self.current_tab or not self.current_tab.config:
            return
        
        triggers = self.current_tab.config.triggers
        if not triggers:
            return
        
        # Check if there's a cell-level trigger for on_navigate_cell or on_enter
        # We'll use on_navigate_cell for enum changes as it's cell-specific
        cell_key = f"{self.table.selected_index}:{field_name}"
        if triggers.cells and cell_key in triggers.cells:
            cell_triggers = triggers.cells[cell_key]
            if cell_triggers.on_navigate_cell:
                context = self._build_trigger_context()
                context["DV_ENUM_FIELD"] = field_name
                context["DV_ENUM_NEW_VALUE"] = str(new_value)
                self.key_handler._execute_trigger_event("on_navigate_cell", self.table, async_exec=False)
    
    def _build_trigger_context(self) -> Dict[str, Any]:
        """
        Build trigger context dictionary.
        
        Creates a dictionary with current selection state for use in trigger
        execution. Includes selected index, column, row, and cell values.
        
        Returns:
            Dictionary with trigger context variables
        """
        if not self.table or not self.current_tab:
            return {}
        
        context = {
            "selected_index": self.table.selected_index,
            "selected_column": None,
            "selected_row": self.table.selected_item,
            "selected_cell": None,
        }
        
        if self.table.selection_mode == 'cell' and self.table.selected_column < len(self.table.columns):
            col_name = self.table.columns[self.table.selected_column]
            context["selected_cell"] = self.table.selected_item.get(col_name)
            context["selected_column"] = col_name
        
        return context
    
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
    
    def create_tab_from_data(self, name: str, data: List[Dict[str, Any]], parent_context: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a new tab from the provided data.
        
        Args:
            name: Name for the new tab
            data: Data to display in the new tab
            parent_context: Parent data context for triggers/actions
        """
        tab = Tab(name=name, source="inline", data=data, config=self.config)
        tab.parent_context = parent_context
        
        # Use configured columns if set, otherwise auto-detect from data
        columns = self.config.columns
        enum_config = self.config.enum
        tab.table = Table(tab.data, columns, enum_config)
        
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
    
    def drill_down(self, value: Any, field_name: Optional[str] = None) -> None:
        """
        Drill down into nested data.
        
        Args:
            value: The cell value (list or dict) to drill into
            field_name: The name of the field being drilled into (optional)
        """
        if not self.current_tab or not self.table:
            return
        
        drill_config = self.current_tab.config.drill_down if self.current_tab.config else None
        
        # If drill_down config has a field_name, use that to get data
        if drill_config and drill_config.field_name and drill_config.field_name != field_name:
            if isinstance(value, dict) and drill_config.field_name in value:
                value = value[drill_config.field_name]
                field_name = drill_config.field_name
        
        # Convert value to list format for table display
        nested_data = []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    nested_data.append(item)
                else:
                    nested_data.append({"value": item})
        elif isinstance(value, dict):
            # Smart handling: if dict has a single array field, use that array's content
            if len(value) == 1:
                single_key = list(value.keys())[0]
                single_value = value[single_key]
                if isinstance(single_value, list):
                    # Drill into the array content directly
                    for item in single_value:
                        if isinstance(item, dict):
                            nested_data.append(item)
                        else:
                            nested_data.append({"value": item})
                else:
                    nested_data = [value]
            else:
                nested_data = [value]
        else:
            return  # Not drillable
        
        # Set parent context
        parent_context = self.current_tab.data[self.table.selected_index].copy() if 0 <= self.table.selected_index < len(self.current_tab.data) else None
        
        # Check if new_tab is enabled
        if drill_config and drill_config.new_tab:
            drill_name = f"{self.current_tab.name}"
            if field_name:
                drill_name += f".{field_name}"
            drill_name += " [drill-down]"
            self.create_tab_from_data(drill_name, nested_data, parent_context)
        else:
            # Save current state to navigation stack
            # Store table reference for fast restoration (avoids expensive Table recreation on go_back)
            if self.current_tab and self.table:
                self.current_tab.navigation_stack.append({
                    "table": self.table,
                    "data": self.current_tab.data,
                    "selected_index": self.table.selected_index,
                    "scroll_offset": self.table.scroll_offset,
                    "selection_mode": self.table.selection_mode,
                    "selected_column": self.table.selected_column,
                    "parent_context": self.current_tab.parent_context,
                })
            
            # Create drill-down view
            drill_name = f"{self.current_tab.name}"
            if field_name:
                drill_name += f".{field_name}"
            drill_name += " [drill-down]"
            
            # Replace current tab data with drill-down data
            self.current_tab.data = nested_data
            self.current_tab.parent_context = parent_context
            columns = self.config.columns
            enum_config = self.config.enum
            self.current_tab.table = Table(self.current_tab.data, columns, enum_config)
            self.current_tab.table.selected_index = 0
            self.current_tab.table.scroll_offset = 0
            self.current_tab.table.selection_mode = 'row'
            self.current_tab.table.selected_column = 0

            # Fire drilldown trigger with comprehensive navigation context
            drill_level = len(self.current_tab.navigation_stack)
            drill_to_context = {
                # Current view AFTER drilldown (what we just entered)
                "selected_index": self.current_tab.table.selected_index,
                "selected_column": self.current_tab.table.selected_column,
                "selected_cell": self.current_tab.table.selected_item,

                # Level information
                "level_name": self.current_tab.name + " [drill-down]",
                "depth": drill_level + 1,

                # Parent level we came FROM
                "parent_level_index": self.table.selected_index,
                "parent_level_name": self.current_tab.name,

                # Dataset information
                "dataset_size": len(nested_data),
                "data_source": self.current_file,
            }
            if self.key_handler:
                self.key_handler.trigger_drilldown_event(
                    self.table,
                    drill_to_context=drill_to_context
                )
    
    def go_back(self) -> bool:
        """
        Go back to previous navigation level.
        
        Optimized to restore cached Table object instead of recreating it.
        This avoids expensive column detection and color map recalculation.
        
        Returns:
            True if went back, False if no previous level exists
        """
        if not self.current_tab:
            return False
        
        if not self.current_tab.navigation_stack:
            return False
        
        previous_state = self.current_tab.navigation_stack.pop()
        
        # Restore previous state by directly swapping the table
        # Much faster than recreating Table (avoids _detect_columns, color map rebuild)
        self.current_tab.table = previous_state["table"]
        self.current_tab.data = previous_state["data"]
        self.current_tab.parent_context = previous_state["parent_context"]
        
        # Restore selection state
        self.current_tab.table.selected_index = previous_state["selected_index"]
        self.current_tab.table.scroll_offset = previous_state["scroll_offset"]
        self.current_tab.table.selection_mode = previous_state["selection_mode"]
        self.current_tab.table.selected_column = previous_state["selected_column"]

        # Fire backup trigger with navigation stack depth after pop
        backup_level = len(self.current_tab.navigation_stack)
        previous_level_name = "top level" if not previous_state.get("parent_context") else "nested level"
        backup_to_context = {
            # Current view AFTER backup (what we just restored to)
            "selected_index": self.current_tab.table.selected_index,
            "selected_column": self.current_tab.table.selected_column,
            "selected_cell": self.current_tab.table.selected_item,

            # Level information
            "level_name": self.current_tab.name,
            "depth": backup_level,

            # Previous level we just LEFT
            "previous_level_index": previous_state["selected_index"],
            "previous_level_name": previous_level_name,

            # Dataset information
            "dataset_size": len(self.current_tab.data),
            "data_source": self.current_file,

            # Original parent context for reference
            "previous_parent_context": previous_state.get("parent_context")
        }
        if self.key_handler:
            self.key_handler.trigger_backup_event(
                self.table,
                backup_to_context=backup_to_context
            )

        return True
    
    def _get_named_array_label(self, value: Any) -> Optional[str]:
        """
        Get label for objects with a single array field.
        
        Returns the field name if value is a dict with exactly one key
        containing an array, otherwise None.
        """
        if not isinstance(value, dict):
            return None
        if len(value) != 1:
            return None
        
        single_key = list(value.keys())[0]
        single_value = value[single_key]
        
        if isinstance(single_value, list):
            return f"[{single_key}]"
        
        return None
    
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
                drill_level = len(tab.navigation_stack) + 1
                if self.key_handler.mode == Mode.SEARCH:
                    tab_text = f"{display_name} (Level {drill_level}) - {len(self.key_handler.filtered_indices)}/{len(tab.data)} items [SEARCH]"
                else:
                    tab_text = f"{display_name} (Level {drill_level}) - {len(tab.data)} items"
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
                
                is_drillable = self.table.is_drillable(item_index, col_idx)
                
            if is_drillable:
                named_array_label = self._get_named_array_label(value)
                if named_array_label:
                    display_str = named_array_label.ljust(col_width)
                else:
                    drill_indicator = "[]" if isinstance(value, list) else "{}"
                    display_str = drill_indicator.ljust(col_width)
            else:
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
                    # Use enum color cycling for enum fields
                    color = self.table.get_enum_color(col, str(value))
                    
                    if is_drillable:
                        color = color | curses.A_BOLD
                    
                    try:
                        self.stdscr.addstr(y, x, display_str, color)
                    except curses.error:
                        pass
                
                x += col_width + 1
    
    def _render_footer(self, height: int, width: int) -> None:
        """Render footer with keybind hints."""
        footer_y = height - 1
        has_nav_stack = self.current_tab and len(self.current_tab.navigation_stack) > 0
        back_hint = " | ESC go back" if has_nav_stack else ""
        has_enum = self.current_tab and self.current_tab.config and self.current_tab.config.enum
        enum_hint = ""
        if has_enum and self.table.selection_mode == 'cell':
            enum_hint = " | e/E cycle enum | ^E popup"
        if self.key_handler.mode == Mode.SEARCH:
            keybind_hints = "Type to filter | Tab/S-Tab navigate | ESC exit search | Enter select" + back_hint
        elif self.table.selection_mode == 'cell':
            if len(self.tabs) > 1:
                keybind_hints = "j/↓ down | k/↑ up | h/← left cell | l/→ right cell | Enter drill-down/select cell | c: row mode | / search | q quit" + enum_hint + back_hint
            else:
                keybind_hints = "j/↓ down | k/↑ up | h/← left cell | l/→ right cell | Enter drill-down/select cell | c: row mode | / search | q quit" + enum_hint + back_hint
        else:
            if len(self.tabs) > 1:
                keybind_hints = "j/↓ down | k/↑ up | h/← prev tab | l/→ next tab | Enter select row | c: cell mode | / search | q quit" + back_hint
            else:
                keybind_hints = "j/↓ down | k/↑ up | Enter select row | c: cell mode | / search | q quit" + back_hint
        draw_footer(self.stdscr, footer_y, keybind_hints, width)
    
    def run(self, stdscr) -> None:
        """Run TUI."""
        self.init_curses(stdscr)
        self.load_data()

        if not self.current_tab or not self.current_tab.data:
            stdscr.addstr(0, 0, "0 items")
            stdscr.getch()
            return

        # Fire startup trigger after data is loaded
        if self.key_handler:
            self.key_handler.trigger_startup_event(
                self.table,
                data_source=self.current_file,
                config_file=self.config.config_file
            )
        
        while True:
            self.check_and_reload()
            self._check_auto_refresh()
            self.render()
            key = stdscr.getch()
            
            if key == -1:
                self.key_handler.update_leader_timeout()
                continue
            
            if self.key_handler.is_left_key(key) and self.table.selection_mode != 'cell':
                self.tab_left()
            elif self.key_handler.is_right_key(key) and self.table.selection_mode != 'cell':
                self.tab_right()
            elif self.key_handler.is_escape_key(key) and self.current_tab and len(self.current_tab.navigation_stack) > 0:
                self.go_back()
            elif self.key_handler.is_enum_picker_key(key):
                self._handle_enum_picker()
            elif self.key_handler.is_enum_cycle_next_key(key) or self.key_handler.is_enum_cycle_prev_key(key):
                self._handle_enum_cycle(key)
            else:
                should_exit, selected_item = self.key_handler.handle_key(key, self.table, self.terminal_height)
                
                if should_exit:
                    break
                
                if selected_item and selected_item.get("drill_down"):
                    self.drill_down(selected_item["value"], selected_item["column"])
                elif self.single_select and selected_item is not None:
                    self.selected_output = selected_item
                    
                    # Write to output file to bypass curses stdout interference
                    if self.output_file:
                        with open(self.output_file, 'w') as f:
                            json.dump(self.selected_output, f, indent=2)
                            f.write('\n')
                    
                    break
        
        self.cleanup_curses()
        return self.selected_output
