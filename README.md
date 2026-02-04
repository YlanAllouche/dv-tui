# dv-tui

Terminal UI for browsing dataview queries with neovim triggers, fuzzy search, and media playback.


*(Example screenshot with data from [personal-share-example](https://github.com/YlanAllouche/personal-share-example) as displayed in this [dashboard](https://ylanallouche.github.io/dashboard-md/) as well)*
![screenshot](./screen1.png)

> 💡 **Universalization in progress:** This tool is currently idiosyncratic, but see the `initial-universalizing-effort` branch for ongoing work to generalize it for broader use cases.

## Features

- **Multi-tab browsing** - Load multiple JSON files as tabs
- **Vim keybindings** - Navigate with j/k, h/l for tabs
- **Fuzzy search** - Real-time filtering with smart character-distance scoring
- **Neovim integration** - Opens files at specified line numbers via remote server
- **Auto-reload** - Detects and reloads modified JSON files (if not using single-select)
- **Media playback** - Launches `jelly_play_yt` via "locator" field (Ctrl+P or ;p)
- **Color-coded display** - Dynamic color cycling for statuses; special colors for "focus", "active", and dates
- **Type handling** - Supports string types ("work", "study") and integer durations (shown as minutes)
- **Smart sanitization** - Cleans control characters and truncates long strings
- **Tab indicators** - Shows item counts; search mode shows filtered vs. total count
- **Leader key shortcuts** - Semicolon (`;`) as leader for extended commands
- **Three display modes** - Normal, search, and single-select (`-s` flag)

## Usage

```bash
dv                          # Interactive selection from ~/share/_tmp/
dv file.json                # Open specific file
dv file1.json file2.json    # Multiple files as tabs
dv -s file.json             # Single-select mode (exit after trigerring)
```

or in tmux as a popup window

```bash

bind-key e run-shell "tmux display-popup -w 90% -h 80%  -E ~/.local/bin/dv -s ~/share/_tmp/query1.json ~/share/_tmp/query2.json"
```

## Installation

```bash
cp dv.py ~/.local/bin/dv # or whereever in your PATH

```

## JSON Structure

Expected array of objects with optional fields:

```json
[
  {
    "type": "work",           // string or int (duration in seconds, shown as minutes)
    "status": "active",       // colors: "focus" (magenta), "active" (green), dates (yellow), or custom
    "summary": "Description", // used for search and display
    "file": "path/to/file",   // path relative to ~/share/ for nvim
    "line": 42,               // line number (0-indexed, displayed as line+1)
    "locator": "url_or_id"    // passed to jelly_play_yt
  }
]
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `h` / `←` | Previous tab |
| `l` / `→` | Next tab |
| `Enter` | Open in neovim |
| `Ctrl+P` / `;p` | Play media |
| `/` | Enter search mode |
| `Tab` / `↓` | Next result (search mode) |
| `Shift+Tab` / `↑` | Previous result (search mode) |
| `Esc` | Exit search (restores position) |
| `Backspace` | Delete search character |
| `q` | Quit |


## Notes

Highly idiosyncratic—tailored to Dataview-based personal knowledge management. Assumes: files relative to `~/share/`, neovim with remote server at `~/.cache/nvim/share.pipe`, and `jelly_play_yt` at `~/.local/bin/`.
