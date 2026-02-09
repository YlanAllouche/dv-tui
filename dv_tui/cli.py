import sys
import json
import os
import tempfile
import argparse
import curses
from pathlib import Path
from typing import List, Optional, Dict, Any

from .core import TUI
from .utils import beautify_filename
from .config import load_config, load_config_from_inline_json
from .data_loaders import load_file


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="dv",
        description="A curses-based TUI for viewing JSON/CSV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dv file.json                    # View JSON file
  dv file1.json file2.json        # Multiple files as tabs
  dv -s file.json                 # Single-select mode
  dv --config myconfig.json       # Use custom config
  dv --columns "name,status"       # Filter columns
  dv --stdin-timeout 60           # Read from stdin with 60s timeout
  dv -c "query.sh"                 # Use command for data (with refresh)
        """
    )
    
    parser.add_argument(
        "files",
        nargs="*",
        help="JSON/CSV files to view (if no files, prompt from ~/share/_tmp/)"
    )
    
    parser.add_argument(
        "-s", "--single-select",
        action="store_true",
        help="Exit after selecting an item"
    )
    
    parser.add_argument(
        "-c", "--command",
        type=str,
        default=None,
        help="Command to generate data (used for refresh)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to external config file (default: ~/.config/dv/config.json)"
    )
    
    parser.add_argument(
        "--columns",
        type=str,
        default=None,
        help="Comma-separated list of columns to display (e.g., 'type,status')"
    )
    
    parser.add_argument(
        "--stdin-timeout",
        type=float,
        default=None,
        help="Timeout for stdin input in seconds (default: 30, use 0 for no timeout)"
    )
    
    parser.add_argument(
        "--no-stdin-timeout",
        action="store_true",
        help="Wait indefinitely for stdin input"
    )
    
    parser.add_argument(
        "--tab-name",
        type=str,
        default=None,
        help="Custom name for the tab (default: filename or source type)"
    )
    
    parser.add_argument(
        "--delimiter",
        type=str,
        default=',',
        help="Delimiter for CSV files (default: ',')"
    )
    
    parser.add_argument(
        "--refresh",
        action="store_true",
        default=None,
        help="Enable auto-refresh"
    )
    
    parser.add_argument(
        "--no-refresh",
        action="store_true",
        dest="no_refresh",
        help="Disable auto-refresh"
    )
    
    parser.add_argument(
        "--refresh-interval",
        type=float,
        default=None,
        help="Auto-refresh interval in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--bind",
        type=str,
        action="append",
        default=None,
        help="Add or override a keybind (format: 'key:action' or 'mode:key:action')"
    )
    
    parser.add_argument(
        "--unbind",
        type=str,
        action="append",
        default=None,
        help="Remove a keybind (format: 'key' or 'mode:key')"
    )
    
    parser.add_argument(
        "--tab-field",
        type=str,
        default="_config.tabs",
        help="Custom field name for tabs in JSON config (default: '_config.tabs')"
    )
    
    return parser.parse_args(args)


def get_cli_config(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Convert CLI arguments to config dictionary.
    
    Args:
        args: Parsed CLI arguments
        
    Returns:
        Config dictionary for merging
    """
    cli_config = {}
    
    if args.columns:
        cli_config["columns"] = [c.strip() for c in args.columns.split(",")]
    
    if args.stdin_timeout is not None:
        cli_config["stdin_timeout"] = args.stdin_timeout
    elif args.no_stdin_timeout:
        cli_config["stdin_timeout"] = 0
    
    refresh_config = {}
    if args.refresh:
        refresh_config["enabled"] = True
    elif args.no_refresh:
        refresh_config["enabled"] = False
    
    if args.refresh_interval is not None:
        refresh_config["interval"] = args.refresh_interval
    
    if refresh_config:
        cli_config["refresh"] = refresh_config
    
    if args.command:
        if "refresh" not in cli_config:
            cli_config["refresh"] = {}
        cli_config["refresh"]["command"] = args.command
    
    if args.delimiter != ',':
        cli_config["delimiter"] = args.delimiter
    
    if args.tab_name:
        cli_config["tab_name"] = args.tab_name
    
    if args.bind:
        binds = []
        for bind in args.bind:
            parts = bind.split(":")
            if len(parts) == 2:
                binds.append({"key": parts[0], "action": parts[1], "mode": "normal"})
            elif len(parts) == 3:
                binds.append({"key": parts[1], "action": parts[2], "mode": parts[0]})
        if binds:
            cli_config["binds"] = binds
    
    if args.unbind:
        unbinds = []
        for unbind in args.unbind:
            parts = unbind.split(":")
            if len(parts) == 1:
                unbinds.append({"key": parts[0], "mode": "normal"})
            elif len(parts) == 2:
                unbinds.append({"key": parts[1], "mode": parts[0]})
        if unbinds:
            cli_config["unbinds"] = unbinds
    
    cli_config["tab_field"] = args.tab_field
    
    return cli_config





