# Example Configuration: Play Locator

This example shows how to implement play_locator integration using triggers.

## Basic Play Locator Integration

Save this config as `~/.config/dv/play_locator_config.json`:

```json
{
  "triggers": {
    "table": {
      "on_select": {
        "command": "jelly_play_yt {locator}",
        "async_": true
      }
    }
  }
}
```

## Using with Data

Assuming your data has a `locator` field:

```json
[
  {"locator": "youtube.com/watch?v=dQw4w9WgXcQ", "title": "Video 1"},
  {"locator": "youtube.com/watch?v=abc123", "title": "Video 2"}
]
```

Run with:
```bash
dv --config ~/.config/dv/play_locator_config.json videos.json
```

## Key Binding: Ctrl+P

```json
{
  "keybinds": {
    "normal": {
      "16": ["enter"]
    }
  },
  "triggers": {
    "table": {
      "on_enter": {
        "command": "jelly_play_yt {locator}",
        "async_": true
      }
    }
  }
}
```

Press `Ctrl+P` to play the selected video.

## Key Binding: Leader + p

```json
{
  "triggers": {
    "table": {
      "on_enter": {
        "command": "jelly_play_yt {locator}",
        "async_": true
      }
    }
  }
}
```

Press `;` (leader) then `p` to play the selected video.

## Custom Player

Use a different media player:

```json
{
  "triggers": {
    "table": {
      "on_select": {
        "command": "mpv {locator}",
        "async_": true
      }
    }
  }
}
```

## Cell-Level Triggers

Apply to specific cells only:

```json
{
  "triggers": {
    "cells": {
      "0:locator": {
        "on_enter": {
          "command": "jelly_play_yt {locator}",
          "async_": true
        }
      }
    }
  }
}
```

Navigate to the locator cell and press Enter to play.
