#!/bin/sh
set -eu

fail=0

# Check candidate YAML files (tune patterns as needed)
# Default: hee/cards + hee/pills + hee/contracts if present.
paths="hee/cards hee/pills hee/contracts"

for p in $paths; do
  [ -d "$p" ] || continue
  find "$p" -type f \( -name '*.yml' -o -name '*.yaml' \) | while IFS= read -r f; do
    # Grab first two meaningful keys
    k1="$(awk '
      /^[[:space:]]*#/ {next}
      /^[[:space:]]*$/ {next}
      { sub(/:.*/, "", $0); gsub(/[[:space:]]+/, "", $0); print; exit }
    ' "$f" 2>/dev/null || true)"

    k2="$(awk '
      BEGIN{c=0}
      /^[[:space:]]*#/ {next}
      /^[[:space:]]*$/ {next}
      { c++; if(c==2){ sub(/:.*/, "", $0); gsub(/[[:space:]]+/, "", $0); print; exit } }
    ' "$f" 2>/dev/null || true)"

    # Only enforce if it looks like a hee-obj (apiVersion/kind present somewhere)
    if rg -q -n '^[[:space:]]*apiVersion:' "$f" && rg -q -n '^[[:space:]]*kind:' "$f"; then
      if [ "$k1" != "apiVersion" ] || [ "$k2" != "kind" ]; then
        echo "❌ YAML header order: $f (got: $k1 then $k2; want: apiVersion then kind)" 1>&2
        fail=1
      fi
    fi
  done
done

exit "$fail"
