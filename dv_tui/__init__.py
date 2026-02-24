"""
dv-tui: A curses-based TUI for viewing JSON/CSV data with nvim integration.
"""

__version__ = "0.1.0"
__author__ = "Ylan Allouche"

from .core import TUI
from .table import Table
from .config import load_config, load_config_from_inline_json, DEFAULT_CONFIG, validate_config, get_column_widths, Config
from .data_loaders import load_file


class TableUI:
    """High-level API for using dv-tui as a Python library."""
    
    def __init__(self, data, columns=None, keybinds=None, enum_config=None):
        """
        Initialize TableUI with data.
        
        Args:
            data: List of dictionaries to display
            columns: Optional list of column names to display
            keybinds: Optional keybindings dict (e.g., {"normal": {"j": "custom_down"}})
            enum_config: Optional enum configuration for dropdowns
        """
        self._data = data
        self._columns = columns
        self._keybinds = keybinds or {}
        self._enum_config = enum_config
        
        self._key_handlers = {}
        self._trigger_handlers = {}
        
        self._on_quit_callback = None
        self._on_mode_change_callback = None
        self._on_select_callback = None
        
        self._tui = None
        self._selected_output = None
        
    def bind_key(self, key, handler):
        """
        Bind a key to a Python function.
        
        Args:
            key: Key name (e.g., 'Enter', 'q', 'j')
            handler: Function that receives selected row data when key is pressed
        """
        self._key_handlers[key] = handler
        
    def bind_trigger(self, trigger_name, handler):
        """
        Bind a trigger event to a Python function.
        
        Args:
            trigger_name: Trigger name (e.g., 'on_enter', 'on_select')
            handler: Function that receives event data when trigger fires
        """
        self._trigger_handlers[trigger_name] = handler
        
    def update_data(self, data):
        """
        Update the data programmatically.
        
        Args:
            data: New list of dictionaries to display
        """
        self._data = data
        
    def on_quit(self, callback):
        """
        Set callback for when TUI exits.
        
        Args:
            callback: Function to call when TUI exits
        """
        self._on_quit_callback = callback
        
    def on_mode_change(self, callback):
        """
        Set callback for when selection mode changes.
        
        Args:
            callback: Function that receives mode name when mode changes
        """
        self._on_mode_change_callback = callback
        
    def on_select(self, callback):
        """
        Set callback for when a row is selected.
        
        Args:
            callback: Function that receives selected row data
        """
        self._on_select_callback = callback
        
    def run(self):
        """
        Start the TUI and run until user quits.
        
        Returns:
            Selected item data if any, None otherwise
        """
        import curses
        import tempfile
        import os
        
        # Create config from constructor arguments
        cli_config = {}
        
        if self._columns:
            cli_config["columns"] = self._columns
            
        if self._keybinds:
            cli_config["binds"] = []
            for mode, binds in self._keybinds.items():
                for key, action in binds.items():
                    cli_config["binds"].append({"key": key, "action": action, "mode": mode})
        
        if self._enum_config:
            cli_config["enum"] = self._enum_config
        
        config = load_config(
            config_path=None,
            inline_config={},
            cli_config=cli_config,
        )
        
        # Create temporary file with data
        import json
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self._data, temp_file, indent=2)
        temp_file.close()
        
        try:
            # Create TUI instance
            self._tui = TUI([temp_file.name], single_select=False, config=config, tab_field="_config.tabs")
            
            # Wrap the TUI run method to handle our callbacks
            original_run = self._tui.run
            selected_data = [None]
            
            def wrapped_run(stdscr):
                result = original_run(stdscr)
                selected_data[0] = result
                
                # Call quit callback
                if self._on_quit_callback:
                    self._on_quit_callback()
                    
                return result
            
            # Run curses
            try:
                stdscr = curses.initscr()
                curses.noecho()
                curses.cbreak()
                stdscr.keypad(True)
                
                result = wrapped_run(stdscr)
                
            except curses.error:
                pass
            finally:
                if stdscr is not None:
                    try:
                        stdscr.keypad(False)
                        curses.echo()
                        curses.nocbreak()
                        curses.endwin()
                    except curses.error:
                        pass
            
            return selected_data[0]
            
        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass


def main():
    """Import and run CLI main function lazily to avoid circular import."""
    from .cli import main as cli_main
    return cli_main()

__all__ = [
    "TUI",
    "TableUI",
    "Table",
    "Config",
    "load_config",
    "load_config_from_inline_json",
    "validate_config",
    "get_column_widths",
    "DEFAULT_CONFIG",
    "load_file",
    "main",
]
