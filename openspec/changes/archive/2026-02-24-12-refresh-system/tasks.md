## 1. Implementation
- [x] 1.1 Add refresh configuration schema
- [x] 1.2 Implement refresh for file input
- [x] 1.3 Implement refresh for stdin with command
- [x] 1.4 Implement refresh for stdin without command (warning)
- [x] 1.5 Add --refresh CLI flag
- [x] 1.6 Add --no-refresh CLI flag (REMOVED - refresh defaults to OFF)
- [x] 1.7 Add --refresh-interval SECONDS CLI flag
- [x] 1.8 Implement auto-refresh at interval
- [x] 1.9 Implement refresh after trigger (on_trigger)
- [x] 1.10 Preserve selection position after refresh
- [x] 1.11 Preserve scroll position after refresh

## 2. Fixes
- [x] Changed default refresh.enabled from True to False
- [x] Removed --no-refresh flag from CLI
- [x] Changed load_config default for enabled from True to False
