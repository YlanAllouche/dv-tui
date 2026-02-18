import time
import curses
import json
from typing import Dict, Any, List, Callable, Optional, Tuple, TYPE_CHECKING, Union, Set
from enum import Enum
from .triggers import TriggerManager

if TYPE_CHECKING:
    from .config import Config


class Mode(Enum):
    """TUI modes."""
    NORMAL = "normal"
    SEARCH = "search"
    NAVIGATE = "navigate"


class KeybindManager:
    """Manages mode-based keybinds with layering support."""
    
    def __init__(self, config: Optional["Config"] = None):
        """Initialize KeybindManager with default keybinds and optional config."""
        self.mode = Mode.NORMAL
        
        self.defaults: Dict[str, Dict[str, Any]] = {
            "normal": {
                "leader": ord(';'),
                "quit": [ord('q'), ord('Q')],
                "down": [ord('j'), ord('J'), 258],
                "up": [ord('k'), ord('K'), 259],
                "left": [ord('h'), ord('H'), 260],
                "right": [ord('l'), ord('L'), 261],
                "search": ord('/'),
                "enter": [ord('\n'), 10],
                "escape": 27,
                "backspace": [263, 127],
                "toggle_mode": ord('c'),
            },
            "search": {
                "enter": [ord('\n'), 10],
                "escape": 27,
                "backspace": [263, 127],
                "tab": 9,
                "shift_tab": 353,
            },
            "cell": {
                "leader": ord(';'),
                "quit": [ord('q'), ord('Q')],
                "down": [ord('j'), ord('J'), 258],
                "up": [ord('k'), ord('K'), 259],
                "left": [ord('h'), ord('H'), 260],
                "right": [ord('l'), ord('L'), 261],
                "search": ord('/'),
                "enter": [ord('\n'), 10],
                "escape": 27,
                "backspace": [263, 127],
                "toggle_mode": ord('c'),
            }
        }
        
        self.cli_binds: Dict[str, Dict[str, Any]] = {}
        self.inline_binds: Dict[str, Dict[str, Any]] = {}
        self.file_binds: Dict[str, Dict[str, Any]] = {}
        self.unbinds: Dict[str, Set[Union[int, str]]] = {"normal": set(), "search": set(), "cell": set()}
        
        if config:
            self.load_config(config)
    
    def load_config(self, config: "Config") -> None:
        """Load keybind configuration from Config object."""
        if hasattr(config, 'keybinds'):
            keybinds = config.keybinds
            
            if isinstance(keybinds, dict):
                for mode_name in ["normal", "search", "cell"]:
                    if mode_name in keybinds and isinstance(keybinds[mode_name], dict):
                        self.file_binds[mode_name] = keybinds[mode_name]
                    elif mode_name == "normal" and isinstance(keybinds, dict):
                        self.file_binds[mode_name] = keybinds
    
    def set_mode(self, mode: Mode) -> None:
        """Switch to the specified mode."""
        self.mode = mode
    
    def get_mode(self) -> Mode:
        """Get current mode."""
        return self.mode
    
    def add_bind(self, keybind: str, action: str, mode: str = "normal") -> None:
        """Add a keybind at the CLI layer."""
        key = self._parse_key(keybind)
        if mode not in self.cli_binds:
            self.cli_binds[mode] = {}
        self.cli_binds[mode][action] = key
    
    def unbind(self, keybind: str, mode: str = "normal") -> None:
        """Unbind a key at all layers."""
        key = self._parse_key(keybind)
        self.unbinds[mode].add(key)
    
    def _parse_key(self, keybind: str) -> Union[int, str]:
        """Parse a keybind string to an int or keep as string."""
        if len(keybind) == 1:
            return ord(keybind)
        try:
            return int(keybind)
        except ValueError:
            return keybind
    
    def get_keybind(self, action: str) -> Union[int, List[int]]:
        """Get keybind for an action with precedence: CLI > inline > file > defaults."""
        mode_name = self.mode.value
        
        if mode_name in self.unbinds:
            for key in self.unbinds[mode_name]:
                keybind = self._get_action_key_from_layers(action, mode_name)
                if key == keybind or (isinstance(keybind, list) and key in keybind):
                    return None
        
        return self._get_action_key_from_layers(action, mode_name)
    
    def _get_action_key_from_layers(self, action: str, mode: str) -> Union[int, List[int]]:
        """Get action key from layers in order: CLI > inline > file > defaults."""
        for layer in [self.cli_binds, self.inline_binds, self.file_binds, self.defaults]:
            if mode in layer and action in layer[mode]:
                return layer[mode][action]
        
        return None
    
    def get_all_keybinds(self) -> Dict[str, Any]:
        """Get all keybinds for current mode with full precedence applied."""
        mode_name = self.mode.value
        result: Dict[str, Any] = {}
        
        for layer in [self.defaults, self.file_binds, self.inline_binds, self.cli_binds]:
            if mode_name in layer:
                result.update(layer[mode_name])
        
        for key in self.unbinds.get(mode_name, set()):
            result = {k: v for k, v in result.items() if v != key and not (isinstance(v, list) and key in v)}
        
        return result
    
    def is_action_bound(self, action: str) -> bool:
        """Check if an action has a bound key."""
        return self.get_keybind(action) is not None


