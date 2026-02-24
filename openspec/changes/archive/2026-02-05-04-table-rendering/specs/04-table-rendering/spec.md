## ADDED Requirements
### Requirement: Dynamic Column Detection
The system SHALL automatically detect columns as the union of all object keys in the data.

#### Scenario: Uniform rows
- **GIVEN** all rows have keys `["name", "age", "city"]`
- **WHEN** data is displayed
- **THEN** columns are `["name", "age", "city"]`

#### Scenario: Rows with different keys
- **GIVEN** row1 has keys `["name", "age"]` and row2 has keys `["name", "city"]`
- **WHEN** data is displayed
- **THEN** columns are `["name", "age", "city"]` with empty cells where missing

### Requirement: Column Filtering
The system SHALL support filtering which columns are displayed via configuration.

#### Scenario: Filter columns
- **GIVEN** data has columns `["name", "age", "city", "country"]`
- **WHEN** config sets `columns: ["name", "city"]`
- **THEN** only columns `["name", "city"]` are displayed

### Requirement: Column Reordering
The system SHALL support reordering columns via configuration.

#### Scenario: Reorder columns
- **GIVEN** data has columns `["name", "age", "city"]`
- **WHEN** config sets `columns: ["city", "name", "age"]`
- **THEN** columns are displayed as `["city", "name", "age"]`

### Requirement: Dynamic Column Widths
The system SHALL calculate column widths based on content.

#### Scenario: Auto-fit columns
- **GIVEN** column "name" has values `["Alice", "Bob"]` and column "description" has values `["A person named Alice", "A person named Bob"]`
- **WHEN** table is rendered
- **THEN** "description" column is wider than "name" column

### Requirement: Tab Display with Counts
The system SHALL display tabs with item counts.

#### Scenario: Single tab
- **GIVEN** data has 5 items
- **WHEN** table is rendered
- **THEN** tab shows filename and count (e.g., "data.json (5)")

#### Scenario: Multiple tabs
- **GIVEN** tab1 has 10 items and tab2 has 5 items
- **WHEN** table is rendered
- **THEN** tabs show respective counts (e.g., "file1.json (10) | file2.json (5)")

### Requirement: Color-Coded Values
The system SHALL support color-coding values based on content.

#### Scenario: Enum colors
- **GIVEN** status column has values "active" and "inactive"
- **WHEN** table is rendered
- **THEN** "active" and "inactive" have different colors

### Requirement: Fuzzy Search Mode
The system SHALL provide fuzzy search for filtering data.

#### Scenario: Enter fuzzy search
- **WHEN** user presses `/`
- **THEN** search mode is activated and user can type query

#### Scenario: Fuzzy search results
- **GIVEN** rows with summaries "Apple Pie" and "Apricot Tart"
- **WHEN** user searches "ap"
- **THEN** both rows are shown with "Apple Pie" ranked higher

### Requirement: Scroll Offset Management
The system SHALL manage scroll offset for large datasets.

#### Scenario: Scroll down
- **GIVEN** 100 rows and only 20 visible
- **WHEN** user presses "j"
- **THEN** view scrolls down one row if selection is not at bottom

#### Scenario: Scroll to selected row
- **GIVEN** 100 rows and row 50 is selected but not visible
- **WHEN** user jumps to row 50
- **THEN** view scrolls to show row 50
