#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# ----------------------------
# Guardrails / invariants
# ----------------------------
DEFAULT_PREFIX = "rescue/untracked"
DEFAULT_BASE_BRANCH = "main"


@dataclass(frozen=True)
class Bucket:
    key: str
    files: List[str]


def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], check=check)


def require_git_repo() -> None:
    try:
        git("rev-parse", "--is-inside-work-tree")
    except subprocess.CalledProcessError:
        print("ERROR: not inside a git work tree", file=sys.stderr)
        sys.exit(2)


def ensure_clean_worktree(allow_dirty: bool) -> None:
    r = git("status", "--porcelain")
    if r.stdout.strip() and not allow_dirty:
        print("ERROR: working tree is not clean (use --allow-dirty to override)", file=sys.stderr)
        print(r.stdout, end="", file=sys.stderr)
        sys.exit(2)


def get_untracked() -> List[str]:
    r = git("ls-files", "-o", "--exclude-standard", "-z")
    raw = r.stdout
    if not raw:
        return []
    parts = raw.split("\x00")
    files = [p for p in parts if p]
    return sorted(files)


def top_bucket_key(path: str) -> str:
    """
    Heuristic bucketing:
    - If file is under a top-level dir, bucket by that dir (e.g. 'blueprints', 'docs', 'ci', '.github')
    - Otherwise bucket as 'root'
    """
    p = Path(path)
    if len(p.parts) == 0:
        return "root"
    first = p.parts[0]
    # normalize special top-level
    if first.startswith("."):
        return first  # e.g. ".github", ".vscode"
    return first


def bucketize(files: List[str]) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = {}
    for f in files:
        k = top_bucket_key(f)
        buckets.setdefault(k, []).append(f)
    return buckets


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "bucket"


def branch_name(prefix: str, bucket_key: str) -> str:
    return f"{prefix}/{slugify(bucket_key)}"


def current_branch() -> str:
    r = git("rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.strip()


def checkout_new_branch(branch: str, base: str) -> None:
    git("fetch", "--all", check=False)
    git("checkout", base)
    git("pull", "--ff-only", check=False)
    git("checkout", "-b", branch)


def add_files(files: List[str]) -> None:
    # Use -A with explicit paths; never deletes
    git("add", "--", *files)


def commit(message: str) -> None:
    git("commit", "-m", message)


def print_plan(buckets: Dict[str, List[str]], prefix: str, base: str) -> None:
    print("UNTRACKED RESCUE PLAN")
    print(f"base_branch: {base}")
    print(f"branch_prefix: {prefix}")
    print("")
    for k in sorted(buckets.keys()):
        b = branch_name(prefix, k)
        fs = buckets[k]
        print(f"- bucket: {k}")
        print(f"  branch: {b}")
        print(f"  files: {len(fs)}")
        for f in fs:
            print(f"    - {f}")
    print("")


def apply_plan(
    buckets: Dict[str, List[str]],
    prefix: str,
    base: str,
    commit_prefix: str,
    keep_branch: bool,
) -> None:
    start_branch = current_branch()
    for k in sorted(buckets.keys()):
        fs = buckets[k]
        b = branch_name(prefix, k)
        msg = f"{commit_prefix}: rescue untracked ({k})"

        print(f"APPLY bucket={k} branch={b} files={len(fs)}")
        checkout_new_branch(b, base)
        add_files(fs)

        # If nothing staged (e.g. ignore rules changed), skip
        st = git("diff", "--cached", "--name-only")
        if not st.stdout.strip():
            print(f"  SKIP (nothing staged) bucket={k}")
            git("checkout", start_branch)
            git("branch", "-D", b)
            continue

        commit(msg)
        print(f"  COMMITTED: {msg}")
        print(f"  PR TITLE SUGGESTION: {msg}")
        print("")

        # Return to start branch to avoid accidental stacking
        git("checkout", start_branch)

        if not keep_branch:
            # keep_branch default is True; deletion is opt-in only
            pass

    print("DONE")


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve untracked files into branches + commits.")
    ap.add_argument("--base", default=DEFAULT_BASE_BRANCH, help="Base branch (default: main)")
    ap.add_argument("--prefix", default=DEFAULT_PREFIX, help="Branch prefix (default: rescue/untracked)")
    ap.add_argument(
        "--commit-prefix",
        default="HEE",
        help="Commit message prefix (default: HEE)",
    )
    ap.add_argument("--allow-dirty", action="store_true", help="Allow dirty worktree (NOT recommended)")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run plan only)")
    ap.add_argument(
        "--keep-branches",
        action="store_true",
        help="Keep created branches (default: yes). This flag is here for future extension; currently branches are kept.",
    )
    args = ap.parse_args()

    require_git_repo()

    # Guardrail: don't mix rescue with staged work by default
    ensure_clean_worktree(args.allow_dirty)

    files = get_untracked()
    if not files:
        print("No untracked files found. PASS.")
        return 0

    buckets = bucketize(files)
    print_plan(buckets, args.prefix, args.base)

    if not args.apply:
        print("DRY RUN ONLY (use --apply to execute).")
        return 0

    # Apply plan (creates branches + commits)
    apply_plan(buckets, args.prefix, args.base, args.commit_prefix, keep_branch=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
