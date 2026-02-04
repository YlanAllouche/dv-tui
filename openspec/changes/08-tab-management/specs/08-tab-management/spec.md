## ADDED Requirements
### Requirement: Tab Configuration
The system SHALL support tabs via JSON `tabs` array in `_config`.

#### Scenario: Load tabs from config
- **GIVEN** inline JSON has `_config.tabs: ["file1.json", "file2.json"]`
- **WHEN** dv starts
- **THEN** two tabs are created with data from those files

#### Scenario: CLI file args ignored with tabs config
- **GIVEN** inline JSON has `_config.tabs: ["file1.json"]`
- **WHEN** user runs `dv file2.json`
- **THEN** only file1.json tab is loaded, file2.json is ignored

### Requirement: Custom Tab Field
The system SHALL support custom tab field name via CLI flag.

#### Scenario: Custom tab field name
- **WHEN** user runs `dv --tab-field myTabs`
- **THEN** tabs are loaded from `_config.myTabs` instead of `_config.tabs`

### Requirement: Tab Navigation
The system SHALL provide keybinds for tab navigation.

#### Scenario: Previous tab
- **GIVEN** multiple tabs exist and tab 2 is active
- **WHEN** user presses 'h'
- **THEN** active tab changes to tab 1

#### Scenario: Next tab
- **GIVEN** multiple tabs exist and tab 1 is active
- **WHEN** user presses 'l'
- **THEN** active tab changes to tab 2

### Requirement: Tab Indicator
The system SHALL display active tab indicator.

#### Scenario: Tab display
- **GIVEN** two tabs "file1.json" and "file2.json" with tab1 active
- **WHEN** table is rendered
- **THEN** header shows "file1.json [ACTIVE] | file2.json"

### Requirement: Independent Tab State
Each tab SHALL maintain its own data, selection, and scroll state.

#### Scenario: Independent selection
- **GIVEN** tab1 has row 3 selected and tab2 has row 5 selected
- **WHEN** user switches to tab1
- **THEN** row 3 is selected in tab1

#### Scenario: Independent scroll
- **GIVEN** tab1 has scroll offset 10 and tab2 has scroll offset 0
- **WHEN** user switches to tab1
- **THEN** scroll offset is 10 in tab1

### Requirement: Drill-Down to New Tab
The system SHALL support opening drill-down data in new tab.

#### Scenario: New tab drill-down
- **GIVEN** drill-down config has `new_tab: true`
- **WHEN** user drills into a cell
- **THEN** new tab is created with nested data

#### Scenario: Same tab drill-down (default)
- **GIVEN** drill-down config has `new_tab: false` or not set
- **WHEN** user drills into a cell
- **THEN** current tab view is replaced with nested data
