# Quick Test Reference

## Files Created

| File | Purpose |
|------|---------|
| `test_data_projects.json` | Sample project data (3 items) |
| `test_data_tasks.json` | Sample task data (5 items) |
| `test_with_tabs.json` | Config with `_config.tabs` |
| `test_custom_tab_field.json` | Config with `myTabs` field |
| `test_colored_tasks.json` | Tasks with colored status |
| `test_tabs.sh` | Interactive test script |
| `TAB_MANAGEMENT_TESTING.md` | Full testing guide |

## Quick Commands

```bash
# Test 1: Tabs from config
./dv_tui test_with_tabs.json

# Test 2: Custom tab field
./dv_tui --tab-field myTabs test_custom_tab_field.json

# Test 3: Multiple files
./dv_tui test_data_projects.json test_data_tasks.json

# Test 4: Three tabs (from CLI)
./dv_tui test_data_projects.json test_data_tasks.json test_colored_tasks.json
```

## Quick Verification Checklist

- [ ] Tab indicator shows in header
- [ ] `h`/`l` switches between tabs
- [ ] Selection preserved when switching tabs
- [ ] Scroll offset preserved when switching tabs
- [ ] Multiple tabs display with names
- [ ] Tab names show "X items" count
- [ ] `--tab-field` uses custom field name
- [ ] Tabs from config work (ignoring CLI args)
- [ ] Config-only items don't appear as empty rows
- [ ] Tab names not unnecessarily truncated when there's room
