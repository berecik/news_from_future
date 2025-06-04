# Project Utility Scripts

This directory contains utility scripts for managing the project's dependencies.

## Dependency Management Scripts

### `use_wildcard_versions.py`

This script converts all dependency versions in `pyproject.toml` to use wildcard versions (`^x.y.z`).
This is useful during development to allow for compatible dependency updates.

Usage:
```bash
# Direct script usage
python scripts/use_wildcard_versions.py

# Using the Makefile
make wildcards
