#!/usr/bin/env bash
set -u
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SB_SRC="$SRC_DIR/shellboss"
LIB_SRC_DIR="$SRC_DIR/library/bash"
SB_DST="${SB_DST:-$HOME/.local/bin/shellboss}"
LIB_DST_DIR="${LIB_DST_DIR:-$HOME/.hee/library/bash}"
force="${FORCE:-0}"
die(){ echo "ERROR: $*" >&2; exit 1; }
ok(){ echo "OK: $*"; }
test -f "$SB_SRC" || die "missing: $SB_SRC"
test -d "$LIB_SRC_DIR" || die "missing: $LIB_SRC_DIR"
mkdir -p "$(dirname "$SB_DST")" "$LIB_DST_DIR" || die "mkdir failed"
if test -e "$SB_DST" && test "$force" != "1"; then
  die "clobber refused: $SB_DST (set FORCE=1 to override)"
fi
cp -p "$SB_SRC" "$SB_DST" || die "copy shellboss failed"
chmod +x "$SB_DST" || die "chmod failed"
ok "installed: $SB_DST"
for f in "$LIB_SRC_DIR"/*.bash; do
  base="$(basename "$f")"
  dst="$LIB_DST_DIR/$base"
  if test -e "$dst" && test "$force" != "1"; then
    die "clobber refused: $dst (set FORCE=1 to override)"
  fi
  cp -p "$f" "$dst" || die "copy lib failed: $base"
  ok "installed: $dst"
done
ok "done"
