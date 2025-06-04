#!/usr/bin/env python3
"""
Dependency Management Script

This script provides functionality to toggle between wildcard and frozen dependency versions
in a Poetry project's pyproject.toml file.

Usage:
    python scripts/manage_deps.py freeze    # Freeze dependencies to current installed versions
    python scripts/manage_deps.py wildcard  # Convert dependencies to wildcard versions
"""

import os
import sys
import subprocess
import re
from pathlib import Path
import argparse

try:
    import toml
except ImportError:
    print("Error: The 'toml' module is not installed.")
    print("Please install it using: pip install toml")
    print("Or update your poetry dependencies with: poetry add toml")
    sys.exit(1)

def get_project_root():
    """Get the project root directory."""
    script_path = Path(os.path.realpath(__file__))
    return script_path.parent.parent

def load_pyproject_toml(project_root):
    """Load the pyproject.toml file."""
    pyproject_path = project_root / 'pyproject.toml'
    
    if not pyproject_path.exists():
        print(f"Error: pyproject.toml not found at {pyproject_path}")
        sys.exit(1)
    
    return pyproject_path, toml.load(pyproject_path)

def save_pyproject_toml(pyproject_path, config):
    """Save the pyproject.toml file."""
    with open(pyproject_path, 'w') as f:
        toml.dump(config, f)
    print(f"Updated {pyproject_path}")

def get_installed_versions():
    """Get currently installed package versions using Poetry."""
    try:
        result = subprocess.run(
            ["poetry", "show", "--no-ansi"], 
            capture_output=True, 
            text=True,
            check=True
        )
        packages = {}
        
        for line in result.stdout.splitlines():
            match = re.match(r'^(\S+)\s+(\S+)', line)
            if match:
                name, version = match.groups()
                packages[name] = version
        
        return packages
    except subprocess.CalledProcessError as e:
        print(f"Error running poetry show: {e}")
        print(e.stderr)
        sys.exit(1)

def freeze_dependencies(config, installed_versions):
    """Freeze dependencies to specific versions."""
    modified = False
    
    # Handle main dependencies
    for name in config.get('tool', {}).get('poetry', {}).get('dependencies', {}):
        if name == 'python':
            # Keep Python as a specific version range
            if config['tool']['poetry']['dependencies']['python'] != ">=3.10,<3.14":
                config['tool']['poetry']['dependencies']['python'] = ">=3.10,<3.14"
                modified = True
            
            # Make sure build-system has proper Python requirement
            if 'build-system' in config and 'requires' in config['build-system']:
                if "python>=3.10,<3.14" not in config['build-system']['requires']:
                    if "poetry-core>=1.0.0" not in config['build-system']['requires']:
                        config['build-system']['requires'] = ["poetry-core>=1.0.0", "python>=3.10,<3.14"]
                    else:
                        config['build-system']['requires'].append("python>=3.10,<3.14")
                    modified = True
            continue
            
        if name in installed_versions:
            dep = config['tool']['poetry']['dependencies'][name]
            version = installed_versions[name]
            
            if isinstance(dep, dict) and 'version' in dep:
                if dep['version'] != f"^{version}":
                    dep['version'] = f"^{version}"
                    modified = True
            else:
                config['tool']['poetry']['dependencies'][name] = f"^{version}"
                modified = True
    
    # Handle dev dependencies
    for name in config.get('tool', {}).get('poetry', {}).get('group', {}).get('dev', {}).get('dependencies', {}):
        if name in installed_versions:
            version = installed_versions[name]
            if config['tool']['poetry']['group']['dev']['dependencies'][name] != f"^{version}":
                config['tool']['poetry']['group']['dev']['dependencies'][name] = f"^{version}"
                modified = True
    
    return modified

def set_wildcard_dependencies(config):
    """Set all dependencies to use wildcard versions."""
    modified = False
    
    # Handle main dependencies
    for name in list(config.get('tool', {}).get('poetry', {}).get('dependencies', {})):
        if name == 'python':
            # Set Python to use a specific version range
            if config['tool']['poetry']['dependencies']['python'] != ">=3.10,<3.14":
                config['tool']['poetry']['dependencies']['python'] = ">=3.10,<3.14"
                modified = True
            continue
            
        dep = config['tool']['poetry']['dependencies'][name]
        if isinstance(dep, dict) and 'version' in dep:
            if dep['version'] != "*":
                dep['version'] = "*"
                modified = True
        elif dep != "*":
            config['tool']['poetry']['dependencies'][name] = "*"
            modified = True
    
    # Make sure build-system has proper Python requirement
    if 'build-system' in config and 'requires' in config['build-system']:
        if "python>=3.10,<3.14" not in config['build-system']['requires']:
            if "poetry-core>=1.0.0" not in config['build-system']['requires']:
                config['build-system']['requires'] = ["poetry-core>=1.0.0", "python>=3.10,<3.14"]
            else:
                config['build-system']['requires'].append("python>=3.10,<3.14")
            modified = True
    
    # Handle dev dependencies
    for name in list(config.get('tool', {}).get('poetry', {}).get('group', {}).get('dev', {}).get('dependencies', {})):
        if config['tool']['poetry']['group']['dev']['dependencies'][name] != "*":
            config['tool']['poetry']['group']['dev']['dependencies'][name] = "*"
            modified = True
    
    return modified

def main():
    parser = argparse.ArgumentParser(description="Manage Poetry dependency versions")
    parser.add_argument('action', choices=['freeze', 'wildcard'], 
                      help="Action to perform: 'freeze' to pin dependencies to current versions, "
                           "'wildcard' to use wildcard (*) versions")
    
    args = parser.parse_args()
    
    project_root = get_project_root()
    pyproject_path, config = load_pyproject_toml(project_root)
    
    if args.action == 'freeze':
        print("Freezing dependencies to currently installed versions...")
        installed_versions = get_installed_versions()
        modified = freeze_dependencies(config, installed_versions)
        if modified:
            save_pyproject_toml(pyproject_path, config)
            print("Dependencies have been frozen to specific versions.")
        else:
            print("Dependencies were already frozen or not found in the installed packages.")
    
    elif args.action == 'wildcard':
        print("Converting dependencies to wildcard versions...")
        modified = set_wildcard_dependencies(config)
        if modified:
            save_pyproject_toml(pyproject_path, config)
            print("Dependencies have been set to wildcard (*) versions.")
        else:
            print("Dependencies were already using wildcard versions.")

if __name__ == "__main__":
    main()
