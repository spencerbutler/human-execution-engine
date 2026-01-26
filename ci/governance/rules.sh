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

  # Check required directories
  local required_paths=("docs" "prompts" ".github/workflows")

  for path in "${required_paths[@]}"; do
    if [[ ! -d "$root_path/$path" ]]; then
      violations+=("$path/")
    fi
  done

  if [[ ${#violations[@]} -gt 0 ]]; then
    echo "GOV-STRUCT-001: missing required path: ${violations[*]}"
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
    echo "GOV-DOC-001: doctrine directory missing"
    return 1
  fi

  # Check if directory has any files (not just subdirectories)
  local file_count
  file_count=$(find "$doctrine_dir" -maxdepth 1 -type f | wc -l)

  if [[ $file_count -eq 0 ]]; then
    echo "GOV-DOC-001: doctrine directory exists but contains no documents"
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

  local violations=()

  # Check all .md files in prompts directory
  while IFS= read -r -d '' prompt_file; do
    local has_authority=false
    local has_scope=false
    local has_invariants=false

    # Check for required sections (case-insensitive, must be at start of line)
    if grep -qi "^#\+[[:space:]]*authority" "$prompt_file"; then
      has_authority=true
    fi

    if grep -qi "^#\+[[:space:]]*scope" "$prompt_file"; then
      has_scope=true
    fi

    if grep -qi "^#\+[[:space:]]*invariant" "$prompt_file"; then
      has_invariants=true
    fi

    # If any required section is missing, record violation
    if [[ $has_authority != true || $has_scope != true || $has_invariants != true ]]; then
      local missing_sections=()
      [[ $has_authority != true ]] && missing_sections+=("Authority")
      [[ $has_scope != true ]] && missing_sections+=("Scope")
      [[ $has_invariants != true ]] && missing_sections+=("Invariants")

      violations+=("$(basename "$prompt_file"): missing ${missing_sections[*]}")
    fi
  done < <(find "$prompts_dir" -name "*.md" -type f -print0)

  if [[ ${#violations[@]} -gt 0 ]]; then
    echo "GOV-PROMPT-001: ${violations[*]}"
    return 1
  fi

  return 0
}

# Main rule execution function
# Runs all governance rules against the specified path
run_governance_checks() {
  local root_path="$1"
  local violations_found=false

  # Run each rule
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
