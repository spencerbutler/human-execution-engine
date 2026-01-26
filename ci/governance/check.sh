#!/usr/bin/env bash
# HEE Governance Checker - Single Stable Entrypoint
# OPS-HEE-CI-Governance-Testing

set -euo pipefail

# Load governance rules
# shellcheck source=ci/governance/rules.sh
# shellcheck disable=SC1091
source "$(dirname "${BASH_SOURCE[0]}")/rules.sh"

# Script constants
readonly SCRIPT_NAME="check.sh"
readonly SCRIPT_VERSION="1.0.0"

# Usage information
usage() {
  cat << EOF
HEE Governance Checker v${SCRIPT_VERSION}

Validates HEE governance invariants against a repository path.

USAGE:
  $SCRIPT_NAME --path <directory> [OPTIONS]

REQUIRED ARGUMENTS:
  --path <directory>    Path to repository root to check

OPTIONS:
  --help, -h           Show this help message
  --version, -v        Show version information

EXIT CODES:
  0    Success - All governance checks passed
  1    Governance violation(s) found
  2    Checker error (invalid arguments, path issues, etc.)

OUTPUT FORMAT:
  Violations are emitted as: RULE_ID: description

EXAMPLES:
  $SCRIPT_NAME --path .
  $SCRIPT_NAME --path /path/to/repo
  $SCRIPT_NAME --help

EOF
}

# Show version
show_version() {
  echo "$SCRIPT_NAME v$SCRIPT_VERSION"
}

# Validate that a path exists and is a directory
validate_path() {
  local path="$1"

  if [[ ! -e "$path" ]]; then
    echo "ERROR: Path does not exist: $path" >&2
    return 1
  fi

  if [[ ! -d "$path" ]]; then
    echo "ERROR: Path is not a directory: $path" >&2
    return 1
  fi

  return 0
}

# Main function
main() {
  local target_path=""

  # Parse command line arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --path)
        if [[ -n "${2:-}" ]]; then
          target_path="$2"
          shift 2
        else
          echo "ERROR: --path requires a directory argument" >&2
          usage >&2
          exit 2
        fi
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      --version|-v)
        show_version
        exit 0
        ;;
      *)
        echo "ERROR: Unknown option: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
  done

  # Validate required arguments
  if [[ -z "$target_path" ]]; then
    echo "ERROR: --path argument is required" >&2
    usage >&2
    exit 2
  fi

  # Resolve path to absolute path immediately
  # This ensures immutable root and prevents cd-related issues
  if ! target_path=$(realpath "$target_path" 2>/dev/null); then
    echo "ERROR: Failed to resolve path: $target_path" >&2
    exit 2
  fi

  # Validate the resolved path
  if ! validate_path "$target_path"; then
    exit 2
  fi

  # Run governance checks
  # All output from rules goes to stdout/stderr as violations
  if run_governance_checks "$target_path"; then
    # Success - no violations found
    exit 0
  else
    # Violations found
    exit 1
  fi
}

# Execute main function with all arguments
main "$@"
