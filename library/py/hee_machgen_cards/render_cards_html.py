#!/usr/bin/env python3
import argparse
import html
from pathlib import Path
from typing import List, Tuple, Dict

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
:root {
  --bg: #ffffff;
  --fg: #111111;
  --muted: #555555;
  --border: #00000022;
  --card: #ffffff;
  --code-bg: #f6f8fa;
  --link: #0969da;
  --btn-bg: #00000008;
  --btn-fg: var(--fg);
  --toast-bg: #111111;
  --toast-fg: #ffffff;
  color-scheme: light;
}
:root[data-theme="dark"] {
  --bg: #0d1117;
  --fg: #c9d1d9;
  --muted: #8b949e;
  --border: #30363d;
  --card: #161b22;
  --code-bg: #0b1220;
  --link: #58a6ff;
  --btn-bg: #30363d;
  --btn-fg: var(--fg);
  --toast-bg: #c9d1d9;
  --toast-fg: #0d1117;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; padding: 0; background: var(--bg); color: var(--fg); }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
header { padding: 16px 20px; border-bottom: 1px solid var(--border); background: var(--bg); position: sticky; top: 0; z-index: 10; }
nav { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
main { padding: 18px 20px; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(260px, 1fr)); gap: 12px; }
@media (max-width: 980px) { .grid { grid-template-columns: repeat(2, minmax(240px, 1fr)); } }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }
.card { border: 1px solid var(--border); border-radius: 14px; padding: 12px; background: var(--card); }
.card h3 { margin: 0 0 8px 0; font-size: 16px; }
.small { opacity: 0.8; font-size: 12px; color: var(--muted); }
pre { overflow: auto; padding: 12px; border-radius: 12px; border: 1px solid var(--border); background: var(--code-bg); }
.toolbar { display: flex; gap: 10px; align-items: center; justify-content: space-between; margin: 10px 0; }
.btn {
  border: 1px solid var(--border);
  background: var(--btn-bg);
  color: var(--btn-fg);
  padding: 6px 10px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
}
.btn:hover { filter: brightness(1.05); }
input[type="search"]{
  width: min(720px, 100%);
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--fg);
}
footer { padding: 14px 20px; border-top: 1px solid var(--border); opacity: 0.85; font-size: 12px; color: var(--muted); background: var(--bg); }
.toast {
  position: fixed;
  right: 16px;
  bottom: 16px;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--toast-bg);
  color: var(--toast-fg);
  border: 1px solid var(--border);
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 140ms ease, transform 140ms ease;
  pointer-events: none;
}
.toast.show { opacity: 1; transform: translateY(0); }
"""

# highlight.js dual theme (light + dark); swap via disabled attr
HLJS = """
<link id="hljs-light" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
<link id="hljs-dark" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" disabled>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/yaml.min.js"></script>
"""

JS = r"""
<script>
(function(){
  function prefersDark(){
    try { return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches; }
    catch (e) { return false; }
  }

  function applyTheme(theme){
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('hee_theme', theme); } catch (e) {}
    var light = document.getElementById('hljs-light');
    var dark = document.getElementById('hljs-dark');
    if (light && dark) {
      if (theme === 'dark') { dark.disabled = false; light.disabled = true; }
      else { dark.disabled = true; light.disabled = false; }
    }
  }

  function currentTheme(){
    var stored = null;
    try { stored = localStorage.getItem('hee_theme'); } catch (e) {}
    if (stored === 'light' || stored === 'dark') return stored;
    return prefersDark() ? 'dark' : 'light';
  }

  function toast(msg){
    var t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(function(){ t.classList.remove('show'); }, 900);
  }

  window.hee = window.hee || {};
  window.hee.applyTheme = applyTheme;
  window.hee.toast = toast;

  applyTheme(currentTheme());

  document.addEventListener('DOMContentLoaded', function(){
    var btn = document.getElementById('themeToggle');
    if (btn) {
      btn.addEventListener('click', function(){
        var now = document.documentElement.dataset.theme || 'light';
        applyTheme(now === 'dark' ? 'light' : 'dark');
      });
    }

    // Highlight
    try { if (window.hljs) { window.hljs.highlightAll(); } } catch (e) {}

    // Copy buttons
    document.querySelectorAll('button.copyBtn').forEach(function(b){
      b.addEventListener('click', function(){
        var sel = b.getAttribute('data-copy');
        var el = sel ? document.querySelector(sel) : null;
        var text = el ? el.innerText : '';
        if (!text) { toast('nothing to copy'); return; }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function(){ toast('copied'); }, function(){ toast('copy failed'); });
        } else {
          try {
            var ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            toast('copied');
          } catch (e) { toast('copy failed'); }
        }
      });
    });

    // Search (root page)
    var q = document.getElementById('search');
    if (q) {
      q.addEventListener('input', function(){
        var v = (q.value || '').toLowerCase();
        document.querySelectorAll('[data-search-item="1"]').forEach(function(it){
          var name = (it.getAttribute('data-name') || '').toLowerCase();
          var kind = (it.getAttribute('data-kind') || '').toLowerCase();
          var show = !v || name.indexOf(v) !== -1 || kind.indexOf(v) !== -1;
          it.style.display = show ? '' : 'none';
        });
      });
    }
  });
})();
</script>
"""

def render_item_page(title: str, rel_home: str, raw_text: str, note: str) -> str:
    safe = html.escape(raw_text)
    code_id = "codeblock"
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
  {HLJS}
</head>
<body>
<header>
  <div class="small">{html.escape(note)}</div>
  <div class="toolbar">
    <div>
      <h2 style="margin:0">{html.escape(title)}</h2>
      <nav style="margin-top:6px">
        <a href="{rel_home}index.html">home</a>
      </nav>
    </div>
    <div style="display:flex; gap:8px; align-items:center;">
      <button class="btn" id="themeToggle" type="button">theme</button>
      <button class="btn copyBtn" type="button" data-copy="#{code_id}">copy</button>
    </div>
  </div>
</header>
<main>
  <pre><code id="{code_id}" class="language-yaml">{safe}</code></pre>
</main>
<footer>hee ui v0: dark toggle + copy + hljs. Next: registrar + trace_chain + gh_link.</footer>
<div id="toast" class="toast" aria-live="polite"></div>
{JS}
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
  <div class="toolbar">
    <div>
      <h2 style="margin:0">{html.escape(section)}</h2>
      <nav style="margin-top:6px">
        <a href="../index.html">home</a>
        <a href="../cards/index.html">cards</a>
        <a href="../pills/index.html">pills</a>
        <a href="../registries/index.html">registries</a>
      </nav>
    </div>
    <button class="btn" id="themeToggle" type="button">theme</button>
  </div>
</header>
<main>
  <div class="grid">
    {cards_html}
  </div>
</main>
<footer>hee ui v0: section index (shows up to 9 by default).</footer>
<div id="toast" class="toast" aria-live="polite"></div>
{JS}
</body>
</html>
"""

