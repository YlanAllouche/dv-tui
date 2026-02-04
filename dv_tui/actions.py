import subprocess
from pathlib import Path
from typing import Dict, Any, Callable


def scroll_down(selected_index: int, max_index: int) -> int:
    """Scroll down one item."""
    return min(max_index, selected_index + 1)


def scroll_up(selected_index: int) -> int:
    """Scroll up one item."""
    return max(0, selected_index - 1)


def select_item(item: Dict[str, Any], single_select: bool = False) -> bool:
    """
    Select an item and open it in nvim.
    Returns True if should exit (single_select mode).
    """
    file_path = item.get("file", "")
    if not file_path:
        return False
    
    share_path = Path.home() / "share" / file_path
    if not share_path.exists():
        clean_path = file_path.lstrip('/')
        share_path = Path.home() / "share" / clean_path
    
    if not share_path.exists():
        return False
    
    line = item.get("line", 0)
    target_line = line + 1
    socket_path = Path.home() / ".cache" / "nvim" / "share.pipe"
    
    cmd = [
        "nvim",
        "--server", str(socket_path),
        "--remote-expr", f"execute('edit +{target_line} {str(share_path)}')"
    ]
    
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       start_new_session=True, close_fds=True)
    except Exception:
        pass
    
    return single_select


def play_locator(item: Dict[str, Any]) -> None:
    """Run jelly_play_yt on the content of the 'locator' field."""
    locator = item.get("locator", "")
    if not locator:
        return
    
    with open('/tmp/dv_play.log', 'a') as f:
        f.write(f"play_locator called. Locator: '{locator}'\n")
    
    cmd = [str(Path.home() / ".local" / "bin" / "jelly_play_yt"), str(locator)]
    with open('/tmp/dv_play.log', 'a') as f:
        f.write(f"  -> Running: {' '.join(cmd)}\n")
    
    try:
        subprocess.Popen(cmd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       start_new_session=True, close_fds=True)
        with open('/tmp/dv_play.log', 'a') as f:
            f.write(f"  -> Process spawned\n")
    except Exception as e:
        with open('/tmp/dv_play.log', 'a') as f:
            f.write(f"  -> Error: {e}\n")


def copy_to_clipboard(text: str) -> None:
    """Copy text to system clipboard."""
    try:
        subprocess.run(["wl-copy"], input=text.encode(), check=True)
    except Exception:
        try:
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
        except Exception:
            pass


def execute_command(cmd: list[str], async_exec: bool = True) -> None:
    """Execute a shell command."""
    try:
        if async_exec:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           start_new_session=True, close_fds=True)
        else:
            subprocess.run(cmd)
    except Exception:
        pass
