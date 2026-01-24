#!/usr/bin/env bash
set -euo pipefail

# Consumer-side HEE freshness check (template)
# Assumes HEE is vendored into the consumer repo and exposes docs/hee/VERSION.md.

EXPECTED_VERSION_FILE="docs/hee/VERSION.md"

if [[ ! -f "$EXPECTED_VERSION_FILE" ]]; then
  echo "ERROR: $EXPECTED_VERSION_FILE not found."
  echo "HEE policy may not be vendored correctly."
  exit 2
fi

VENDORED_VERSION="$(sed -n '1p' "$EXPECTED_VERSION_FILE" | tr -d '[:space:]')"

if [[ -z "$VENDORED_VERSION" ]]; then
  echo "ERROR: $EXPECTED_VERSION_FILE is empty or malformed."
  exit 3
fi

echo "OK: Vendored HEE version detected: $VENDORED_VERSION"
