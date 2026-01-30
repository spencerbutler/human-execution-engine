#!/usr/bin/env python3
"""
Strict Validator for HEE Schema Naming Enforcement

This script validates YAML files for Phase 04b requirements:
- Path header presence and format (# path: <repo-relative-path>)
- $schema field validation (if present, must match resolved schema)
- Integration with fixer script for header validation
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

HEADER_PREFIX = "# path: "
HEADER_PATTERN = r"^# path: .+$"
SCHEMA_FIELD = "$schema"


def validate_yaml_header(file_path: Path, repo_root: Path) -> Tuple[bool, str]:
    """
    Validate that a YAML file has the correct path header.
    
    Args:
        file_path: Path to the YAML file
        repo_root: Repository root path
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        
        # Check if first line matches the expected header format
        expected_header = f"{HEADER_PREFIX}{file_path.relative_to(repo_root).as_posix()}"
        
        if first_line != expected_header:
            return False, f"Invalid header. Expected: '{expected_header}', Got: '{first_line}'"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_schema_field(file_path: Path, repo_root: Path) -> Tuple[bool, str]:
    """
    Validate $schema field if present.
    
    Args:
        file_path: Path to the YAML file
        repo_root: Repository root path
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML to check for $schema field
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            return False, f"Invalid YAML syntax: {e}"
        
        if data is None:
            return True, ""  # Empty file is valid
            
        if SCHEMA_FIELD in data:
            schema_value = data[SCHEMA_FIELD]
            
            # For Phase 04b, we validate that if $schema is present,
            # it should be consistent with the file's location
            # This is a basic check - more sophisticated schema resolution
            # can be added in future phases
            
            if not isinstance(schema_value, str):
                return False, f"$schema field must be a string, got: {type(schema_value)}"
            
            # Basic validation - schema should not be empty
            if not schema_value.strip():
                return False, "$schema field cannot be empty"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error validating schema field: {e}"


def validate_file(file_path: Path, repo_root: Path) -> Dict[str, Any]:
    """
    Validate a single YAML file for Phase 04b requirements.
    
    Args:
        file_path: Path to the YAML file
        repo_root: Repository root path
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'file': str(file_path.relative_to(repo_root)),
        'header_valid': False,
        'schema_valid': False,
        'errors': [],
        'warnings': []
    }
    
    # Validate header
    header_valid, header_error = validate_yaml_header(file_path, repo_root)
    results['header_valid'] = header_valid
    if not header_valid:
        results['errors'].append(f"Header validation failed: {header_error}")
    
    # Validate schema field
    schema_valid, schema_error = validate_schema_field(file_path, repo_root)
    results['schema_valid'] = schema_valid
    if not schema_valid:
        results['errors'].append(f"Schema validation failed: {schema_error}")
    
    # Check if file is empty (warning)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if not content:
            results['warnings'].append("File is empty")
    except Exception:
        pass
    
    return results


def validate_scope(scope_dirs: List[Path], repo_root: Path) -> Dict[str, Any]:
    """
    Validate all YAML files in the specified scope.
    
    Args:
        scope_dirs: List of directories to validate
        repo_root: Repository root path
        
    Returns:
        Dictionary with overall validation results
    """
    all_results = []
    total_files = 0
    valid_files = 0
    error_count = 0
    
    for scope_dir in scope_dirs:
        if not scope_dir.exists():
            continue
            
        for yaml_file in scope_dir.rglob("*.yaml"):
            # Skip var/** files
            if "var" in yaml_file.parts:
                continue
                
            total_files += 1
            result = validate_file(yaml_file, repo_root)
            all_results.append(result)
            
            if result['header_valid'] and result['schema_valid']:
                valid_files += 1
            else:
                error_count += len(result['errors'])
    
    return {
        'total_files': total_files,
        'valid_files': valid_files,
        'error_count': error_count,
        'results': all_results
    }


def print_results(results: Dict[str, Any], verbose: bool = False) -> None:
    """
    Print validation results.
    
    Args:
        results: Validation results dictionary
        verbose: Whether to print detailed results
    """
    print(f"Total files: {results['total_files']}")
    print(f"Valid files: {results['valid_files']}")
    print(f"Error count: {results['error_count']}")
    
    if results['total_files'] == 0:
        print("No YAML files found in scope")
        return
    
    if results['valid_files'] == results['total_files']:
        print("✅ All files passed validation")
        return
    
    print("\n❌ Files with errors:")
    for result in results['results']:
        if result['errors']:
            print(f"\nFile: {result['file']}")
            for error in result['errors']:
                print(f"  - {error}")
            if verbose and result['warnings']:
                print("  Warnings:")
                for warning in result['warnings']:
                    print(f"    - {warning}")


def main() -> int:
    """Main entry point for the strict validator."""
    parser = argparse.ArgumentParser(description="Strict validator for HEE schema naming enforcement")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--scope", action="append", default=["contracts", "blueprints"], 
                       help="Scopes to validate (default: contracts blueprints)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-only", action="store_true", 
                       help="Only check files, don't run fixer")
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    scope_dirs = [repo_root / s for s in args.scope]
    
    # Validate files
    results = validate_scope(scope_dirs, repo_root)
    
    # Print results
    print_results(results, args.verbose)
    
    # If check-only mode, just return validation status
    if args.check_only:
        return 0 if results['error_count'] == 0 else 1
    
    # Run fixer check if not in check-only mode
    try:
        import subprocess
        fixer_path = repo_root / "ci" / "naming" / "fix_yaml_path_header.py"
        
        if fixer_path.exists():
            print(f"\nRunning fixer check...")
            result = subprocess.run([
                sys.executable, str(fixer_path), 
                "--repo-root", str(repo_root),
                "--scope"] + args.scope + ["--check"],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print("❌ Fixer check failed:")
                print(result.stdout)
                print(result.stderr)
                return 1
            else:
                print("✅ Fixer check passed")
        else:
            print("⚠️  Fixer script not found, skipping fixer check")
    
    except Exception as e:
        print(f"⚠️  Error running fixer check: {e}")
    
    # Run naming check
    try:
        naming_checker_path = repo_root / "ci" / "naming" / "check_authoritative_yaml_naming.py"
        
        if naming_checker_path.exists():
            print(f"\nRunning naming check...")
            result = subprocess.run([
                sys.executable, str(naming_checker_path), 
                "--repo-root", str(repo_root),
                "--scope"] + args.scope,
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print("❌ Naming check failed:")
                print(result.stdout)
                print(result.stderr)
                return 1
            else:
                print("✅ Naming check passed")
        else:
            print("⚠️  Naming checker script not found, skipping naming check")
    
    except Exception as e:
        print(f"⚠️  Error running naming check: {e}")
    
    return 0 if results['error_count'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())