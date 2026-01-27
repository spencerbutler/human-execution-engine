#!/usr/bin/env bash
# Frozen Contracts Presence Checker
# OPS-HEE-Frozen-Contracts-Agent-CI

set -euo pipefail

SCRIPT_NAME="check_frozen_contracts.sh"
SCRIPT_VERSION="1.0.0"

usage() {
  cat << EOF
$SCRIPT_NAME v$SCRIPT_VERSION

Validates presence of frozen contracts and required governance infrastructure.

USAGE:
  $SCRIPT_NAME [--strict]

OPTIONS:
  --strict    Enable best-effort content sanity checks (optional)
  --help, -h  Show this help message

EXIT CODES:
  0    Success - All required files/directories present
  1    Missing required files/directories
  2    Internal error

EOF
}

show_version() {
  echo "$SCRIPT_NAME v$SCRIPT_VERSION"
}

# Check if a file exists
check_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "ERROR: Missing required file: $file" >&2
    return 1
  fi
  return 0
}

# Check if a directory exists
check_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "ERROR: Missing required directory: $dir" >&2
    return 1
  fi
  return 0
}

# Check if files matching pattern exist
check_pattern() {
  local pattern="$1"
  local description="$2"
  if ! compgen -G "$pattern" > /dev/null; then
    echo "ERROR: Missing required $description: $pattern" >&2
    return 1
  fi
  return 0
}

# Best-effort content sanity checks
check_strict() {
  local violations=0

  # Check that FROZEN_CONTRACTS.md has content
  if [[ -f "docs/doctrine/FROZEN_CONTRACTS.md" ]]; then
    local line_count
    line_count=$(wc -l < "docs/doctrine/FROZEN_CONTRACTS.md" 2>/dev/null || echo "0")
    if [[ "$line_count" -lt 5 ]]; then
      echo "WARNING: FROZEN_CONTRACTS.md appears to be minimal content ($line_count lines)" >&2
      # Don't fail on this, just warn
    fi
  fi

  # Check that governance directory has content
  if [[ -d "governance" ]]; then
    local file_count
    file_count=$(find governance -type f | wc -l 2>/dev/null || echo "0")
    if [[ "$file_count" -eq 0 ]]; then
      echo "WARNING: governance/ directory exists but contains no files" >&2
    fi
  fi

  return 0  # Strict checks don't fail the presence check
}

main() {
  local strict_mode=false

  # Parse args
  while [[ $# -gt 0 ]]; do
    case $1 in
      --strict)
        strict_mode=true
        shift
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

  local violations=0

  # Required files
  check_file "ci/governance/check.sh" || ((violations++))
  check_file "docs/doctrine/FROZEN_CONTRACTS.md" || ((violations++))

  # Required directories
  check_dir "governance/fixtures" || ((violations++))
  check_dir "docs/doctrine" || ((violations++))
  check_dir ".github/workflows" || ((violations++))

  # Required pattern
  check_pattern ".github/workflows/*governance*" "governance workflow" || ((violations++))

  # If strict mode requested, do best-effort content checks
  if [[ "$strict_mode" == true ]]; then
    check_strict
  fi

  if [[ $violations -gt 0 ]]; then
    exit 1
  fi

  echo "PASS: All frozen contracts and governance infrastructure present"
  exit 0
}

main "$@"
