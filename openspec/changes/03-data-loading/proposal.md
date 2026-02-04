# Change: Implement Unified Data Loading System

## Why
Support multiple data sources (JSON, CSV, stdin) with a unified interface for flexibility and extensibility.

## What Changes
- Create `DataLoader` abstract base class
- Implement `JsonDataLoader` for file/inline JSON
- Implement `CsvDataLoader` for basic CSV parsing
- Implement `StdinDataLoader` for piped data with timeout and command support
- Implement data validation and error handling
- Store original data source for refresh capability
- Handle missing columns by union of all keys

## Impact
- Affected specs: None (new capability)
- Affected code: data_loaders.py module
