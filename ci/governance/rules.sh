#!/usr/bin/env bash
# HEE Governance Rules Implementation
# This file contains the rule definitions and validation logic

set -euo pipefail

# Rule Registry - Declarative definition of all governance rules
RULES=(
  "GOV-STRUCT-001:required_paths_exist"
  "GOV-DOC-001:doctrine_presence"
  "GOV-PROMPT-001:prompt_schema_validation"
)

# Rule: GOV-STRUCT-001 - Required Paths Exist
# Validates that required directory structure exists
# Required paths: docs/, prompts/, .github/workflows/
check_gov_struct_001() {
  local root_path="$1"
  local violations=()

  local required_paths=("docs" "prompts" ".github/workflows")

  for path in "${required_paths[@]}"; do
    if [[ ! -d "$root_path/$path" ]]; then
      violations+=("$path/")
    fi
  done

  if [[ ${#violations[@]} -gt 0 ]]; then
    printf 'GOV-STRUCT-001: %s: missing required path(s)\n' "<root>" >&2
    for v in "${violations[@]}"; do
      printf 'GOV-STRUCT-001: %s: missing required path\n' "$v" >&2
    done
    return 1
  fi

  return 0
}

# Rule: GOV-DOC-001 - Doctrine Presence
# Validates that doctrine directory exists and contains at least one document
# Requirement: docs/doctrine/ directory exists with ≥1 file
check_gov_doc_001() {
  local root_path="$1"
  local doctrine_dir="$root_path/docs/doctrine"

  if [[ ! -d "$doctrine_dir" ]]; then
    printf 'GOV-DOC-001: %s: doctrine directory missing\n' "docs/doctrine/" >&2
    return 1
  fi

  local file_count
  file_count=$(find "$doctrine_dir" -maxdepth 1 -type f | wc -l)

  if [[ $file_count -eq 0 ]]; then
    printf 'GOV-DOC-001: %s: doctrine directory exists but contains no documents\n' "docs/doctrine/" >&2
    return 1
  fi

  return 0
}

# Rule: GOV-PROMPT-001 - Prompt Schema Minimum Sections
# Validates prompts contain required structural elements
# Required sections: Authority, Scope, Invariants (case-insensitive)
check_gov_prompt_001() {
  local root_path="$1"
  local prompts_dir="$root_path/prompts"

  if [[ ! -d "$prompts_dir" ]]; then
    # If prompts directory doesn't exist, this is caught by GOV-STRUCT-001
    return 0
  fi

  local violations_found=false

  while IFS= read -r -d '' prompt_file; do
    local has_authority=false
    local has_scope=false
    local has_invariants=false

    if grep -qi "^#\+[[:space:]]*authority" "$prompt_file"; then
      has_authority=true
    fi
    if grep -qi "^#\+[[:space:]]*scope" "$prompt_file"; then
      has_scope=true
    fi
    if grep -qi "^#\+[[:space:]]*invariant" "$prompt_file"; then
      has_invariants=true
    fi

    if [[ $has_authority != true || $has_scope != true || $has_invariants != true ]]; then
      local missing_sections=()
      [[ $has_authority != true ]] && missing_sections+=("Authority")
      [[ $has_scope != true ]] && missing_sections+=("Scope")
      [[ $has_invariants != true ]] && missing_sections+=("Invariants")

      # Subject should be a stable repo-relative path
      local subject="$prompt_file"
      if [[ "$subject" == "$root_path/"* ]]; then
        subject="${subject#$root_path/}"
      else
        subject="$(basename "$prompt_file")"
      fi

      printf 'GOV-PROMPT-001: %s: missing %s\n' "$subject" "${missing_sections[*]}" >&2
      violations_found=true
    fi
  done < <(find "$prompts_dir" -name "*.md" -type f -print0)

  if [[ $violations_found == true ]]; then
    return 1
  fi

  return 0
}

# Main rule execution function
# Runs all governance rules against the specified path
run_governance_checks() {
  local root_path="$1"
  local violations_found=false

  if ! check_gov_struct_001 "$root_path"; then
    violations_found=true
  fi
  if ! check_gov_doc_001 "$root_path"; then
    violations_found=true
  fi
  if ! check_gov_prompt_001 "$root_path"; then
    violations_found=true
  fi

  if [[ $violations_found == true ]]; then
    return 1
  fi

  return 0
}
