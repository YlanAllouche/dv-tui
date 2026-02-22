## ADDED Requirements
### Requirement: Refresh Configuration
The system SHALL support refresh configuration in _config.

#### Scenario: Enable refresh
- **GIVEN** config has `refresh: {"enabled": true}`
- **WHEN** refresh is triggered
- **THEN** data is reloaded from source

#### Scenario: Disable refresh
- **GIVEN** config has `refresh: {"enabled": false}`
- **WHEN** refresh is triggered
- **THEN** no data reload occurs

#### Scenario: Refresh on trigger
- **GIVEN** config has `refresh: {"on_trigger": true}`
- **WHEN** a trigger modifies data
- **THEN** data is automatically refreshed

#### Scenario: Auto-refresh interval
- **GIVEN** config has `refresh: {"interval": 5.0}`
- **WHEN** dv is running
- **THEN** data is refreshed every 5 seconds

#### Scenario: Custom refresh command
- **GIVEN** config has `refresh: {"command": "regenerate.sh"}`
- **WHEN** refresh is triggered
- **THEN** regenerate.sh is executed to regenerate data

### Requirement: File Refresh
The system SHALL support refreshing data from file input.

#### Scenario: Reload from file
- **GIVEN** data was loaded from data.json
- **WHEN** refresh is triggered
- **THEN** data is reloaded from data.json

### Requirement: Stdin with Command Refresh
The system SHALL support refreshing stdin data by re-running command.

#### Scenario: Re-run command
- **GIVEN** data was loaded via stdin with `-c "query.sh"`
- **WHEN** refresh is triggered
- **THEN** query.sh is re-executed to regenerate data

### Requirement: Stdin without Command Refresh
The system SHALL warn when attempting to refresh stdin without command.

#### Scenario: Refresh stdin without command warning
- **GIVEN** data was loaded via stdin without `-c` flag
- **WHEN** refresh is triggered
- **THEN** warning message "Cannot refresh piped data without command" is shown

### Requirement: CLI Refresh Flags
The system SHALL support CLI flags for refresh control.

#### Scenario: Enable refresh via CLI
- **WHEN** user runs `dv --refresh`
- **THEN** refresh is enabled

#### Scenario: Disable refresh via CLI
- **WHEN** user runs `dv --no-refresh`
- **THEN** refresh is disabled

#### Scenario: Set refresh interval via CLI
- **WHEN** user runs `dv --refresh-interval 10`
- **THEN** auto-refresh interval is set to 10 seconds

### Requirement: Preserve State After Refresh
The system SHALL preserve selection and scroll position after refresh.

#### Scenario: Preserve selection
- **GIVEN** row 5 is selected
- **WHEN** refresh is triggered
- **THEN** row 5 remains selected after refresh

#### Scenario: Preserve scroll
- **GIVEN** scroll offset is 10
- **WHEN** refresh is triggered
- **THEN** scroll offset remains 10 after refresh

#### Scenario: Selection after data change
- **GIVEN** row 5 is selected and data changes (row 5 removed)
- **WHEN** refresh is triggered
- **THEN** selection moves to nearest available row
