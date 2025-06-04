#!/usr/bin/env python3
"""
Convert all dependency versions in pyproject.toml to use wildcards.

This script reads the pyproject.toml file and replaces specific version constraints
with wildcard versions (^x.y.z) to allow for more flexible dependency updates
during development.

Usage:
    python scripts/use_wildcard_versions.py
"""

import re
import sys
import toml
from pathlib import Path


def convert_to_wildcard_versions(pyproject_path):
    """Convert specific version constraints to wildcard versions."""
    try:
        # Read the pyproject.toml file
        with open(pyproject_path, 'r') as f:
            content = f.read()
            pyproject = toml.loads(content)

        # Process dependencies
        dependencies = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
        for dep, version in dependencies.items():
            if dep == 'python':
                # Skip python version
                continue
                
            if isinstance(version, str):
                # Simple version string
                match = re.match(r'[~^]?(\d+\.\d+\.\d+).*', version)
                if match:
                    major, minor, patch = match.group(1).split('.')
                    dependencies[dep] = f"^{major}.{minor}.{patch}"
            elif isinstance(version, dict) and 'version' in version:
                # Version with extras
                match = re.match(r'[~^]?(\d+\.\d+\.\d+).*', version['version'])
                if match:
                    major, minor, patch = match.group(1).split('.')
                    version['version'] = f"^{major}.{minor}.{patch}"
        
        # Process dev dependencies if they exist
        dev_dependencies = pyproject.get('tool', {}).get('poetry', {}).get('group', {}).get('dev', {}).get('dependencies', {})
        if not dev_dependencies:
            dev_dependencies = pyproject.get('tool', {}).get('poetry', {}).get('dev-dependencies', {})
            
        if dev_dependencies:
            for dep, version in dev_dependencies.items():
                if isinstance(version, str):
                    match = re.match(r'[~^]?(\d+\.\d+\.\d+).*', version)
                    if match:
                        major, minor, patch = match.group(1).split('.')
                        dev_dependencies[dep] = f"^{major}.{minor}.{patch}"
                elif isinstance(version, dict) and 'version' in version:
                    match = re.match(r'[~^]?(\d+\.\d+\.\d+).*', version['version'])
                    if match:
                        major, minor, patch = match.group(1).split('.')
                        version['version'] = f"^{major}.{minor}.{patch}"

        # Write back to pyproject.toml
        with open(pyproject_path, 'w') as f:
            toml.dump(pyproject, f)
        
        print(f"Successfully converted dependency versions to wildcards in {pyproject_path}")
        return True
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Find the pyproject.toml file in the project root
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    
    if not pyproject_path.exists():
        print(f"Error: Could not find pyproject.toml in {project_root}", file=sys.stderr)
        sys.exit(1)
    
    success = convert_to_wildcard_versions(pyproject_path)
    sys.exit(0 if success else 1)
