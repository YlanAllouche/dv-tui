#!/bin/bash

# Example trigger script that logs selections to a file
echo "[$(date)] Selected:" >> /tmp/dv-tui-triggers.log
echo "  Index: $DV_SELECTED_INDEX" >> /tmp/dv-tui-triggers.log
echo "  Column: $DV_SELECTED_COLUMN" >> /tmp/dv-tui-triggers.log
echo "  Cell: $DV_SELECTED_CELL" >> /tmp/dv-tui-triggers.log
echo "  Row: $DV_SELECTED_ROW" >> /tmp/dv-tui-triggers.log
echo "---" >> /tmp/dv-tui-triggers.log
