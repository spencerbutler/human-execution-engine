#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Validating pager prevention in CI-executed contexts..."

# Deterministic scope: only tracked files that can actually execute in CI contexts.
# Do NOT scan docs/markdown.
mapfile -t files < <(
  git ls-files \
    '.github/workflows/*.yml' '.github/workflows/*.yaml' \
    'scripts/*.sh' \
    2>/dev/null || true
)

if (( ${#files[@]} == 0 )); then
  echo "✅ Pager prevention validation passed (no scoped files found)"
  exit 0
fi

# Skip this script to avoid self-matching in comments/strings.
self_path="scripts/check_pager_prevention.sh"

# Patterns
git_log_re='(^|[[:space:];|&])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+log\b'
man_re='(^|[[:space:];|&])man[[:space:]]+[^[:space:]]'

# Inline mitigations
git_inline_ok_re='(--no-pager|-c[[:space:]]+core\.pager=|GIT_PAGER=cat|PAGER=cat|core\.pager=cat)'
man_inline_ok_re='(man[[:space:]]+-P[[:space:]]+cat|MANPAGER=cat|PAGER=cat)'

# YAML env-level mitigations (same-file)
yaml_env_ok_re='(^|[[:space:]])GIT_PAGER:[[:space:]]*cat\b|(^|[[:space:]])PAGER:[[:space:]]*cat\b|(^|[[:space:]])MANPAGER:[[:space:]]*cat\b'

violations=0

for f in "${files[@]}"; do
  [[ "$f" == "$self_path" ]] && continue

  # File-level mitigation present?
  file_has_global_ok=0
  if grep -Eq "$yaml_env_ok_re" "$f" 2>/dev/null; then
    file_has_global_ok=1
  elif grep -Eq '(^|[[:space:]])(export[[:space:]]+)?GIT_PAGER=cat\b|(^|[[:space:]])(export[[:space:]]+)?PAGER=cat\b|(^|[[:space:]])(export[[:space:]]+)?MANPAGER=cat\b' "$f" 2>/dev/null; then
    file_has_global_ok=1
  fi

  # Line-by-line scan; ignore pure comment lines to reduce noise.
  lineno=0
  while IFS= read -r line || [[ -n "$line" ]]; do
    lineno=$((lineno+1))

    # Ignore comment-only lines (bash/yaml comments). This is safe because comments are non-executable.
    [[ "$line" =~ ^[[:space:]]*# ]] && continue

    # --- git log ---
    if [[ "$line" =~ $git_log_re ]]; then
      if [[ "$line" =~ $git_inline_ok_re ]] || (( file_has_global_ok == 1 )); then
        :
      else
        echo "❌ Pager-risk git log without prevention: ${f}:${lineno}"
        echo "   $line"
        violations=$((violations+1))
      fi
    fi

    # --- man ---
    if [[ "$line" =~ $man_re ]]; then
      if [[ "$line" =~ $man_inline_ok_re ]] || (( file_has_global_ok == 1 )); then
        :
      else
        echo "❌ Pager-risk man without prevention: ${f}:${lineno}"
        echo "   $line"
        violations=$((violations+1))
      fi
    fi

    if (( violations >= 5 )); then
      break
    fi
  done < "$f"

  if (( violations >= 5 )); then
    break
  fi
done

if (( violations > 0 )); then
  echo
  echo "Failing pager-prevention validation. Fix by adding one of:"
  echo "  - git --no-pager log ..."
  echo "  - git -c core.pager=cat log ..."
  echo "  - workflow env: GIT_PAGER: cat (and/or PAGER: cat)"
  echo "  - script env: export GIT_PAGER=cat (and/or PAGER=cat)"
  echo "  - man -P cat <topic>  OR  MANPAGER=cat"
  exit 1
fi

echo "✅ Pager prevention validation passed"
