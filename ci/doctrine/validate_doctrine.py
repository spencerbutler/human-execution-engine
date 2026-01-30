#!/usr/bin/env python3
"""
HEE Doctrine Validation Script

This script validates doctrine files in the blueprints directory.
It checks for:
- Valid YAML syntax
- Required doctrine files
- Basic structure validation
"""

import yaml
import os
import sys
from pathlib import Path


def validate_doctrine():
    """Validate all doctrine files in the blueprints directory."""
    doctrine_dir = Path('blueprints')
    if not doctrine_dir.exists():
        print('ERROR: Doctrine directory not found')
        return False
    
    doctrine_files = list(doctrine_dir.glob('*doctrine*.yml'))
    if not doctrine_files:
        print('ERROR: No doctrine files found')
        return False
    
    print(f'Found {len(doctrine_files)} doctrine files')
    
    for doctrine_file in doctrine_files:
        try:
            with open(doctrine_file, 'r') as f:
                yaml.safe_load(f)
            print(f'✅ {doctrine_file.name}: Valid YAML')
        except Exception as e:
            print(f'❌ {doctrine_file.name}: {e}')
            return False
    
    # Check for required doctrine files
    required = ['hee-doctrine.yml', 'core-tools-doctrine.yml']
    for req in required:
        if not (doctrine_dir / req).exists():
            print(f'❌ Missing required doctrine: {req}')
            return False
    
    print('✅ All doctrine validation passed')
    return True


def main():
    """Main entry point for the validation script."""
    if not validate_doctrine():
        sys.exit(1)
    
    # Additional checks can be added here
    print('✅ Doctrine validation completed successfully')


if __name__ == '__main__':
    main()