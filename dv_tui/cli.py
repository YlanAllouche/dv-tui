import sys
import curses
from pathlib import Path
from typing import List, Optional

from .core import TUI
from .utils import beautify_filename


def parse_args(args: Optional[List[str]] = None) -> tuple[bool, List[str]]:
    """
    Parse command line arguments.
    
    Returns:
        (single_select, files)
    """
    if args is None:
        args = sys.argv[1:]
    
    single_select = False
    files = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == '-s' or arg == '--single-select':
            single_select = True
        elif arg.startswith('-'):
            i += 1
        else:
            files.append(arg)
        i += 1
    
    return single_select, files


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
    
    Returns:
        Exit code
    """
    single_select, files = parse_args(args)
    
    if not files:
        selected_file = select_file_interactive()
        if selected_file is None:
            return 0
        files = [selected_file]
    
    try:
        tui = TUI(files, single_select)
        curses.wrapper(tui.run)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
