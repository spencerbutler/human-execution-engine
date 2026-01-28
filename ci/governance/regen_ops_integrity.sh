#!/usr/bin/env bash
set -euo pipefail

die(){ echo "FAIL: $*" >&2; exit 2; }
note(){ echo "note: $*" >&2; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not in a git repo"
cd "$ROOT"

DIR="docs/governance/operations"
OUT="$DIR/INTEGRITY_SHA256SUMS"

[[ -d "$DIR" ]] || die "missing $DIR"

command -v sha256sum >/dev/null || die "missing sha256sum"

note "regenerating $OUT"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

find "$DIR" -type f ! -name "$(basename "$OUT")" -print0 \
  | sort -z \
  | xargs -0 sha256sum >"$tmp"

mv "$tmp" "$OUT"
note "OK: wrote $OUT"
