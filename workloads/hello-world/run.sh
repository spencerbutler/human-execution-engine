#!/usr/bin/env sh
set -eu

echo "HEE-HELLO-WORLD: ok"

if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
  if [ -z "${GITHUB_SHA:-}" ]; then
    echo "ERROR: missing GITHUB_SHA"
    exit 4
  fi
fi