def render_root_index(note: str, search_items_html: str) -> str:
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
  <div class="toolbar">
    <div>
      <h2 style="margin:0">HEE Battle Center</h2>
      <nav style="margin-top:6px">
        <a href="cards/index.html">cards</a>
        <a href="pills/index.html">pills</a>
        <a href="registries/index.html">registries</a>
      </nav>
    </div>
    <button class="btn" id="themeToggle" type="button">theme</button>
  </div>
</header>
<main>
  <input id="search" type="search" placeholder="search cards/pills/registries (type to filter)" />
  <div style="height:12px"></div>
  <div class="grid">
    {search_items_html}
  </div>
</main>
<footer>v0: html render + tiny server. Next: registrar + trace_chain + gh_link.</footer>
<div id="toast" class="toast" aria-live="polite"></div>
{JS}
</body>
</html>
"""

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="repo root (default .)")
    ap.add_argument("--out-root", default="generated/html", help="output root")
    ap.add_argument("--limit", type=int, default=9, help="items per section index")
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

    note = "repo-only render; bind server to 127.0.0.1; uid/provenance planned"
    if git_head:
        note = note + f"; git_head={git_head}"

    # Generate all item pages (so search links always work), but keep section index limited.
    search_items: List[Dict[str, str]] = []

    for section, src_dir, dst_dir in sections:
        dst_dir.mkdir(parents=True, exist_ok=True)

        if not src_dir.exists():
            _write_file(dst_dir / "index.html", render_index_page(section, [], note + f"; missing={src_dir}"))
            continue

        all_paths = sorted([p for p in src_dir.glob("*.y*ml") if p.is_file()])
        index_paths = all_paths[: max(0, args.limit)]

        # Create pages for all (search), collect index list for first N
        index_items: List[Tuple[str, str]] = []
        for p in all_paths:
            raw = _read_text(p)
            pretty, used_yaml = _try_yaml_pretty(raw)
            used = "yaml_pretty" if used_yaml else "raw_text"
            title = p.name
            page_name = p.name + ".html"
            _write_file(dst_dir / page_name, render_item_page(title, "../", pretty, note + f"; mode={used}"))
            search_items.append({"kind": section, "name": title, "href": f"{section}/{page_name}"})

        for p in index_paths:
            index_items.append((p.name, p.name + ".html"))

        _write_file(dst_dir / "index.html", render_index_page(section, index_items, note))

    # Root index with search grid
    search_items = sorted(search_items, key=lambda x: (x["kind"], x["name"]))
    cards_html = []
    for it in search_items:
        kind = it["kind"]
        name = it["name"]
        href = it["href"]
        cards_html.append(
            f'<div class="card" data-search-item="1" data-kind="{html.escape(kind)}" data-name="{html.escape(name)}">'
            f'<h3><a href="{html.escape(href)}">{html.escape(name)}</a></h3>'
            f'<div class="small">{html.escape(kind)}</div>'
            f'</div>'
        )
    _write_file(out_root / "index.html", render_root_index(note, "\n".join(cards_html)))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
