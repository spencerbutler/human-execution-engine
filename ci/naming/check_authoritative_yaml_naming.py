#!/usr/bin/env python3
"""
Authoritative YAML Naming Checker for HEE Schema Naming Enforcement

This script validates YAML files for Phase 05 requirements:
- Require .yaml extension; disallow .yml
- Enforce kebab-case filenames
- Max dots in filename = 1
- Scope: include contracts/**, blueprints/**; exclude var/**
- Fail fast; list offending repo-relative paths; no auto-fix
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Naming rules
REQUIRED_EXTENSION = ".yaml"
FORBIDDEN_EXTENSION = ".yml"
MAX_DOTS_IN_FILENAME = 1


def is_kebab_case(name: str) -> bool:
    """
    Check if a filename is in kebab-case.

    Args:
        name: Filename to check

    Returns:
        True if kebab-case, False otherwise
    """
    # Remove extension and check pattern
    base_name = name.replace(REQUIRED_EXTENSION, "")

    # Must contain only lowercase letters, numbers, and hyphens
    if not re.match(r'^[a-z0-9-]+$', base_name):
        return False

    # Must not start or end with hyphen
    if base_name.startswith('-') or base_name.endswith('-'):
        return False

    # Must not have consecutive hyphens
    if '--' in base_name:
        return False

    # Must not be empty
    if not base_name:
        return False

    return True


def count_dots_in_filename(name: str) -> int:
    """
    Count dots in filename (excluding extension).

    Args:
        name: Filename to check

    Returns:
        Number of dots in filename
    """
    base_name = name.replace(REQUIRED_EXTENSION, "")
    return base_name.count('.')


def validate_file_naming(file_path: Path, repo_root: Path) -> Tuple[bool, List[str]]:
    """
    Validate naming rules for a single YAML file.

    Args:
        file_path: Path to the YAML file
        repo_root: Repository root path

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check extension
    if file_path.suffix == FORBIDDEN_EXTENSION:
        errors.append(f"File uses forbidden extension '{FORBIDDEN_EXTENSION}', must use '{REQUIRED_EXTENSION}'")

    if file_path.suffix != REQUIRED_EXTENSION:
        errors.append(f"File must use extension '{REQUIRED_EXTENSION}'")

    # Check kebab-case
    if not is_kebab_case(file_path.name):
        errors.append(f"Filename '{file_path.name}' is not in kebab-case")

    # Check dots count
    dots_count = count_dots_in_filename(file_path.name)
    if dots_count > MAX_DOTS_IN_FILENAME:
        errors.append(f"Filename '{file_path.name}' has {dots_count} dots, maximum allowed is {MAX_DOTS_IN_FILENAME}")

    return len(errors) == 0, errors


def validate_scope(scope_dirs: List[Path], repo_root: Path) -> Dict[str, Any]:
    """
    Validate naming rules for all YAML files in the specified scope.

    Args:
        scope_dirs: List of directories to validate
        repo_root: Repository root path

    Returns:
        Dictionary with overall validation results
    """
    all_errors = []
    total_files = 0
    valid_files = 0

    for scope_dir in scope_dirs:
        if not scope_dir.exists():
            continue

        for yaml_file in scope_dir.rglob("*.yaml"):
            # Skip var/** files
            if "var" in yaml_file.parts:
                continue

            total_files += 1
            is_valid, errors = validate_file_naming(yaml_file, repo_root)

            if errors:
                # Convert to repo-relative path for error reporting
                rel_path = yaml_file.relative_to(repo_root).as_posix()
                for error in errors:
                    all_errors.append(f"{rel_path}: {error}")
            else:
                valid_files += 1

    return {
        'total_files': total_files,
        'valid_files': valid_files,
        'errors': all_errors
    }


def print_results(results: Dict[str, Any]) -> None:
    """
    Print validation results.

    Args:
        results: Validation results dictionary
    """
    print(f"Total files: {results['total_files']}")
    print(f"Valid files: {results['valid_files']}")
    print(f"Errors: {len(results['errors'])}")

    if results['total_files'] == 0:
        print("No YAML files found in scope")
        return

    if len(results['errors']) == 0:
        print("✅ All files passed naming validation")
        return

    print("\n❌ Files with naming errors:")
    for error in results['errors']:
        print(f"  - {error}")


def main() -> int:
    """Main entry point for the naming checker."""
    parser = argparse.ArgumentParser(description="Authoritative YAML naming checker for HEE schema naming enforcement")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--scope", action="append", default=["contracts", "blueprints"],
                       help="Scopes to validate (default: contracts blueprints)")
    parser.add_argument("--fail-fast", action="store_true",
                       help="Exit immediately on first error (default: collect all errors)")

    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scope_dirs = [repo_root / s for s in args.scope]

    # Validate files
    results = validate_scope(scope_dirs, repo_root)

    # Print results
    print_results(results)

    # Fail fast if requested and there are errors
    if args.fail_fast and results['errors']:
        print(f"\n❌ Fail-fast mode: Exiting due to {len(results['errors'])} naming errors")
        return 1

    # Return non-zero exit code if there are any errors
    return 1 if results['errors'] else 0


if __name__ == "__main__":
    sys.exit(main())
