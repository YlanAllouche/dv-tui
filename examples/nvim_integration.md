# Example Configuration: Nvim Integration

This example shows how to implement nvim integration using triggers.

## Basic Nvim Integration

Save this config as `~/.config/dv/nvim_config.json`:

```json
{
  "triggers": {
    "table": {
      "on_select": {
        "command": "nvim --server ~/.cache/nvim/share.pipe --remote-expr \"execute('edit +{line} {file}')\"",
        "async_": true,
        "env": {
          "file": "{file}",
          "line": "{line}"
        }
      }
    }
  }
}
```

## Using with Files

Assuming your data has `file` and `line` fields:

```json
[
  {"file": "src/main.py", "line": 42, "title": "Fix bug"},
  {"file": "src/utils.py", "line": 15, "title": "Add feature"}
]
```

Run with:
```bash
dv --config ~/.config/dv/nvim_config.json data.json
```

## Advanced: Custom Path Base

If your files are relative to a base directory:

```json
{
  "triggers": {
    "table": {
      "on_select": {
        "command": "nvim --server ~/.cache/nvim/share.pipe --remote-expr \"execute('edit +{line} ~/share/{file}')\"",
        "async_": true
      }
    }
  }
}
```

## Cell-Level Triggers

Apply nvim integration to specific cells:

```json
{
  "triggers": {
    "cells": {
      "0:file": {
        "on_enter": {
          "command": "nvim --server ~/.cache/nvim/share.pipe --remote-expr \"execute('edit +{line} {file}')\"",
          "async_": true
        }
      }
    }
  }
}
```

## Key Binding

You can also bind a key to nvim:

```json
{
  "keybinds": {
    "normal": {
      "e": ["enter"]
    }
  },
  "triggers": {
    "table": {
      "on_enter": {
        "command": "nvim --server ~/.cache/nvim/share.pipe --remote-expr \"execute('edit +{line} {file}')\"",
        "async_": true
      }
    }
  }
}
```

Press `e` to open the selected item in nvim.
