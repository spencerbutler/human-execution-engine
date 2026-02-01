#!/usr/bin/env sh
# schema-id-scan: scan schemas/** for $id and $ref and write an outfile mapping.
# NOTE: does not modify working tree.

set -u

TOPIC="${TOPIC:-hee-rfc-kickoff-onegogreen}"
EVDIR="${EVDIR:-.hee/evidence/$TOPIC}"
mkdir -p "$EVDIR"

OUT="${OUT:-$EVDIR/E99-schema-id-scan.txt}"

_now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
_host() { hostname -f 2>/dev/null || hostname; }

{
  echo "# NOW (UTC)"; _now
  echo "# HOST"; _host
  echo "# PWD"; pwd
  echo "# GIT_ROOT"; (git rev-parse --show-toplevel 2>/dev/null || echo "no_git")
  echo

  if ! command -v rg >/dev/null 2>&1; then
    echo "scan=FAIL reason=rg_missing"
    exit 0
  fi

  echo "# MATCHES: file:line: $id/$ref"
  rg -n --no-heading '"\$id"[[:space:]]*:|"\$ref"[[:space:]]*: ' schemas 2>/dev/null || true
} > "$OUT" 2>&1

echo "WROTE: $OUT"
