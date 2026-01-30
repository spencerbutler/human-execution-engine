#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable

HEADER_PREFIX = "# path: "

def iter_yaml_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in (".yaml", ".yml"):
            continue
        parts = p.parts
        if "var" in parts:
            continue
        yield p

def ensure_header(file_path: Path, repo_root: Path) -> tuple[bool, str]:
    rel = file_path.relative_to(repo_root).as_posix()
    desired = f"{HEADER_PREFIX}{rel}\n"
    data = file_path.read_text(encoding="utf-8")
    lines = data.splitlines(keepends=True)

    if not lines:
        new_data = desired
        return True, new_data

    # If first line already a path header, normalize it.
    if lines[0].startswith(HEADER_PREFIX):
        if lines[0] == desired:
            return False, data
        lines[0] = desired
        return True, "".join(lines)

    # Insert header as first line.
    return True, desired + data

def main() -> int:
    ap = argparse.ArgumentParser(description="Ensure YAML files begin with a canonical '# path: <relpath>' header.")
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .)")
    ap.add_argument("--scope", action="append", default=["contracts", "blueprints"], help="Scopes to process")
    ap.add_argument("--check", action="store_true", help="Check only; non-zero if changes needed")
    ap.add_argument("--apply", action="store_true", help="Apply changes in-place")
    args = ap.parse_args()

    if args.check and args.apply:
        raise SystemExit("Choose only one: --check or --apply")

    repo_root = Path(args.repo_root).resolve()
    scopes = [repo_root / s for s in args.scope]

    changed: list[str] = []
    for scope in scopes:
        if not scope.exists():
            continue
        for f in iter_yaml_files(scope):
            did_change, new_data = ensure_header(f, repo_root)
            if did_change:
                changed.append(f.relative_to(repo_root).as_posix())
                if args.apply:
                    f.write_text(new_data, encoding="utf-8")

    if args.check:
        if changed:
            print("NEEDS_FIX:")
            for p in changed:
                print(p)
            return 2
        print("OK")
        return 0

    if args.apply:
        if changed:
            print("UPDATED:")
            for p in changed:
                print(p)
        else:
            print("NO_CHANGES")
        return 0

    # default: check mode semantics without exit 2
    if changed:
        print("NEEDS_FIX:")
        for p in changed:
            print(p)
    else:
        print("OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
