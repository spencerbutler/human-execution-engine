# rg.scan.shfn.bash
#
# shfn: tiny ripgrep helpers for oper UX
# - default to counts (wc -l)
# - write full matches to mktemp ONLY when needed (hits>0) or forced
# - never exit (return only)
#
# Usage:
#   rg_count 'PATTERN' [paths...]
#   rg_scan  'PATTERN' [paths...]            # AUTO: mktemp report only if hits>0
#   rg_scan  --out ALWAYS 'PATTERN' [paths...]
#   rg_scan  --out NEVER  'PATTERN' [paths...]
#

rg_count() {
  local pat="$1"; shift || true
  rg -n --hidden -S "$pat" "$@" 2>/dev/null | wc -l | tr -d ' '
}

rg_scan() {
  local out_mode="AUTO"
  if [ "${1-}" = "--out" ]; then
    out_mode="${2-}"; shift 2 || true
  fi

  local pat="${1-}"
  if [ -z "$pat" ]; then
    echo "❌ rg_scan: missing PATTERN" >&2
    return 2
  fi
  shift || true

  local paths=("$@")
  if [ "${#paths[@]}" -eq 0 ]; then
    paths=(.)
  fi

  local hits
  hits="$(rg_count "$pat" "${paths[@]}")" || return 1

  if [ "$hits" -eq 0 ]; then
    echo "✅ rg_scan hits=0 pattern=$pat"
    return 0
  fi

  echo "🛑 rg_scan hits=$hits pattern=$pat"

  case "$out_mode" in
    NEVER) return 0 ;;
    ALWAYS|AUTO) ;;
    *) echo "❌ rg_scan: --out must be AUTO|ALWAYS|NEVER" >&2; return 2 ;;
  esac

  local out
  out="$(mktemp -t hee.rg.scan.XXXXXX.txt)" || { echo "❌ rg_scan: mktemp failed" >&2; return 1; }

  {
    echo "# rg_scan"
    echo "timestamp=$(date -Is)"
    echo "pattern=$pat"
    echo "paths=${paths[*]}"
    echo
    rg -n --hidden -S "$pat" "${paths[@]}" || true
  } > "$out"

  echo "🧾 rg_scan report=$out"
  return 0
}
