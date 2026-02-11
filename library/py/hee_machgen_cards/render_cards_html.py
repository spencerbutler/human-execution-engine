#!/usr/bin/env python3
import argparse
import html
import os
from pathlib import Path
from typing import List, Tuple

def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def _try_yaml_pretty(text: str) -> Tuple[str, bool]:
    try:
        import yaml  # type: ignore
    except Exception:
        return text, False

    try:
        obj = yaml.safe_load(text)
        pretty = yaml.safe_dump(obj, sort_keys=False, width=120)
        return pretty, True
    except Exception:
        return text, False

def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

CSS = """
:root { color-scheme: light dark; }
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; padding: 0; }
header { padding: 16px 20px; border-bottom: 1px solid #9993; }
nav a { margin-right: 12px; text-decoration: none; }
main { padding: 18px 20px; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(260px, 1fr)); gap: 12px; }
.card { border: 1px solid #9993; border-radius: 14px; padding: 12px; }
.card h3 { margin: 0 0 8px 0; font-size: 16px; }
.small { opacity: 0.75; font-size: 12px; }
pre { overflow: auto; padding: 12px; border-radius: 12px; border: 1px solid #9993; }
footer { padding: 14px 20px; border-top: 1px solid #9993; opacity: 0.8; font-size: 12px; }
"""

def render_item_page(title: str, rel_home: str, raw_text: str, note: str) -> str:
    safe = html.escape(raw_text)
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
<header>
  <div class="small">{html.escape(note)}</div>
  <h2>{html.escape(title)}</h2>
  <nav>
    <a href="{rel_home}index.html">home</a>
  </nav>
</header>
<main>
  <pre>{safe}</pre>
</main>
<footer>hee-machgen-cards: html render (v0). argv-only contract; shellboss runner planned.</footer>
</body>
</html>
"""

def render_index_page(section: str, items: List[Tuple[str, str]], note: str) -> str:
    cards = []
    for title, href in items:
        cards.append(
            f'<div class="card"><h3><a href="{html.escape(href)}">{html.escape(title)}</a></h3>'
            f'<div class="small">{html.escape(section)}</div></div>'
        )
    cards_html = "\n".join(cards)
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(section)}</title>
  <style>{CSS}</style>
</head>
<body>
<header>
  <div class="small">{html.escape(note)}</div>
  <h2>{html.escape(section)}</h2>
  <nav>
    <a href="../index.html">home</a>
    <a href="../cards/index.html">cards</a>
    <a href="../pills/index.html">pills</a>
    <a href="../registries/index.html">registries</a>
  </nav>
</header>
<main>
  <div class="grid">
    {cards_html}
  </div>
</main>
<footer>hee-machgen-cards: index (v0). default shows up to 9 items per section.</footer>
</body>
</html>
"""

def render_root_index(note: str) -> str:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HEE Battle Center</title>
  <style>{CSS}</style>
</head>
<body>
<header>
  <div class="small">{html.escape(note)}</div>
  <h2>HEE Battle Center</h2>
  <nav>
    <a href="cards/index.html">cards</a>
    <a href="pills/index.html">pills</a>
    <a href="registries/index.html">registries</a>
  </nav>
</header>
<main>
  <p>Dead simple UI. Rendered from repo YAML. Images later.</p>
  <ul>
    <li><a href="cards/index.html">cards</a></li>
    <li><a href="pills/index.html">pills</a></li>
    <li><a href="registries/index.html">registries</a></li>
  </ul>
</main>
<footer>v0: html render + tiny server. Next: registrar + trace_chain + gh_link.</footer>
</body>
</html>
"""

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="repo root (default .)")
    ap.add_argument("--out-root", default="generated/html", help="output root")
    ap.add_argument("--limit", type=int, default=9, help="items per section")
    ap.add_argument("--git-head", default="", help="optional git head (for provenance note)")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    out_root = Path(args.out_root).resolve()
    git_head = args.git_head.strip()

    sections = [
        ("cards", repo / "hee" / "cards", out_root / "cards"),
        ("pills", repo / "hee" / "pills", out_root / "pills"),
        ("registries", repo / "hee" / "registries", out_root / "registries"),
    ]

    note = "repo-only render; bind server to 127.0.0.1; provenance tokens planned"
    if git_head:
        note = note + f"; git_head={git_head}"

    _write_file(out_root / "index.html", render_root_index(note))

    for section, src_dir, dst_dir in sections:
        dst_dir.mkdir(parents=True, exist_ok=True)
        items: List[Tuple[str, str]] = []

        if not src_dir.exists():
            _write_file(dst_dir / "index.html", render_index_page(section, [], note + f"; missing={src_dir}"))
            continue

        paths = sorted([p for p in src_dir.glob("*.y*ml") if p.is_file()])
        paths = paths[: max(0, args.limit)]

        for p in paths:
            raw = _read_text(p)
            pretty, used_yaml = _try_yaml_pretty(raw)
            used = "yaml_pretty" if used_yaml else "raw_text"
            title = p.name
            page_name = p.name + ".html"
            _write_file(dst_dir / page_name, render_item_page(title, "../", pretty, note + f"; mode={used}"))
            items.append((title, page_name))

        _write_file(dst_dir / "index.html", render_index_page(section, items, note))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
