#!/usr/bin/env python3
"""
Freeze all dependency versions in pyproject.toml to their currently installed versions.

This script uses Poetry's lock file to determine the currently installed versions of
all dependencies and updates the pyproject.toml file to use those specific versions
for production stability.

Usage:
    python scripts/freeze_dependencies.py
"""

import json
import re
import subprocess
import sys
import toml
from pathlib import Path


def get_installed_versions():
    """Get currently installed package versions using Poetry."""
    try:
        # Run poetry show --format json to get all installed packages
        result = subprocess.run(
            ["poetry", "show", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        
        # Create a dictionary mapping package names to their versions
        versions = {}
        for package in packages:
            name = package["name"]
            version = package["version"]
            versions[name] = version
        
        return versions
    
    except subprocess.CalledProcessError as e:
        print(f"Error running poetry show: {e}", file=sys.stderr)
        print(f"Output: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing poetry output: {e}", file=sys.stderr)
        return None


def freeze_dependencies(pyproject_path, installed_versions):
    """Update dependency versions in pyproject.toml to their installed versions."""
    try:
        # Read the pyproject.toml file
        with open(pyproject_path, 'r') as f:
            content = f.read()
            pyproject = toml.loads(content)
        
        # Process dependencies
        dependencies = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
        for dep, version in list(dependencies.items()):
            if dep == 'python':
                # Skip python version
                continue
                
            # Check if we have the installed version
            normalized_dep = dep.lower().replace('-', '_')
            if normalized_dep in installed_versions:
                exact_version = installed_versions[normalized_dep]
                
                if isinstance(version, str):
                    # Simple version string
                    dependencies[dep] = f"=={exact_version}"
                elif isinstance(version, dict) and 'version' in version:
                    # Version with extras
                    version['version'] = f"=={exact_version}"
        
        # Process dev dependencies if they exist
        dev_dependencies = pyproject.get('tool', {}).get('poetry', {}).get('group', {}).get('dev', {}).get('dependencies', {})
        if not dev_dependencies:
            dev_dependencies = pyproject.get('tool', {}).get('poetry', {}).get('dev-dependencies', {})
            
        if dev_dependencies:
            for dep, version in list(dev_dependencies.items()):
                # Check if we have the installed version
                normalized_dep = dep.lower().replace('-', '_')
                if normalized_dep in installed_versions:
                    exact_version = installed_versions[normalized_dep]
                    
                    if isinstance(version, str):
                        # Simple version string
                        dev_dependencies[dep] = f"=={exact_version}"
                    elif isinstance(version, dict) and 'version' in version:
                        # Version with extras
                        version['version'] = f"=={exact_version}"

        # Write back to pyproject.toml
        with open(pyproject_path, 'w') as f:
            toml.dump(pyproject, f)
        
        print(f"Successfully froze dependency versions in {pyproject_path}")
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
    
    # Get currently installed versions
    print("Getting currently installed package versions...")
    installed_versions = get_installed_versions()
    if not installed_versions:
        print("Failed to get installed package versions", file=sys.stderr)
        sys.exit(1)
    
    # Freeze dependencies to their installed versions
    success = freeze_dependencies(pyproject_path, installed_versions)
    sys.exit(0 if success else 1)
