#!/bin/bash

# Example trigger script that opens the selected task in a text editor
if [ -z "$DV_SELECTED_CELL" ]; then
    echo "No cell selected"
    exit 1
fi

echo "Task Details:"
echo "  Index: $DV_SELECTED_INDEX"
echo "  Column: $DV_SELECTED_COLUMN"
echo "  Value: $DV_SELECTED_CELL"
echo "  Full Row: $DV_SELECTED_ROW"

# You could add more complex logic here, like:
# - Opening a specific file based on the task ID
# - Making API calls to update task status
# - Sending notifications
# - etc.
