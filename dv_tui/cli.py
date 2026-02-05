import sys
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
    
    return cli_config


def select_file_interactive() -> Optional[str]:
    """Interactive file selection from ~/share/_tmp/."""
    tmp_dir = Path.home() / "share" / "_tmp"
    
    if not tmp_dir.exists():
        print(f"Directory {tmp_dir} not found")
        return None
    
    json_files = list(tmp_dir.glob("*.json"))
    if not json_files:
        print("No JSON files found in ~/share/_tmp/")
        return None
    
    def select_file(stdscr):
        selected = 0
        curses.curs_set(0)
        stdscr.keypad(True)
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            title = f"{len(json_files)} files in ~/share/_tmp/"
            try:
                stdscr.addstr(0, 0, title, curses.A_BOLD)
            except curses.error:
                pass
            
            visible_items = min(len(json_files), height - 3)
            for i in range(visible_items):
                if i >= len(json_files):
                    break
                
                beautified = beautify_filename(json_files[i].name)
                line_text = beautified
                
                try:
                    if i == selected:
                        stdscr.addstr(i + 2, 2, line_text, curses.A_REVERSE)
                    else:
                        stdscr.addstr(i + 2, 2, line_text)
                except curses.error:
                    pass
            
            key = stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                return None
            elif key == curses.KEY_UP or key == ord('k'):
                selected = max(0, selected - 1)
            elif key == curses.KEY_DOWN or key == ord('j'):
                selected = min(len(json_files) - 1, selected + 1)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                return str(json_files[selected])
    
    selected_file = curses.wrapper(select_file)
    return selected_file


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
    
    # Load inline config from first file and validate it before TUI creation
    inline_config = {}
    files = parsed_args.files
    
    if not files:
        selected_file = select_file_interactive()
        if selected_file is None:
            return 0
        files = [selected_file]
    else:
        # Load and validate inline config from first file
        try:
            data = load_file(files[0])
            from .config import load_config_from_inline_json
            inline_config = load_config_from_inline_json(data)
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    config = load_config(
        config_path=parsed_args.config,
        inline_config=inline_config,
        cli_config=cli_config,
    )
    
    config.single_select = parsed_args.single_select
    
    if parsed_args.stdin_timeout is not None:
        config.stdin_timeout = parsed_args.stdin_timeout
    
    files = parsed_args.files
    
    if not files:
        selected_file = select_file_interactive()
        if selected_file is None:
            return 0
        files = [selected_file]
    
    try:
        tui = TUI(files, single_select=config.single_select, config=config)
        curses.wrapper(tui.run)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