class KeyHandler:
    """Handle keybinds and mode management."""
    
    def __init__(self, config: Optional["Config"] = None):
        self.keybind_manager = KeybindManager(config)
        self.mode = self.keybind_manager.get_mode()
        self.leader_pending = False
        self.leader_timeout = 0
        self.leader_key = ord(';')
        self.leader_timeout_duration = 0.5
        
        self.search_query = ""
        self.filtered_indices: List[int] = []
        self.search_selected_index = 0
        self.pre_search_selected_index = 0
        self.pre_search_scroll_offset = 0
        
        self.custom_handlers: Dict[int, Callable] = {}
        self.trigger_manager = TriggerManager()
        
        if config:
            self.load_config(config)
    
    def load_config(self, config: "Config") -> None:
        """Load keybind and trigger configuration."""
        self.keybind_manager.load_config(config)
        
        if hasattr(config, 'binds') and config.binds:
            for bind in config.binds:
                key = bind.get("key")
                action = bind.get("action")
                mode = bind.get("mode", "normal")
                if key and action:
                    self.keybind_manager.add_bind(key, action, mode)
        
        if hasattr(config, 'unbinds') and config.unbinds:
            for unbind in config.unbinds:
                key = unbind.get("key")
                mode = unbind.get("mode", "normal")
                if key:
                    self.keybind_manager.unbind(key, mode)
        
        keybinds = self.keybind_manager.get_all_keybinds()
        leader = keybinds.get("leader", ord(';'))
        self.leader_key = leader if isinstance(leader, int) else ord(leader)
        
        self._load_triggers(config)
    
    def _normalize_trigger(self, trigger: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize trigger to object format (convert string to {command: string})."""
        if isinstance(trigger, str):
            return {"command": trigger, "async_": True}
        return trigger
    
    def _load_triggers(self, config: "Config") -> None:
        """Load triggers from configuration."""
        if not hasattr(config, 'triggers') or not config.triggers:
            return
        
        triggers = config.triggers
        
        if triggers.table:
            normalized_table = {
                k: self._normalize_trigger(v)
                for k, v in [
                    ("on_enter", triggers.table.on_enter),
                    ("on_select", triggers.table.on_select),
                    ("on_navigate_row", triggers.table.on_navigate_row),
                    ("on_navigate_cell", triggers.table.on_navigate_cell),
                    ("on_startup", triggers.table.on_startup),
                    ("on_drilldown", triggers.table.on_drilldown),
                    ("on_backup", triggers.table.on_backup)
                ]
                if v is not None
            }
            self.trigger_manager.set_table_triggers(normalized_table)

        if triggers.rows:
            for row_key, row_triggers in triggers.rows.items():
                try:
                    row_index = int(row_key)
                    normalized_row = {
                        k: self._normalize_trigger(v)
                        for k, v in [
                            ("on_enter", row_triggers.on_enter),
                            ("on_select", row_triggers.on_select),
                            ("on_navigate_row", row_triggers.on_navigate_row),
                            ("on_navigate_cell", row_triggers.on_navigate_cell),
                            ("on_startup", row_triggers.on_startup),
                            ("on_drilldown", row_triggers.on_drilldown),
                            ("on_backup", row_triggers.on_backup)
                        ]
                        if v is not None
                    }
                    self.trigger_manager.set_row_triggers(row_index, normalized_row)
                except ValueError:
                    pass

        if triggers.cells:
            for cell_key, cell_triggers in triggers.cells.items():
                if ":" in cell_key:
                    parts = cell_key.split(":")
                    try:
                        row_index = int(parts[0])
                        column = parts[1]
                        normalized_cell = {
                            k: self._normalize_trigger(v)
                            for k, v in [
                                ("on_enter", cell_triggers.on_enter),
                                ("on_select", cell_triggers.on_select),
                                ("on_navigate_row", cell_triggers.on_navigate_row),
                                ("on_navigate_cell", cell_triggers.on_navigate_cell),
                                ("on_startup", cell_triggers.on_startup),
                                ("on_drilldown", cell_triggers.on_drilldown),
                                ("on_backup", cell_triggers.on_backup)
                            ]
                            if v is not None
                        }
                        self.trigger_manager.set_cell_triggers(row_index, column, normalized_cell)
                    except ValueError:
                        pass
    
    def is_quit_key(self, key: int) -> bool:
        """Check if key is a quit key."""
        quit_keys = self.keybind_manager.get_keybind("quit")
        if quit_keys is None:
            quit_keys = [ord('q'), ord('Q')]
        return key in (quit_keys if isinstance(quit_keys, list) else [quit_keys])
    
    def is_down_key(self, key: int) -> bool:
        """Check if key is a down key."""
        down_keys = self.keybind_manager.get_keybind("down")
        if down_keys is None:
            down_keys = [ord('j'), ord('J'), 258]
        return key in (down_keys if isinstance(down_keys, list) else [down_keys])
    
    def is_up_key(self, key: int) -> bool:
        """Check if key is an up key."""
        up_keys = self.keybind_manager.get_keybind("up")
        if up_keys is None:
            up_keys = [ord('k'), ord('K'), 259]
        return key in (up_keys if isinstance(up_keys, list) else [up_keys])
    
    def is_left_key(self, key: int) -> bool:
        """Check if key is a left key."""
        left_keys = self.keybind_manager.get_keybind("left")
        if left_keys is None:
            left_keys = [ord('h'), ord('H'), 260]
        return key in (left_keys if isinstance(left_keys, list) else [left_keys])
    
    def is_right_key(self, key: int) -> bool:
        """Check if key is a right key."""
        right_keys = self.keybind_manager.get_keybind("right")
        if right_keys is None:
            right_keys = [ord('l'), ord('L'), 261]
        return key in (right_keys if isinstance(right_keys, list) else [right_keys])
    
    def is_search_key(self, key: int) -> bool:
        """Check if key starts search mode."""
        search_key = self.keybind_manager.get_keybind("search")
        if search_key is None:
            search_key = ord('/')
        return key == (search_key if isinstance(search_key, int) else search_key)
    
    def is_enter_key(self, key: int) -> bool:
        """Check if key is enter."""
        enter_keys = self.keybind_manager.get_keybind("enter")
        if enter_keys is None:
            enter_keys = [ord('\n'), 10]
        return key in (enter_keys if isinstance(enter_keys, list) else [enter_keys])
    
    def is_escape_key(self, key: int) -> bool:
        """Check if key is escape."""
        escape_key = self.keybind_manager.get_keybind("escape")
        if escape_key is None:
            escape_key = 27
        return key == (escape_key if isinstance(escape_key, int) else escape_key)
    
    def is_backspace_key(self, key: int) -> bool:
        """Check if key is backspace."""
        backspace_keys = self.keybind_manager.get_keybind("backspace")
        if backspace_keys is None:
            backspace_keys = [263, 127]
        return key in (backspace_keys if isinstance(backspace_keys, list) else [backspace_keys])
    
    def is_toggle_mode_key(self, key: int) -> bool:
        """Check if key toggles selection mode."""
        toggle_key = self.keybind_manager.get_keybind("toggle_mode")
        if toggle_key is None:
            toggle_key = ord('c')
        return key == (toggle_key if isinstance(toggle_key, int) else toggle_key)
    
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
            old_index = table.selected_index
            table.scroll_down()
            if table.selected_index != old_index:
                self._execute_trigger_event("on_navigate_row", table)
        elif self.is_up_key(key):
            old_index = table.selected_index
            table.scroll_up()
            if table.selected_index != old_index:
                self._execute_trigger_event("on_navigate_row", table)
        elif self.is_left_key(key):
            if table.selection_mode == 'cell':
                old_column = table.selected_column
                table.selected_column = max(0, table.selected_column - 1)
                if table.selected_column != old_column:
                    self._execute_trigger_event("on_navigate_cell", table)
        elif self.is_right_key(key):
            if table.selection_mode == 'cell':
                old_column = table.selected_column
                table.selected_column = min(len(table.columns) - 1, table.selected_column + 1)
                if table.selected_column != old_column:
                    self._execute_trigger_event("on_navigate_cell", table)
        elif self.is_enter_key(key):
            self._execute_trigger_event("on_enter", table, async_exec=False)
            self._execute_trigger_event("on_select", table)
            if table.selection_mode == 'cell':
                cell_value = table.data[table.selected_index].get(table.columns[table.selected_column])
                if table.is_drillable(table.selected_index, table.selected_column):
                    return False, {
                        "value": cell_value,
                        "row": table.selected_index,
                        "column": table.columns[table.selected_column],
                        "column_index": table.selected_column,
                        "item": table.selected_item,
                        "drill_down": True
                    }
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
            selected_item = None
            if self.filtered_indices:
                table.selected_index = self.filtered_indices[self.search_selected_index]
                selected_item = table.selected_item
            self.exit_search_mode(table)
            return False, selected_item
        
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
        self.keybind_manager.set_mode(Mode.SEARCH)
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
        self.keybind_manager.set_mode(Mode.NORMAL)
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
    
    def _build_trigger_context(self, table, column: Optional[str] = None) -> Dict[str, Any]:
        """Build context dictionary for trigger execution."""
        context = {
            "selected_index": table.selected_index,
            "selected_column": None,
            "selected_row": table.selected_item,
            "selected_cell": None,
            # Dataset information available to all triggers
            "DV_DATASET_SIZE": len(table.data),
            "DV_DATA_SOURCE": getattr(table, 'data_source', ''),
            # Level information (if available)
            "DV_LEVEL_NAME": getattr(table, 'level_name', ''),
            "DV_DEPTH": getattr(table, 'depth', 0),
        }
        
        if table.selection_mode == 'cell' and table.selected_column < len(table.columns):
            col_name = table.columns[table.selected_column]
            context["selected_cell"] = table.selected_item.get(col_name)
            context["selected_column"] = col_name
        
        return context
    
    def _execute_trigger_event(self, event: str, table, async_exec: bool = True) -> None:
        """Execute a trigger event."""
        context = self._build_trigger_context(table)
        self.trigger_manager.execute_trigger_event(event, context, async_exec)

    def trigger_startup_event(self, table, data_source: str, config_file: Optional[str] = None) -> None:
        """Execute startup trigger event."""
        context = self._build_trigger_context(table)
        context["DV_DATA_SOURCE"] = data_source
        if config_file:
            context["DV_CONFIG_FILE"] = config_file
        self.trigger_manager.execute_trigger_event("on_startup", context, async_exec=True)

    def trigger_drilldown_event(self, table, drill_to_context: Dict[str, Any]) -> None:
        """Execute drilldown trigger event with comprehensive context."""
        context = self._build_trigger_context(table)

        # Map drilldown context to DV_ prefixed variables
        key_mapping = {
            "selected_index": "DRILL_FROM_INDEX",
            "selected_column": "DRILL_FROM_COLUMN",
            "selected_cell": "DRILL_FROM_CELL",
            "level_name": "DRILL_LEVEL_NAME",
            "depth": "DRILL_DEPTH",
            "parent_level_index": "PARENT_LEVEL_INDEX",
            "parent_level_name": "PARENT_LEVEL_NAME",
            "dataset_size": "DATASET_SIZE",
            "data_source": "DRILL_DATA_SOURCE",
        }

        for key, value in drill_to_context.items():
            if key in key_mapping:
                context[f"DV_{key_mapping[key]}"] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)

        self.trigger_manager.execute_trigger_event("on_drilldown", context, async_exec=True)

    def trigger_backup_event(self, table, backup_to_context: Dict[str, Any]) -> None:
        """Execute backup trigger event with comprehensive context."""
        context = self._build_trigger_context(table)

        # Map backup context to DV_ prefixed variables
        key_mapping = {
            "selected_index": "CURRENT_INDEX",
            "selected_column": "CURRENT_COLUMN",
            "selected_cell": "CURRENT_CELL",
            "level_name": "CURRENT_LEVEL_NAME",
            "depth": "CURRENT_DEPTH",
            "dataset_size": "DATASET_SIZE",
            "data_source": "DATA_SOURCE",
            "previous_level_index": "PREVIOUS_LEVEL_INDEX",
            "previous_level_name": "PREVIOUS_LEVEL_NAME",
            "previous_parent_context": "PREVIOUS_PARENT_CONTEXT",
        }

        for key, value in backup_to_context.items():
            if key in key_mapping:
                context[f"DV_{key_mapping[key]}"] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)

        self.trigger_manager.execute_trigger_event("on_backup", context, async_exec=True)
