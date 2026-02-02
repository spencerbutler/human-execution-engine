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
readonly SCRIPT_VERSION="1.1.0"

# Waiver file location (relative to target repo root)
readonly WAIVER_FILE=".hee/governance/waivers.txt"

usage() {
  cat << EOF2
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
  0    Success - All governance checks passed (after waivers)
  1    Governance violation(s) found (unwaived)
  2    Checker error (invalid arguments, path issues, waiver parse errors, etc.)

OUTPUT FORMAT:
  Violations are emitted as: RULE_ID: SUBJECT: MESSAGE
  Waivers are emitted as: WAIVER_APPLIED: RULE_ID | SUBJECT | EXPIRES | REASON
  Expired waivers are emitted as: WAIVER_EXPIRED: RULE_ID | SUBJECT_GLOB | EXPIRES | REASON

EXAMPLES:
  $SCRIPT_NAME --path .
  $SCRIPT_NAME --path /path/to/repo
  $SCRIPT_NAME --help

EOF2
}

show_version() {
  echo "$SCRIPT_NAME v$SCRIPT_VERSION"
}

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

# Globals populated by load_waivers
waivers=()

# Load and validate waivers from waiver file
# Exits with code 2 on validation error, returns 0 on success
load_waivers() {
  local root_path="$1"
  local waiver_path="$root_path/$WAIVER_FILE"

  waivers=()

  if [[ ! -f "$waiver_path" ]]; then
    return 0
  fi

  local today
  today="$(date +%Y-%m-%d)"

  local line_number=0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line_number=$((line_number + 1))

    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

    # Validate waiver format: RULE_ID | SUBJECT_GLOB | EXPIRES_YYYY-MM-DD | REASON
    if [[ ! "$line" =~ ^([^|]+)\|[[:space:]]*([^|]+)\|[[:space:]]*([^|]+)\|[[:space:]]*(.+)$ ]]; then
      echo "ERROR: Invalid waiver format at line $line_number: $line" >&2
      echo "Expected: RULE_ID | SUBJECT_GLOB | EXPIRES_YYYY-MM-DD | REASON" >&2
      exit 2
    fi

    # Trim whitespace around fields
    local rule_id subject_glob expires reason
    rule_id="$(echo "${BASH_REMATCH[1]}" | xargs)"
    subject_glob="$(echo "${BASH_REMATCH[2]}" | xargs)"
    expires="$(echo "${BASH_REMATCH[3]}" | xargs)"
    reason="$(echo "${BASH_REMATCH[4]}" | xargs)"

    if [[ -z "$rule_id" || -z "$subject_glob" || -z "$expires" || -z "$reason" ]]; then
      echo "ERROR: Invalid waiver line (empty field) at line $line_number: $line" >&2
      exit 2
    fi

    # Validate expiration date format
    if [[ ! "$expires" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
      echo "ERROR: Invalid expiration date format at line $line_number: $expires" >&2
      echo "Expected: YYYY-MM-DD" >&2
      exit 2
    fi

    # Expired waivers are ignored, but reported
    if [[ "$expires" < "$today" ]]; then
      echo "WAIVER_EXPIRED: $rule_id | $subject_glob | $expires | $reason" >&2
      continue
    fi

    waivers+=("$rule_id|$subject_glob|$expires|$reason")
  done < "$waiver_path"

  return 0
}

# Returns 0 if waived (suppress), 1 if not waived
is_violation_waived() {
  local rule_id="$1"
  local subject="$2"

  for waiver in "${waivers[@]}"; do
    IFS='|' read -r w_rule_id w_subject_glob w_expires w_reason <<< "$waiver"
    # IMPORTANT: subject matching uses glob semantics (waiver subject is a glob)
    if [[ "$rule_id" == "$w_rule_id" ]]; then
      # shellcheck disable=SC2254
      case "$subject" in
        $w_subject_glob)
          echo "WAIVER_APPLIED: $rule_id | $subject | $w_expires | $w_reason" >&2
          return 0
          ;;
      esac
    fi
  done

  return 1
}

# Parse structured violation line into RULE_ID and SUBJECT.
# Expected: RULE_ID: SUBJECT: MESSAGE
# Echoes "RULE_ID|SUBJECT" on success, returns 0. Returns 1 on parse failure.
parse_violation_line() {
  # Whitelist-only parser: emit ONLY real governance violations.
  # Everything else (including bash -x / xtrace noise) is ignored.
  local line="${1-}"

  # normalize CRLF + trim leading whitespace
  line="${line//$'\r'/}"
  line="${line#"${line%%[![:space:]]*}"}"

  # ignore empty, comments, waiver markers, and any non-violation noise
  [[ -z "$line" ]] && return 1
  [[ "$line" == \#* ]] && return 1
  [[ "$line" == WAIVER_APPLIED:* ]] && return 1

  # Accept ONLY these shapes:
  #   GOV-XXXX-001: ...
  #   GOV-XXXX-001 | subject | description
  #   VIOLATION: GOV-XXXX-001 | subject | description
  if [[ "$line" =~ ^(VIOLATION:[[:space:]]*)?GOV-[A-Z0-9]+-[0-9]{3}[[:space:]]*(:|\|) ]]; then
    printf "%s\n" "$line"
    return 0
  fi

  return 1
}


main() {
  local target_path=""

  # Parse args
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

  if [[ -z "$target_path" ]]; then
    echo "ERROR: --path argument is required" >&2
    usage >&2
    exit 2
  fi

  # Resolve to absolute path (immutable root)
  if ! target_path=$(realpath "$target_path" 2>/dev/null); then
    echo "ERROR: Failed to resolve path: $target_path" >&2
    exit 2
  fi


  if ! validate_path "$target_path"; then
    exit 2
  fi

  # Load waivers (may exit 2 on error)
  load_waivers "$target_path"

  # Run governance checks, capturing all output (violations are expected here)
  local output rc
  set +e
  output="$(run_governance_checks "$target_path" 2>&1)"
  rc=$?
  set -e

  # If rules succeeded and produced no output, we are done.
  if [[ $rc -eq 0 ]]; then
    exit 0
  fi

  # Filter violations through waivers
  local remaining=0
  local line parsed rule_id subject

  while IFS= read -r line || [[ -n "$line" ]]; do
    # Ignore empty lines
    [[ -z "$line" ]] && continue

    if parsed="$(parse_violation_line "$line")"; then
      rule_id="${parsed%%|*}"
      subject="${parsed#*|}"

      if is_violation_waived "$rule_id" "$subject"; then
        # waived: suppress original violation line
        continue
      fi
    fi

    # Not waived (or not parseable): print and count
    echo "$line" >&2
    remaining=$((remaining + 1))
  done <<< "$output"

  if [[ $remaining -eq 0 ]]; then
    exit 0
  fi

  exit 1
}

main "$@"
