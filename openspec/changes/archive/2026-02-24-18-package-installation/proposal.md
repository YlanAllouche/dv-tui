# Change: Set Up Package Installation and Distribution

## Why
Create proper Python package structure for installation and distribution via pip.

## What Changes
- Create pyproject.toml with package metadata
- Add dependencies
- Configure CLI entry point
- Add LICENSE file
- Create MANIFEST.in if needed
- Test installation with pip install -e .
- Add version to dv_tui/__init__.py
- Create CHANGELOG.md
- Verify all tests pass
- Document dependencies

## Impact
- Affected specs: None (new capability)
- Affected code: pyproject.toml, LICENSE, CHANGELOG.md, dv_tui/__init__.py