def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
    
    Returns:
        Exit code
    """
    parsed_args = parse_args(args)
    
    cli_config = get_cli_config(parsed_args)
    
    tab_field = cli_config.get("tab_field", "_config.tabs")
    
    # Load inline config from first file and validate it before TUI creation
    inline_config = {}
    files = parsed_args.files
    tab_field = cli_config.get("tab_field", "_config.tabs")
    
    if not files:
        print("Error: No input file provided", file=sys.stderr)
        print("Usage: dv <file.json>", file=sys.stderr)
        return 1
    
    # Load and validate inline config from first file
    # Note: File descriptors from process substitution (<(...)) can only be read once,
    # so we skip inline config loading for FD paths and let the TUI handle them
    inline_config = {}
    is_fd_path = (files[0].startswith('/dev/fd/') or
                  files[0].startswith('/proc/self/fd/') or
                  (files[0].startswith('/proc/') and '/fd/' in files[0]))
    
    if not is_fd_path:
        try:
            from .config import load_config_from_inline_json_file
            inline_config = load_config_from_inline_json_file(files[0])
            
            # Check if tabs are defined in config
            if inline_config and tab_field in inline_config:
                tabs_config = inline_config[tab_field]
                if isinstance(tabs_config, list) and tabs_config:
                    # Use tabs from config, ignoring CLI file args
                    files = tabs_config
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    config = load_config(
        config_path=parsed_args.config,
        inline_config=inline_config,
        cli_config=cli_config,
    )
    
    config.single_select = parsed_args.single_select
    
    if parsed_args.stdin_timeout is not None:
        config.stdin_timeout = parsed_args.stdin_timeout
    
    try:
        tui = TUI(files, single_select=config.single_select, config=config, tab_field=tab_field)
        
        # For single_select mode, create a temp file for output
        # This bypasses curses stdout interference
        output_file = None
        if config.single_select:
            output_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            tui.output_file = output_file.name
            output_file.close()
        
        # Manually initialize and run curses
        def run_tui(stdscr):
            try:
                return tui.run(stdscr)
            except KeyboardInterrupt:
                tui.cleanup_curses()
                return None
        
        selected_output = None
        
        # Try to manually handle curses init to catch errors better
        stdscr = None
        saved_stdout = None
        try:
            # In single_select mode with piped stdout, redirect stdout to /dev/tty
            # so curses can display the TUI on the terminal while output goes to the pipe
            if config.single_select and not sys.stdout.isatty():
                # Save the pipe stdout
                saved_stdout = os.dup(sys.stdout.fileno())
                # Redirect stdout to /dev/tty for curses
                tty_fd = os.open('/dev/tty', os.O_WRONLY)
                os.dup2(tty_fd, sys.stdout.fileno())
                os.close(tty_fd)
            
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
            # Call run_tUI directly
            selected_output = run_tui(stdscr)
            
        except curses.error:
            pass
        finally:
            # Before curses cleanup, redirect stdout to /dev/null to prevent
            # escape sequences from going to the pipe (if stdout was piped)
            if saved_stdout is not None:
                devnull_fd = os.open(os.devnull, os.O_WRONLY)
                os.dup2(devnull_fd, sys.stdout.fileno())
            
            # Always cleanup curses
            if stdscr is not None:
                try:
                    stdscr.keypad(False)
                    curses.echo()
                    curses.nocbreak()
                    curses.endwin()
                except curses.error:
                    pass
            
            # Close devnull fd and restore stdout to the pipe
            if saved_stdout is not None:
                os.close(devnull_fd)
                os.dup2(saved_stdout, sys.stdout.fileno())
                os.close(saved_stdout)
        
        # For single_select mode, read output from file
        if config.single_select and output_file:
            try:
                with open(output_file.name, 'r') as f:
                    content = f.read().strip()
                    if content:
                        print(content)
            except FileNotFoundError:
                pass
            finally:
                # Cleanup temp file
                try:
                    os.unlink(output_file.name)
                except:
                    pass
        
        return 0
    except BrokenPipeError:
        # Silently handle broken pipe (when piping to jq/other commands)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
