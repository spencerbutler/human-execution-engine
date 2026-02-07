#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

def die(msg: str, rc: int = 2) -> int:
    print(f"RRR_ERR: {msg}", file=sys.stderr)
    return rc

def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H_%M_%SZ")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def slug(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9._-]", "", s)
    s = s.strip("-._")
    return s or "rrr"

def read_recipe(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    txt = open(path, "r", encoding="utf-8").read()
    if path.endswith(".json"):
        return json.loads(txt)
    if yaml is None:
        raise RuntimeError("PyYAML not available (import yaml failed). Use .json or install PyYAML.")
    return yaml.safe_load(txt)

def canonicalize(recipe: dict) -> dict:
    # Minimal, deterministic normalization.
    out = dict(recipe) if isinstance(recipe, dict) else {"value": recipe}
    if "name" in out and isinstance(out["name"], str):
        out["name"] = out["name"].strip()
    # Ensure steps is a list
    steps = out.get("steps", [])
    if steps is None:
        steps = []
    out["steps"] = steps
    return out

def compute_tokens(recipe: dict) -> list[str]:
    steps = recipe.get("steps", [])
    toks: list[str] = []
    if isinstance(steps, list):
        for i, st in enumerate(steps):
            if isinstance(st, dict):
                sid = st.get("id")
                desc = st.get("desc")
                if isinstance(sid, str) and sid.strip():
                    toks.append(sid.strip())
                elif isinstance(desc, str) and desc.strip():
                    toks.append(f"s{i+1}:{desc.strip()}")
                else:
                    toks.append(f"s{i+1}")
            else:
                toks.append(f"s{i+1}")
    return toks

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def write_text(path: str, s: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)

def write_bytes(path: str, b: bytes) -> None:
    with open(path, "wb") as f:
        f.write(b)

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="rrr", add_help=True)
    sub = ap.add_subparsers(dest="cmd")

    r = sub.add_parser("render", help="render a recipe to evidence outputs")
    r.add_argument("recipe", help="path to recipe (.yaml/.yml/.json)")
    r.add_argument("--evd", default="", help="evidence dir (default: ~/.hee/evidence/rrr-run.<utc>)")

    args = ap.parse_args(argv)

    if args.cmd != "render":
        ap.print_help()
        return 0

    recipe_path = args.recipe
    evd = args.evd.strip()
    if not evd:
        evd = os.path.expanduser(f"~/.hee/evidence/rrr-run.{utc_stamp()}")
    evd = os.path.expanduser(evd)
    ensure_dir(evd)

    notes: list[str] = []

    try:
        raw = read_recipe(recipe_path)
    except Exception as e:
        return die(f"read failed: {e}")

    if not isinstance(raw, dict):
        notes.append("recipe_not_mapping: wrapped into {'value': ...}")
        raw = {"value": raw}

    canon = canonicalize(raw)
    canon_json = json.dumps(canon, indent=2, sort_keys=True) + "\n"
    canon_bytes = canon_json.encode("utf-8")

    rid = sha256_hex(canon_bytes)

    nm = canon.get("name") if isinstance(canon.get("name"), str) else "rrr"
    stem = f"{slug(nm)}.{rid[:12]}"

    toks = compute_tokens(canon)

    write_bytes(os.path.join(evd, "canonical.json"), canon_bytes)
    write_text(os.path.join(evd, "recipe_id.txt"), rid + "\n")
    write_text(os.path.join(evd, "stem.txt"), stem + "\n")
    write_text(os.path.join(evd, "tokens.txt"), "\n".join(toks) + ("\n" if toks else ""))
    write_text(os.path.join(evd, "notes.txt"), "\n".join(notes) + ("\n" if notes else ""))

    # tiny manifest
    manifest = {
        "rrr": "v0",
        "recipe_path": recipe_path,
        "evidence_dir": evd,
        "stem": stem,
        "recipe_id": rid,
        "files": ["canonical.json", "recipe_id.txt", "stem.txt", "tokens.txt", "notes.txt"],
    }
    write_text(os.path.join(evd, "manifest.json"), json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(evd)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
