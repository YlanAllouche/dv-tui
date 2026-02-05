import time
import curses
from typing import Dict, Any, List, Callable, Optional, Tuple, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .config import Config


class Mode(Enum):
    """TUI modes."""
    NORMAL = "normal"
    SEARCH = "search"
    NAVIGATE = "navigate"


class KeyHandler:
    """Handle keybinds and mode management."""
    
    def __init__(self, config: Optional["Config"] = None):
        self.mode = Mode.NORMAL
        self.leader_pending = False
        self.leader_timeout = 0
        self.leader_key = ord(';')
        self.leader_timeout_duration = 0.5
        
        self.search_query = ""
        self.filtered_indices: List[int] = []
        self.search_selected_index = 0
        self.pre_search_selected_index = 0
        self.pre_search_scroll_offset = 0
        
        self.keybinds: Dict[str, Any] = {}
        self.custom_handlers: Dict[int, Callable] = {}
        
        if config:
            self.load_config(config)
    
    def load_config(self, config: "Config") -> None:
        """Load keybind configuration."""
        if hasattr(config, 'keybinds'):
            self.keybinds = config.keybinds
        
        if isinstance(self.keybinds, dict):
            if "normal" in self.keybinds:
                normal_keybinds = self.keybinds["normal"]
                leader = normal_keybinds.get("leader", ord(';'))
                self.leader_key = leader if isinstance(leader, int) else ord(leader)
                self.keybinds = normal_keybinds
            else:
                leader = self.keybinds.get("leader", ord(';'))
                self.leader_key = leader if isinstance(leader, int) else ord(leader)
    
    def is_quit_key(self, key: int) -> bool:
        """Check if key is a quit key."""
        quit_keys = self.keybinds.get("quit", [ord('q'), ord('Q')])
        return key in quit_keys
    
    def is_down_key(self, key: int) -> bool:
        """Check if key is a down key."""
        down_keys = self.keybinds.get("down", [ord('j'), ord('J'), 258])
        return key in down_keys
    
    def is_up_key(self, key: int) -> bool:
        """Check if key is an up key."""
        up_keys = self.keybinds.get("up", [ord('k'), ord('K'), 259])
        return key in up_keys
    
    def is_left_key(self, key: int) -> bool:
        """Check if key is a left key."""
        left_keys = self.keybinds.get("left", [ord('h'), ord('H'), 260])
        return key in left_keys
    
    def is_right_key(self, key: int) -> bool:
        """Check if key is a right key."""
        right_keys = self.keybinds.get("right", [ord('l'), ord('L'), 261])
        return key in right_keys
    
    def is_search_key(self, key: int) -> bool:
        """Check if key starts search mode."""
        search_key = self.keybinds.get("search", ord('/'))
        return key == search_key
    
    def is_enter_key(self, key: int) -> bool:
        """Check if key is enter."""
        enter_keys = self.keybinds.get("enter", [ord('\n'), 10])
        return key in enter_keys
    
    def is_escape_key(self, key: int) -> bool:
        """Check if key is escape."""
        return key == self.keybinds.get("escape", 27)
    
    def is_backspace_key(self, key: int) -> bool:
        """Check if key is backspace."""
        backspace_keys = self.keybinds.get("backspace", [263, 127])
        return key in backspace_keys
    
    def is_toggle_mode_key(self, key: int) -> bool:
        """Check if key toggles selection mode."""
        toggle_key = self.keybinds.get("toggle_mode", ord('c'))
        return key == toggle_key
    
    def is_leader_key(self, key: int) -> bool:
        """Check if key is the leader key."""
        return key == self.leader_key
    
    def register_handler(self, key: int, handler: Callable) -> None:
        """Register a custom key handler."""
        self.custom_handlers[key] = handler
    
    def handle_key(self, key: int, table, terminal_height: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Handle a key press.
        
        Returns:
            (should_exit, selected_item)
        """
        if key in self.custom_handlers:
            result = self.custom_handlers[key](key)
            if result:
                return result
        
        if self.mode == Mode.SEARCH:
            return self._handle_search_mode(key, table, terminal_height)
        else:
            return self._handle_normal_mode(key, table)
    
    def _handle_normal_mode(self, key: int, table) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle key in normal mode."""
        if self.is_quit_key(key):
            return True, None
        
        if self.is_search_key(key):
            self.enter_search_mode(table)
            return False, None
        
        if self.is_toggle_mode_key(key):
            if table.selection_mode == 'row':
                table.selection_mode = 'cell'
                table.selected_column = 0
            else:
                table.selection_mode = 'row'
        
        if self.is_down_key(key):
            table.scroll_down()
        elif self.is_up_key(key):
            table.scroll_up()
        elif self.is_left_key(key):
            if table.selection_mode == 'cell':
                table.selected_column = max(0, table.selected_column - 1)
        elif self.is_right_key(key):
            if table.selection_mode == 'cell':
                table.selected_column = min(len(table.columns) - 1, table.selected_column + 1)
        elif self.is_enter_key(key):
            if table.selection_mode == 'cell':
                cell_value = table.data[table.selected_index].get(table.columns[table.selected_column])
                return False, {
                    "value": cell_value,
                    "row": table.selected_index,
                    "column": table.columns[table.selected_column],
                    "column_index": table.selected_column,
                    "item": table.selected_item
                }
            return False, table.selected_item
        elif self.is_leader_key(key):
            self.leader_pending = True
            self.leader_timeout = time.time()
        
        return False, None
    
    def _handle_search_mode(self, key: int, table, terminal_height: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle key in search mode."""
        if self.is_escape_key(key):
            self.exit_search_mode(table)
            return False, None
        
        if self.is_enter_key(key):
            if self.filtered_indices:
                table.selected_index = self.filtered_indices[self.search_selected_index]
            self.exit_search_mode(table)
            return False, table.selected_item
        
        if key == curses.KEY_UP or key == 353:
            self.search_selected_index = max(0, self.search_selected_index - 1)
        elif key == curses.KEY_DOWN or key == 9:
            max_index = len(self.filtered_indices) - 1
            if max_index >= 0:
                self.search_selected_index = min(max_index, self.search_selected_index + 1)
                viewport_height = terminal_height - 4
                if self.search_selected_index >= table.scroll_offset + viewport_height:
                    table.scroll_offset = self.search_selected_index - viewport_height + 1
        elif 32 <= key < 127:
            self.search_query += chr(key)
            self.update_filtered_indices(table)
        elif self.is_backspace_key(key):
            if self.search_query:
                self.search_query = self.search_query[:-1]
                self.update_filtered_indices(table)
                if self.filtered_indices:
                    self.search_selected_index = min(self.search_selected_index, len(self.filtered_indices) - 1)
                else:
                    self.search_selected_index = 0
        
        return False, None
    
    def enter_search_mode(self, table) -> None:
        """Enter search mode."""
        self.mode = Mode.SEARCH
        self.pre_search_selected_index = table.selected_index
        self.pre_search_scroll_offset = table.scroll_offset
        self.search_query = ""
        self.filtered_indices = list(range(len(table.data)))
        self.search_selected_index = 0
        table.scroll_offset = 0
    
    def exit_search_mode(self, table) -> None:
        """Exit search mode."""
        table.selected_index = self.pre_search_selected_index
        table.scroll_offset = self.pre_search_scroll_offset
        self.mode = Mode.NORMAL
        self.search_query = ""
        self.filtered_indices = []
        self.search_selected_index = 0
    
    def update_filtered_indices(self, table) -> None:
        """Update filtered indices based on search query."""
        from .utils import fuzzy_filter
        matched = fuzzy_filter(table.data, self.search_query, "summary")
        self.filtered_indices = [table.data.index(item) for item in matched]
        self.search_selected_index = 0
        table.scroll_offset = 0
    
    def update_leader_timeout(self) -> bool:
        """Update leader key timeout. Returns True if timed out."""
        if self.leader_pending:
            if time.time() - self.leader_timeout > self.leader_timeout_duration:
                self.leader_pending = False
                return True
        return False
