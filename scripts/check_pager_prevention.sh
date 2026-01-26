#!/usr/bin/env bash
set -euo pipefail

# HEE Pager Prevention Check Script
# Governance intent: in non-interactive CI contexts, git commands must not invoke an interactive pager.
#
# Deterministic scope:
# - Only scan tracked files under:
#     - .github/workflows/** (executed by CI)
#     - scripts/**          (invoked by CI or automation)
#
# Recognized pager-prevention mechanisms (any is sufficient):
# - git --no-pager log ...
# - git -c core.pager=cat log ...
# - env-level prevention in the same file:
#     - GIT_PAGER=cat / PAGER=cat (shell style)
#     - env: GIT_PAGER: cat / env: PAGER: cat (GitHub Actions YAML style)

echo "🔍 Checking for pager prevention in CI-executed contexts..."

# Deterministically list tracked files in relevant execution contexts.
# (Avoid scanning docs/markdown; only scan automation and workflow definitions.)
mapfile -t files < <(
  git ls-files '.github/workflows/*.yml' '.github/workflows/*.yaml' 'scripts/*.sh' 2>/dev/null || true
)

if (( ${#files[@]} == 0 )); then
  echo "✅ Pager prevention check passed (no scoped files found)"
  exit 0
fi

# Patterns
git_log_re='(^|[[:space:];|&])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+log\b'
inline_ok_re='(--no-pager|-c[[:space:]]+core\.pager=|GIT_PAGER=cat|PAGER=cat|core\.pager=cat)'

# YAML env-level prevention (same-file mitigation)
yaml_env_ok_re='(^|[[:space:]])GIT_PAGER:[[:space:]]*cat\b|(^|[[:space:]])PAGER:[[:space:]]*cat\b'

violations=0

for f in "${files[@]}"; do
  # If the file declares global env pager prevention, we accept git log occurrences in that file
  # even when the line itself doesn't include --no-pager.
  file_has_global_ok=0
  if grep -Eq "$yaml_env_ok_re" "$f" 2>/dev/null; then
    file_has_global_ok=1
  elif grep -Eq '(^|[[:space:]])(export[[:space:]]+)?GIT_PAGER=cat\b|(^|[[:space:]])(export[[:space:]]+)?PAGER=cat\b' "$f" 2>/dev/null; then
    file_has_global_ok=1
  fi

  # Scan line-by-line to produce actionable output (file + line number).
  # Only flag pager-risk git log calls that lack any prevention.
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ $git_log_re ]]; then
      if [[ "$line" =~ $inline_ok_re ]]; then
        continue
      fi
      if (( file_has_global_ok == 1 )); then
        continue
      fi

      # Emit first few violations with line number for auditability.
      lineno=$(grep -nF -- "$line" "$f" | head -n 1 | cut -d: -f1 || echo "?")
      echo "❌ Pager-risk git log without prevention: ${f}:${lineno}"
      echo "   $line"
      violations=$((violations+1))
      if (( violations >= 5 )); then
        break
      fi
    fi
  done < "$f"

  if (( violations >= 5 )); then
    break
  fi
done

if (( violations > 0 )); then
  echo
  echo "Failing pager-prevention check: add one of:"
  echo "  - git --no-pager log ..."
  echo "  - git -c core.pager=cat log ..."
  echo "  - workflow env: GIT_PAGER: cat (or PAGER: cat)"
  echo "  - script env: export GIT_PAGER=cat (or PAGER=cat)"
  exit 1
fi

echo "✅ Pager prevention check passed"
exit 0
