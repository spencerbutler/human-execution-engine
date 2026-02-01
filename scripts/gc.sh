#!/usr/bin/env bash
#!/usr/bin/env bash
set -euo pipefail
set -euo pipefail


rb=""
rb=""
b=""
b=""




# ============================================================
# ============================================================
# GC Report Pack — repo hygiene monitoring (recommend-only)
# GC Report Pack — repo hygiene monitoring (recommend-only)
# Outputs per run:
# Outputs per run:
#   var/gc/runs/YYYY-MM-DD/{README.md,report.html,metrics.json,reports/*,proposed_actions/*}
#   var/gc/runs/YYYY-MM-DD/{README.md,report.html,metrics.json,reports/*,proposed_actions/*}
#   var/gc/latest -> current run
#   var/gc/latest -> current run
#
#
# Safety:
# Safety:
#   - Default recommend-only
#   - Default recommend-only
#   - Apply mode requires: GC_APPLY=1, clean tree, on main
#   - Apply mode requires: GC_APPLY=1, clean tree, on main
#   - Branch deletion NEVER executed automatically; only proposed script
#   - Branch deletion NEVER executed automatically; only proposed script
# ============================================================
# ============================================================


# ----------------------
# ----------------------
# Config (env override)
# Config (env override)
# ----------------------
# ----------------------
GC_ROOT="${GC_ROOT:-$(pwd)}"
GC_ROOT="${GC_ROOT:-$(pwd)}"
GC_OUT_BASE="${GC_OUT_BASE:-$GC_ROOT/var/gc}"
GC_OUT_BASE="${GC_OUT_BASE:-$GC_ROOT/var/gc}"
GC_DATE="${GC_DATE:-$(date +%F)}"
GC_DATE="${GC_DATE:-$(date +%F)}"
GC_RUN_ID="${GC_RUN_ID:-$(date +%Y%m%d)-$(date +%H%M%S)-$$}"
GC_RUN_ID="${GC_RUN_ID:-$(date +%Y%m%d)-$(date +%H%M%S)-$$}"
GC_APPLY="${GC_APPLY:-0}"                         # must remain 0 for cron/overnight
GC_APPLY="${GC_APPLY:-0}"                         # must remain 0 for cron/overnight
GC_EXCLUDE_DIRS="${GC_EXCLUDE_DIRS:-}"            # colon-separated relative dirs to exclude (e.g. "generated:dist:var")
GC_EXCLUDE_DIRS="${GC_EXCLUDE_DIRS:-}"            # colon-separated relative dirs to exclude (e.g. "generated:dist:var")
GC_TIMEOUT_PER_TASK_SECONDS="${GC_TIMEOUT_PER_TASK_SECONDS:-0}"  # 0 disables soft timeout
GC_TIMEOUT_PER_TASK_SECONDS="${GC_TIMEOUT_PER_TASK_SECONDS:-0}"  # 0 disables soft timeout


LARGE_FILE_MB="${LARGE_FILE_MB:-50}"
LARGE_FILE_MB="${LARGE_FILE_MB:-50}"
STALE_BRANCH_DAYS="${STALE_BRANCH_DAYS:-30}"
STALE_BRANCH_DAYS="${STALE_BRANCH_DAYS:-30}"


# Junk Score weights (stable & logged)
# Junk Score weights (stable & logged)
W_CRUFT_BYTES="${W_CRUFT_BYTES:-0.35}"
W_CRUFT_BYTES="${W_CRUFT_BYTES:-0.35}"
W_WEIRD_PATHS="${W_WEIRD_PATHS:-0.20}"
W_WEIRD_PATHS="${W_WEIRD_PATHS:-0.20}"
W_LARGE_BYTES="${W_LARGE_BYTES:-0.25}"
W_LARGE_BYTES="${W_LARGE_BYTES:-0.25}"
W_STALE_BRANCHES="${W_STALE_BRANCHES:-0.20}"
W_STALE_BRANCHES="${W_STALE_BRANCHES:-0.20}"


# Overnight niceness
# Overnight niceness
NICE_CMD="${NICE_CMD:-nice -n 10}"
NICE_CMD="${NICE_CMD:-nice -n 10}"
IONICE_CMD="${IONICE_CMD:-ionice -c2 -n7}"
IONICE_CMD="${IONICE_CMD:-ionice -c2 -n7}"


# Derived paths
# Derived paths
GC_OUT="$GC_OUT_BASE/runs/$GC_DATE"
GC_OUT="$GC_OUT_BASE/runs/$GC_DATE"
GC_LATEST="$GC_OUT_BASE/latest"
GC_LATEST="$GC_OUT_BASE/latest"
GC_CACHE="$GC_OUT_BASE/cache"
GC_CACHE="$GC_OUT_BASE/cache"
GC_REPORTS="$GC_OUT/reports"
mkdir -p "\"\nGC_REPORTS="$GC_OUT/reports"
GC_PROPOSE="$GC_OUT/proposed_actions"
GC_PROPOSE="$GC_OUT/proposed_actions"
GC_README="$GC_OUT/README.md"
GC_README="$GC_OUT/README.md"
GC_HTML="$GC_OUT/report.html"
GC_HTML="$GC_OUT/report.html"
GC_METRICS="$GC_OUT/metrics.json"
GC_METRICS="$GC_OUT/metrics.json"


mkdir -p "$GC_REPORTS" "$GC_PROPOSE" "$GC_CACHE"
mkdir -p "$GC_REPORTS" "$GC_PROPOSE" "$GC_CACHE"
ln -sfn "$GC_OUT" "$GC_LATEST"
ln -sfn "$GC_OUT" "$GC_LATEST"


# ----------------------
# ----------------------
# Utilities
# Utilities
# ----------------------
# ----------------------
ts() { date -Is; }
ts() { date -Is; }
log() { printf "[%s] %s\n" "$(ts)" "$*"; }
log() { printf "[%s] %s\n" "$(ts)" "$*"; }
die() { echo "ERROR: $*" >&2; exit 2; }
die() { echo "ERROR: $*" >&2; exit 2; }


have() { command -v "$1" >/dev/null 2>&1; }
have() { command -v "$1" >/dev/null 2>&1; }


# Soft timeout wrapper (best-effort)
# Soft timeout wrapper (best-effort)
run_task() {
run_task() {
  local name="$1"; shift
  local name="$1"; shift
  local start_ns end_ns dur_s
  local start_ns end_ns dur_s
  start_ns="$(date +%s%N 2>/dev/null || python3 - <<'PY'
  start_ns="$(date +%s%N 2>/dev/null || python3 - <<'PY'
import time; print(int(time.time()*1e9))
import time; print(int(time.time()*1e9))
PY
PY
)"
)"


  if [[ "$GC_TIMEOUT_PER_TASK_SECONDS" -gt 0 ]] && have timeout; then
  if [[ "$GC_TIMEOUT_PER_TASK_SECONDS" -gt 0 ]] && have timeout; then
    # timeout returns 124 on timeout; do not fail the whole run
    # timeout returns 124 on timeout; do not fail the whole run
    if ! $NICE_CMD $IONICE_CMD timeout "$GC_TIMEOUT_PER_TASK_SECONDS" bash -c "$1"; then
    if ! $NICE_CMD $IONICE_CMD timeout "$GC_TIMEOUT_PER_TASK_SECONDS" bash -c "$1"; then
      local rc=$?
      local rc=$?
      if [[ "$rc" == "124" ]]; then
      if [[ "$rc" == "124" ]]; then
        echo "$name|timeout|$GC_TIMEOUT_PER_TASK_SECONDS" >> "$GC_REPORTS/_task_status.txt"
        echo "$name|timeout|$GC_TIMEOUT_PER_TASK_SECONDS" >> "$GC_REPORTS/_task_status.txt"
      else
      else
        echo "$name|error|$rc" >> "$GC_REPORTS/_task_status.txt"
        echo "$name|error|$rc" >> "$GC_REPORTS/_task_status.txt"
      fi
      fi
    else
    else
      echo "$name|ok|0" >> "$GC_REPORTS/_task_status.txt"
      echo "$name|ok|0" >> "$GC_REPORTS/_task_status.txt"
    fi
    fi
  else
  else
    if ! $NICE_CMD $IONICE_CMD bash -c "$1"; then
    if ! $NICE_CMD $IONICE_CMD bash -c "$1"; then
      echo "$name|error|$?" >> "$GC_REPORTS/_task_status.txt"
      echo "$name|error|$?" >> "$GC_REPORTS/_task_status.txt"
    else
    else
      echo "$name|ok|0" >> "$GC_REPORTS/_task_status.txt"
      echo "$name|ok|0" >> "$GC_REPORTS/_task_status.txt"
    fi
    fi
  fi
  fi


  end_ns="$(date +%s%N 2>/dev/null || python3 - <<'PY'
  end_ns="$(date +%s%N 2>/dev/null || python3 - <<'PY'
import time; print(int(time.time()*1e9))
import time; print(int(time.time()*1e9))
PY
PY
)"
)"
  dur_s=$(( (end_ns - start_ns) / 1000000000 ))
  dur_s=$(( (end_ns - start_ns) / 1000000000 ))
  echo "$name|$dur_s" >> "$GC_REPORTS/_task_durations.txt"
  echo "$name|$dur_s" >> "$GC_REPORTS/_task_durations.txt"
}
}


require_repo_root() {
require_repo_root() {
  have git || die "git is required"
  have git || die "git is required"
  git -C "$GC_ROOT" rev-parse --show-toplevel >/dev/null 2>&1 || die "Not a git repo: $GC_ROOT"
  git -C "$GC_ROOT" rev-parse --show-toplevel >/dev/null 2>&1 || die "Not a git repo: $GC_ROOT"
  local top; top="$(git -C "$GC_ROOT" rev-parse --show-toplevel)"
  local top; top="$(git -C "$GC_ROOT" rev-parse --show-toplevel)"
  [[ "$top" == "$GC_ROOT" ]] || die "GC_ROOT must be repo root. top=$top GC_ROOT=$GC_ROOT"
  [[ "$top" == "$GC_ROOT" ]] || die "GC_ROOT must be repo root. top=$top GC_ROOT=$GC_ROOT"
}
}


require_clean_main_if_apply() {
require_clean_main_if_apply() {
  if [[ "$GC_APPLY" != "1" ]]; then return 0; fi
  if [[ "$GC_APPLY" != "1" ]]; then return 0; fi
  local branch
  local branch
  branch="$(git -C "$GC_ROOT" rev-parse --abbrev-ref HEAD)"
  branch="$(git -C "$GC_ROOT" rev-parse --abbrev-ref HEAD)"
  [[ "$branch" == "main" ]] || die "Apply mode requires branch=main (got: $branch)"
  [[ "$branch" == "main" ]] || die "Apply mode requires branch=main (got: $branch)"
  git -C "$GC_ROOT" diff --quiet || die "Apply mode requires clean working tree"
  git -C "$GC_ROOT" diff --quiet || die "Apply mode requires clean working tree"
  git -C "$GC_ROOT" diff --cached --quiet || die "Apply mode requires clean index"
  git -C "$GC_ROOT" diff --cached --quiet || die "Apply mode requires clean index"
}
}


# Exclude find patterns
# Exclude find patterns
build_find_excludes() {
build_find_excludes() {
  local ex=()
  local ex=()
  ex+=( -path "./.git" -prune )
  ex+=( -path "./.git" -prune )
  if [[ -n "$GC_EXCLUDE_DIRS" ]]; then
  if [[ -n "$GC_EXCLUDE_DIRS" ]]; then
    IFS=':' read -r -a parts <<<"$GC_EXCLUDE_DIRS"
    IFS=':' read -r -a parts <<<"$GC_EXCLUDE_DIRS"
    for d in "${parts[@]}"; do
    for d in "${parts[@]}"; do
      [[ -z "$d" ]] && continue
      [[ -z "$d" ]] && continue
      # prune ./dir
      # prune ./dir
      ex+=( -o -path "./$d" -prune )
      ex+=( -o -path "./$d" -prune )
    done
    done
  fi
  fi
  printf "%s " "${ex[@]}"
  printf "%s " "${ex[@]}"
}
}


# Prior run detection
# Prior run detection
find_previous_run_dir() {
find_previous_run_dir() {
  if [[ ! -d "$GC_OUT_BASE/runs" ]]; then
  if [[ ! -d "$GC_OUT_BASE/runs" ]]; then
    echo ""
    echo ""
    return 0
    return 0
  fi
  fi
  # pick most recent run directory != current date
  # pick most recent run directory != current date
  ls -1 "$GC_OUT_BASE/runs" 2>/dev/null \
  ls -1 "$GC_OUT_BASE/runs" 2>/dev/null \
    | sort -r \
    | sort -r \
    | awk -v cur="$GC_DATE" '$0!=cur {print; exit}' \
    | awk -v cur="$GC_DATE" '$0!=cur {print; exit}' \
    | awk -v base="$GC_OUT_BASE/runs" '{print base "/" $0}'
    | awk -v base="$GC_OUT_BASE/runs" '{print base "/" $0}'
}
}


# ----------------------
# ----------------------
# Task: global repo metrics + cache filelist
# Task: global repo metrics + cache filelist
# ----------------------
# ----------------------
task_global_metrics() {
task_global_metrics() {
  local report="$GC_REPORTS/global.txt"
  local report="$GC_REPORTS/global.txt"
  local excludes; excludes="$(build_find_excludes)"
  local excludes; excludes="$(build_find_excludes)"


  run_task "global_metrics" "
  run_task "global_metrics" "
    set -euo pipefail
    set -euo pipefail
    cd '$GC_ROOT'
    cd '$GC_ROOT'
    {
    {
      echo 'repo_root=$GC_ROOT'
      echo 'repo_root=$GC_ROOT'
      echo 'timestamp=$(date -Is)'
      echo 'timestamp=$(date -Is)'
      echo 'git_sha='\"\$(git rev-parse HEAD)\"
      echo 'git_sha='\"\$(git rev-parse HEAD)\"
      echo 'git_branch='\"\$(git rev-parse --abbrev-ref HEAD)\"
      echo 'git_branch='\"\$(git rev-parse --abbrev-ref HEAD)\"
    } > '$report'
    } > '$report'


    # File inventory (excluding .git and excluded dirs). Cache compressed if possible.
    # File inventory (excluding .git and excluded dirs). Cache compressed if possible.
    mkdir -p '$GC_CACHE'
    mkdir -p '$GC_CACHE'
    if command -v zstd >/dev/null 2>&1; then
    if command -v zstd >/dev/null 2>&1; then
      find . $excludes -o -type f -print0 | zstd -q -T0 -19 -o '$GC_CACHE/filelist.zst' || true
      find . $excludes -o -type f -print0 | zstd -q -T0 -19 -o '$GC_CACHE/filelist.zst' || true
      echo 'filelist_cache=var/gc/cache/filelist.zst' >> '$report'
      echo 'filelist_cache=var/gc/cache/filelist.zst' >> '$report'
    elif command -v gzip >/dev/null 2>&1; then
    elif command -v gzip >/dev/null 2>&1; then
      find . $excludes -o -type f -print0 | gzip -c > '$GC_CACHE/filelist.gz' || true
      find . $excludes -o -type f -print0 | gzip -c > '$GC_CACHE/filelist.gz' || true
      echo 'filelist_cache=var/gc/cache/filelist.gz' >> '$report'
      echo 'filelist_cache=var/gc/cache/filelist.gz' >> '$report'
    else
    else
      find . $excludes -o -type f -print0 > '$GC_CACHE/filelist.bin' || true
      find . $excludes -o -type f -print0 > '$GC_CACHE/filelist.bin' || true
      echo 'filelist_cache=var/gc/cache/filelist.bin' >> '$report'
      echo 'filelist_cache=var/gc/cache/filelist.bin' >> '$report'
    fi
    fi


    # Approx counts/sizes (exclude .git and excludes)
    # Approx counts/sizes (exclude .git and excludes)
    python3 - <<'PY' >> '$report'
    python3 - <<'PY' >> '$report'
import os
import os
root = os.getcwd()
root = os.getcwd()
exclude = {'.git'}
exclude = {'.git'}
extra = os.environ.get('GC_EXCLUDE_DIRS','')
extra = os.environ.get('GC_EXCLUDE_DIRS','')
if extra:
if extra:
    exclude |= set([p.strip().lstrip('./') for p in extra.split(':') if p.strip()])
    exclude |= set([p.strip().lstrip('./') for p in extra.split(':') if p.strip()])
total_files = 0
total_files = 0
total_bytes = 0
total_bytes = 0
for dirpath, dirnames, filenames in os.walk(root):
for dirpath, dirnames, filenames in os.walk(root):
    rel = os.path.relpath(dirpath, root)
    rel = os.path.relpath(dirpath, root)
    # prune excludes
    # prune excludes
    parts = [] if rel == '.' else rel.split(os.sep)
    parts = [] if rel == '.' else rel.split(os.sep)
    if parts and parts[0] in exclude:
    if parts and parts[0] in exclude:
        dirnames[:] = []
        dirnames[:] = []
        continue
        continue
    if rel != '.' and rel.split(os.sep)[0] in exclude:
    if rel != '.' and rel.split(os.sep)[0] in exclude:
        dirnames[:] = []
        dirnames[:] = []
        continue
        continue
    # also prune .git anywhere
    # also prune .git anywhere
    dirnames[:] = [d for d in dirnames if d != '.git' and d not in exclude]
    dirnames[:] = [d for d in dirnames if d != '.git' and d not in exclude]
    for fn in filenames:
    for fn in filenames:
        if fn == '.git': continue
        if fn == '.git': continue
        p = os.path.join(dirpath, fn)
        p = os.path.join(dirpath, fn)
        try:
        try:
            st = os.stat(p)
            st = os.stat(p)
        except OSError:
        except OSError:
            continue
            continue
        total_files += 1
        total_files += 1
        total_bytes += st.st_size
        total_bytes += st.st_size
print(f'repo_total_files={total_files}')
print(f'repo_total_files={total_files}')
print(f'repo_total_bytes={total_bytes}')
print(f'repo_total_bytes={total_bytes}')
PY
PY
  "
  "
}
}


# ----------------------
# ----------------------
# Task: cruft detection
# Task: cruft detection
# ----------------------
# ----------------------
task_cruft() {
task_cruft() {
  local report="$GC_REPORTS/cruft_paths.txt"
  local report="$GC_REPORTS/cruft_paths.txt"
  local report2="$GC_REPORTS/cruft_summary.txt"
  local report2="$GC_REPORTS/cruft_summary.txt"
  local excludes; excludes="$(build_find_excludes)"
  local excludes; excludes="$(build_find_excludes)"


  run_task "cruft_scan" "
  run_task "cruft_scan" "
    set -euo pipefail
    set -euo pipefail
    cd '$GC_ROOT'
    cd '$GC_ROOT'
    find . $excludes -o -type f \\( \
    find . $excludes -o -type f \\( \
      -name '*.bak' -o -name '*~' -o -name '*.swp' -o -name '*.tmp' -o -name '*.orig' -o -name '*.rej' -o \
      -name '*.bak' -o -name '*~' -o -name '*.swp' -o -name '*.tmp' -o -name '*.orig' -o -name '*.rej' -o \
      -name '.DS_Store' -o -name 'Thumbs.db' -o -name '*.log' \
      -name '.DS_Store' -o -name 'Thumbs.db' -o -name '*.log' \
    \\) -print > '$report' || true
    \\) -print > '$report' || true


    # Fix: allow variable expansion in heredoc to resolve GC_REPORTS path
    # Fix: allow variable expansion in heredoc to resolve GC_REPORTS path
    python3 - <<PY > '$report2'
    python3 - <<PY > '$report2'
import os, json, re
import os, json, re
root = os.getcwd()
root = os.getcwd()
paths = []
paths = []
with open('$report','r',encoding='utf-8',errors='replace') as f:
with open('$report','r',encoding='utf-8',errors='replace') as f:
    for line in f:
    for line in f:
        p=line.strip()
        p=line.strip()
        if not p: continue
        if not p: continue
        paths.append(p)
        paths.append(p)
def pat(p):
def pat(p):
    base=os.path.basename(p)
    base=os.path.basename(p)
    for k in ['.bak','~','.swp','.tmp','.orig','.rej','.DS_Store','Thumbs.db','.log']:
    for k in ['.bak','~','.swp','.tmp','.orig','.rej','.DS_Store','Thumbs.db','.log']:
        if base==k or base.endswith(k): return k
        if base==k or base.endswith(k): return k
    return 'other'
    return 'other'
by_pat={}
by_pat={}
by_dir={}
by_dir={}
total_bytes=0
total_bytes=0
for p in paths:
for p in paths:
    ap=os.path.join(root,p)
    ap=os.path.join(root,p)
    try:
    try:
        sz=os.stat(ap).st_size
        sz=os.stat(ap).st_size
    except OSError:
    except OSError:
        sz=0
        sz=0
    total_bytes += sz
    total_bytes += sz
    k=pat(p)
    k=pat(p)
    by_pat.setdefault(k, {'count':0,'bytes':0})
    by_pat.setdefault(k, {'count':0,'bytes':0})
    by_pat[k]['count']+=1
    by_pat[k]['count']+=1
    by_pat[k]['bytes']+=sz
    by_pat[k]['bytes']+=sz
    d=os.path.dirname(p) or '.'
    d=os.path.dirname(p) or '.'
    by_dir.setdefault(d, {'count':0,'bytes':0})
    by_dir.setdefault(d, {'count':0,'bytes':0})
    by_dir[d]['count']+=1
    by_dir[d]['count']+=1
    by_dir[d]['bytes']+=sz
    by_dir[d]['bytes']+=sz


top_dirs=sorted(by_dir.items(), key=lambda kv: kv[1]['bytes'], reverse=True)[:20]
top_dirs=sorted(by_dir.items(), key=lambda kv: kv[1]['bytes'], reverse=True)[:20]
top_pats=sorted(by_pat.items(), key=lambda kv: kv[1]['bytes'], reverse=True)
top_pats=sorted(by_pat.items(), key=lambda kv: kv[1]['bytes'], reverse=True)
print(f'cruft_file_count_total={len(paths)}')
print(f'cruft_file_count_total={len(paths)}')
print(f'cruft_bytes_total={total_bytes}')
print(f'cruft_bytes_total={total_bytes}')
print('cruft_by_pattern=' + json.dumps([{ 'pattern':k, **v } for k,v in top_pats]))
print('cruft_by_pattern=' + json.dumps([{ 'pattern':k, **v } for k,v in top_pats]))
print('cruft_top_dirs_by_bytes=' + json.dumps([{ 'dir':k, **v } for k,v in top_dirs]))
print('cruft_top_dirs_by_bytes=' + json.dumps([{ 'dir':k, **v } for k,v in top_dirs]))
PY
PY
  "
  "
}
}


# ----------------------
# ----------------------
# Task: weird paths
# Task: weird paths
# ----------------------
# ----------------------
task_weird_paths() {
task_weird_paths() {
  local report="$GC_REPORTS/weird_paths.txt"
  local report="$GC_REPORTS/weird_paths.txt"
  local mapping="$GC_REPORTS/weird_paths_rename_map.txt"
  local mapping="$GC_REPORTS/weird_paths_rename_map.txt"


  run_task "weird_paths" "
  run_task "weird_paths" "
    set -euo pipefail
    set -euo pipefail
    cd '$GC_ROOT'
    cd '$GC_ROOT'
    { git ls-files -z; git ls-files --others --exclude-standard -z; } \
    { git ls-files -z; git ls-files --others --exclude-standard -z; } \
      | python3 - <<'PY' > '$report'
      | python3 - <<'PY' > '$report'
import sys, unicodedata
import sys, unicodedata
data = sys.stdin.buffer.read().split(b'\x00')
data = sys.stdin.buffer.read().split(b'\x00')
def classify(s: str):
def classify(s: str):
    cats=set()
    cats=set()
    if s.endswith(' '): cats.add('trailing_space')
    if s.endswith(' '): cats.add('trailing_space')
    if any(ord(c) < 32 or ord(c) == 127 for c in s): cats.add('control_chars')
    if any(ord(c) < 32 or ord(c) == 127 for c in s): cats.add('control_chars')
    if '\t' in s or '\r' in s or '\n' in s: cats.add('tabs_newlines')
    if '\t' in s or '\r' in s or '\n' in s: cats.add('tabs_newlines')
    # suspicious non-printing unicode
    # suspicious non-printing unicode
    for c in s:
    for c in s:
        if unicodedata.category(c) in ('Cf',):  # format chars
        if unicodedata.category(c) in ('Cf',):  # format chars
            cats.add('format_chars')
            cats.add('format_chars')
    return cats
    return cats


out=[]
out=[]
for p in data:
for p in data:
    if not p: continue
    if not p: continue
    s=p.decode('utf-8', errors='replace')
    s=p.decode('utf-8', errors='replace')
    cats=classify(s)
    cats=classify(s)
    if cats:
    if cats:
        out.append((s, sorted(cats)))
        out.append((s, sorted(cats)))
for s,cats in out:
for s,cats in out:
    sys.stdout.write(s + '\t' + ','.join(cats) + '\n')
    sys.stdout.write(s + '\t' + ','.join(cats) + '\n')
PY
PY


    # Proposed rename mapping (recommend-only)
    # Proposed rename mapping (recommend-only)
    python3 - <<'PY' > '$mapping'
    python3 - <<'PY' > '$mapping'
import re, sys
import re, sys
def normalize(name: str) -> str:
def normalize(name: str) -> str:
    # replace control chars and whitespace oddities with underscores
    # replace control chars and whitespace oddities with underscores
    name = ''.join('_' if (ord(c)<32 or ord(c)==127) else c for c in name)
    name = ''.join('_' if (ord(c)<32 or ord(c)==127) else c for c in name)
    name = name.replace('\t','_').replace('\r','_').replace('\n','_')
    name = name.replace('\t','_').replace('\r','_').replace('\n','_')
    name = re.sub(r'\s+$','',name)           # drop trailing spaces
    name = re.sub(r'\s+$','',name)           # drop trailing spaces
    name = re.sub(r'__+','_',name)
    name = re.sub(r'__+','_',name)
    return name
    return name


lines=open('$report','r',encoding='utf-8',errors='replace').read().splitlines()
lines=open('$report','r',encoding='utf-8',errors='replace').read().splitlines()
for line in lines:
for line in lines:
    if not line.strip(): continue
    if not line.strip(): continue
    path=line.split('\t',1)[0]
    path=line.split('\t',1)[0]
    n=normalize(path)
    n=normalize(path)
    if n!=path:
    if n!=path:
        print(f'{path} -> {n}')
        print(f'{path} -> {n}')
PY
PY
  "
  "
}
}


# ----------------------
# ----------------------
# Task: branch hygiene (recommend-only + proposed script)
# Task: branch hygiene (recommend-only + proposed script)
# ----------------------
# ----------------------
task_branches() {
task_branches() {
  local report="$GC_REPORTS/branches.txt"
  local report="$GC_REPORTS/branches.txt"
  local propose="$GC_PROPOSE/delete_merged_remote_branches.sh"
  local propose="$GC_PROPOSE/delete_merged_remote_branches.sh"
  local stale_report="$GC_REPORTS/branches_stale.txt"
  local stale_report="$GC_REPORTS/branches_stale.txt"


  run_task "branch_hygiene" "
  run_task "branch_hygiene" "
    set -eo pipefail
    set -eo pipefail
    cd '$GC_ROOT'
    cd '$GC_ROOT'
    git fetch --prune >/dev/null 2>&1 || true
    git fetch --prune >/dev/null 2>&1 || true


    {
    {
      echo 'local_branches_total='\"\$(git branch --format='%(refname:short)' | wc -l | tr -d ' ')\"
      echo 'local_branches_total='\"\$(git branch --format='%(refname:short)' | wc -l | tr -d ' ')\"
      echo 'remote_branches_total='\"\$(git branch -r --format='%(refname:short)' | wc -l | tr -d ' ')\"
      echo 'remote_branches_total='\"\$(git branch -r --format='%(refname:short)' | wc -l | tr -d ' ')\"
    } > '$report'
    } > '$report'


    echo 'merged_remote_branches_into_origin/main:' >> '$report'
    echo 'merged_remote_branches_into_origin/main:' >> '$report'
    git branch -r --merged origin/main | sed 's/^  //' | grep -vE 'origin/(main|master|HEAD)\$' >> '$report' || true
    git branch -r --merged origin/main | sed 's/^  //' | grep -vE 'origin/(main|master|HEAD)\$' >> '$report' || true


    # stale branches: last commit older than STALE_BRANCH_DAYS
    # stale branches: last commit older than STALE_BRANCH_DAYS
    python3 - <<'PY' > '$stale_report'
    python3 - <<'PY' > '$stale_report'
import subprocess, datetime, os
import subprocess, datetime, os
days=int(os.environ.get('STALE_BRANCH_DAYS','30'))
days=int(os.environ.get('STALE_BRANCH_DAYS','30'))
cut=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
cut=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
cmd=['git','for-each-ref','--format=%(refname:short)\t%(committerdate:iso8601)','refs/heads']
cmd=['git','for-each-ref','--format=%(refname:short)\t%(committerdate:iso8601)','refs/heads']
out=subprocess.check_output(cmd, text=True, errors='replace')
out=subprocess.check_output(cmd, text=True, errors='replace')
rows=[]
rows=[]
for line in out.splitlines():
for line in out.splitlines():
    b, d = line.split('\t',1)
    b, d = line.split('\t',1)
    try:
    try:
        dt=datetime.datetime.fromisoformat(d.replace('Z','+00:00'))
        dt=datetime.datetime.fromisoformat(d.replace('Z','+00:00'))
    except Exception:
    except Exception:
        continue
        continue
    if dt < cut:
    if dt < cut:
        rows.append((dt, b))
        rows.append((dt, b))
rows.sort()
rows.sort()
for dt,b in rows:
for dt,b in rows:
    print(f'{b}\t{dt.isoformat()}')
    print(f'{b}\t{dt.isoformat()}')
PY
PY


    # Proposed deletion script (NEVER auto-run)
    # Proposed deletion script (NEVER auto-run)
    : > "$propose"
    : > "$propose"
    printf '%s\n' \
    printf '%s\n' \
      '#!/usr/bin/env bash' \
      '#!/usr/bin/env bash' \
      'set -euo pipefail' \
      'set -euo pipefail' \
      'git fetch --prune' \
      'git fetch --prune' \
      '# REVIEW BEFORE RUNNING.' \
      '# REVIEW BEFORE RUNNING.' \
      '# Deletes ONLY merged remote branches (origin/*) excluding main/master/HEAD.' \
      '# Deletes ONLY merged remote branches (origin/*) excluding main/master/HEAD.' \
      'git branch -r --merged origin/main | sed '\''s/^  //'\'' | grep -vE '\''origin/(main|master|HEAD)$'\'' | while IFS= read -r rb; do' \
      'git branch -r --merged origin/main | sed '\''s/^  //'\'' | grep -vE '\''origin/(main|master|HEAD)$'\'' | while IFS= read -r rb; do' \
      '  [[ -z ${rb:-} ]] && continue' \
      '  [[ -z ${rb:-} ]] && continue' \
      '  b=${rb#origin/}' \
      '  b=${rb#origin/}' \
      '  echo Deleting remote branch: $b' \
      '  echo Deleting remote branch: $b' \
      '  git push origin --delete $b' \
      '  git push origin --delete $b' \
      'done' \
      'done' \
      > "$propose"
      > "$propose"
    chmod +x "$propose"
    chmod +x "$propose"
  "
  "
}
}


# ----------------------
# ----------------------
# Task: large files
# Task: large files
# ----------------------
# ----------------------
task_large_files() {
task_large_files() {
  local report="$GC_REPORTS/large_files.txt"
  local report="$GC_REPORTS/large_files.txt"
  local excludes; excludes="$(build_find_excludes)"
  local excludes; excludes="$(build_find_excludes)"


  run_task "large_files" "
  run_task "large_files" "
    set -euo pipefail
    set -euo pipefail
    cd '$GC_ROOT'
    cd '$GC_ROOT'
    # size in bytes + path, sorted desc
    # size in bytes + path, sorted desc
    python3 - <<'PY' > '$report'
    python3 - <<'PY' > '$report'
import os
import os
root=os.getcwd()
root=os.getcwd()
threshold_mb=int(os.environ.get('LARGE_FILE_MB','50'))
threshold_mb=int(os.environ.get('LARGE_FILE_MB','50'))
threshold=threshold_mb*1024*1024
threshold=threshold_mb*1024*1024
exclude={'.git'}
exclude={'.git'}
extra=os.environ.get('GC_EXCLUDE_DIRS','')
extra=os.environ.get('GC_EXCLUDE_DIRS','')
if extra:
if extra:
    exclude |= set([p.strip().lstrip('./') for p in extra.split(':') if p.strip()])
    exclude |= set([p.strip().lstrip('./') for p in extra.split(':') if p.strip()])
hits=[]
hits=[]
for dirpath, dirnames, filenames in os.walk(root):
for dirpath, dirnames, filenames in os.walk(root):
    rel=os.path.relpath(dirpath, root)
    rel=os.path.relpath(dirpath, root)
    parts=[] if rel == '.' else rel.split(os.sep)
    parts=[] if rel == '.' else rel.split(os.sep)
    if parts and parts[0] in exclude:
    if parts and parts[0] in exclude:
        dirnames[:] = []
        dirnames[:] = []
        continue
        continue
    dirnames[:] = [d for d in dirnames if d!='.git' and d not in exclude]
    dirnames[:] = [d for d in dirnames if d!='.git' and d not in exclude]
    for fn in filenames:
    for fn in filenames:
        p=os.path.join(dirpath, fn)
        p=os.path.join(dirpath, fn)
        try:
        try:
            st=os.stat(p)
            st=os.stat(p)
        except OSError:
        except OSError:
            continue
            continue
        if st.st_size >= threshold:
        if st.st_size >= threshold:
            rp=os.path.relpath(p, root)
            rp=os.path.relpath(p, root)
            hits.append((st.st_size, rp))
            hits.append((st.st_size, rp))
hits.sort(reverse=True)
hits.sort(reverse=True)
for sz, rp in hits[:200]:
for sz, rp in hits[:200]:
    print(f'{sz}\t{rp}')
    print(f'{sz}\t{rp}')
PY
PY
  "
  "
}
}


# ----------------------
# ----------------------
# Task: unused scripts (recommend-only heuristic)
# Task: unused scripts (recommend-only heuristic)
# ----------------------
# ----------------------
task_unused_scripts() {
task_unused_scripts() {
  local report="$GC_REPORTS/unused_scripts.txt"
  local report="$GC_REPORTS/unused_scripts.txt"
  local reasons="$GC_REPORTS/unused_scripts_reasons.txt"
  local reasons="$GC_REPORTS/unused_scripts_reasons.txt"


  run_task "unused_scripts" "
  run_task "unused_scripts" "
    set -euo pipefail
    set -euo pipefail
    cd '$GC_ROOT'
    cd '$GC_ROOT'
    git ls-files | grep -E '\\.(sh|py|rb|pl|js|ts)$' > $GC_REPORTS/_scripts_all.txt' || true
    git ls-files | grep -E '\\.(sh|py|rb|pl|js|ts)$' > $GC_REPORTS/_scripts_all.txt' || true


    # gather reference surfaces (best-effort)
    # gather reference surfaces (best-effort)
    touch $GC_REPORTS/_refs.txt'
    touch $GC_REPORTS/_refs.txt'
    if command -v rg >/dev/null 2>&1; then
    if command -v rg >/dev/null 2>&1; then
      rg -n --no-heading -S \"scripts/|\\./scripts/\" .github Makefile makefile docs prompts 2>/dev/null \
      rg -n --no-heading -S \"scripts/|\\./scripts/\" .github Makefile makefile docs prompts 2>/dev/null \
        | awk -F: '{print \$0}' >> $GC_REPORTS/_refs.txt' || true
        | awk -F: '{print \$0}' >> $GC_REPORTS/_refs.txt' || true
    else
    else
      # fallback: grep (no PCRE)
      # fallback: grep (no PCRE)
      grep -RIn \"scripts/\" .github Makefile makefile docs prompts 2>/dev/null >> $GC_REPORTS/_refs.txt' || true
      grep -RIn \"scripts/\" .github Makefile makefile docs prompts 2>/dev/null >> $GC_REPORTS/_refs.txt' || true
    fi
    fi


    python3 - <<'PY' > '$report'
    python3 - <<'PY' > '$report'
import os, re, subprocess, datetime
import os, re, subprocess, datetime
root=os.getcwd()
root=os.getcwd()
scripts=open($GC_REPORTS/_scripts_all.txt','r',encoding='utf-8',errors='replace').read().splitlines()
scripts=open($GC_REPORTS/_scripts_all.txt','r',encoding='utf-8',errors='replace').read().splitlines()
refs=open($GC_REPORTS/_refs.txt','r',encoding='utf-8',errors='replace').read()
refs=open($GC_REPORTS/_refs.txt','r',encoding='utf-8',errors='replace').read()
cands=[]
cands=[]
for s in scripts:
for s in scripts:
    if not s.strip(): continue
    if not s.strip(): continue
    if s in refs or ('./'+s) in refs:
    if s in refs or ('./'+s) in refs:
        continue
        continue
    cands.append(s)
    cands.append(s)
for s in cands:
for s in cands:
    print(s)
    print(s)
PY
PY


    python3 - <<'PY' > '$reasons'
    python3 - <<'PY' > '$reasons'
import os, subprocess, datetime
import os, subprocess, datetime
root=os.getcwd()
root=os.getcwd()
def git_mtime(path):
def git_mtime(path):
    try:
    try:
        out=subprocess.check_output(['git','log','-1','--format=%ct','--',path], text=True).strip()
        out=subprocess.check_output(['git','log','-1','--format=%ct','--',path], text=True).strip()
        return int(out) if out else 0
        return int(out) if out else 0
    except Exception:
    except Exception:
        return 0
        return 0
def loc(path):
def loc(path):
    try:
    try:
        with open(path,'rb') as f:
        with open(path,'rb') as f:
            return sum(1 for _ in f)
            return sum(1 for _ in f)
    except Exception:
    except Exception:
        return 0
        return 0


now=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
now=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
paths=open('$report','r',encoding='utf-8',errors='replace').read().splitlines()
paths=open('$report','r',encoding='utf-8',errors='replace').read().splitlines()
for p in paths:
for p in paths:
    ts=git_mtime(p)
    ts=git_mtime(p)
    age_days=(now-ts)//86400 if ts else 999999
    age_days=(now-ts)//86400 if ts else 999999
    lines=loc(p)
    lines=loc(p)
    # simple confidence score: older + smaller => higher confidence it's unused
    # simple confidence score: older + smaller => higher confidence it's unused
    score=0
    score=0
    score += 40 if age_days > 180 else (20 if age_days > 60 else 5)
    score += 40 if age_days > 180 else (20 if age_days > 60 else 5)
    score += 30 if lines < 80 else (15 if lines < 250 else 5)
    score += 30 if lines < 80 else (15 if lines < 250 else 5)
    score += 30  # base: not referenced
    score += 30  # base: not referenced
    if score > 100: score = 100
    if score > 100: score = 100
    print(f'{p}\tconfidence={score}\tlast_commit_age_days={age_days}\tloc={lines}\treason=not_referenced_in_common_surfaces')
    print(f'{p}\tconfidence={score}\tlast_commit_age_days={age_days}\tloc={lines}\treason=not_referenced_in_common_surfaces')
PY
PY
  "
  "
}
}


# ----------------------
# ----------------------
# Metrics + HTML + README generation
# Metrics + HTML + README generation
# ----------------------
# ----------------------
parse_kv_file() {
parse_kv_file() {
  # parse key=value lines into env-like export map (python returns json)
  # parse key=value lines into env-like export map (python returns json)
  local file="$1"
  local file="$1"
  python3 - <<PY
  python3 - <<PY
import json
import json
d={}
d={}
for line in open("$file","r",encoding="utf-8",errors="replace"):
for line in open("$file","r",encoding="utf-8",errors="replace"):
    line=line.strip()
    line=line.strip()
    if not line or line.startswith("#"): continue
    if not line or line.startswith("#"): continue
    if "=" in line:
    if "=" in line:
        k,v=line.split("=",1)
        k,v=line.split("=",1)
        d[k.strip()]=v.strip()
        d[k.strip()]=v.strip()
print(json.dumps(d))
print(json.dumps(d))
PY
PY
}
}


generate_metrics_and_reports() {
generate_metrics_and_reports() {
  local prev_dir prev_metrics
  local prev_dir prev_metrics
  prev_dir="$(find_previous_run_dir)"
  prev_dir="$(find_previous_run_dir)"
  prev_metrics=""
  prev_metrics=""
  if [[ -n "$prev_dir" ]] && [[ -f "$prev_dir/metrics.json" ]]; then
  if [[ -n "$prev_dir" ]] && [[ -f "$prev_dir/metrics.json" ]]; then
    prev_metrics="$prev_dir/metrics.json"
    prev_metrics="$prev_dir/metrics.json"
  fi
  fi


  # Gather global info
  # Gather global info
  local gkv_json
  local gkv_json
  gkv_json="$(parse_kv_file "$GC_REPORTS/global.txt")"
  gkv_json="$(parse_kv_file "$GC_REPORTS/global.txt")"
  local cruft_kv weird_count weird_by_cat large_summary branches_summary stale_count merged_count
  local cruft_kv weird_count weird_by_cat large_summary branches_summary stale_count merged_count


  cruft_kv="$(python3 - <<'PY'
  cruft_kv="$(python3 - <<'PY'
import json, re
import json, re
txt=open("$GC_REPORTS/cruft_summary.txt'","r",encoding="utf-8",errors="replace").read().splitlines()
txt=open("$GC_REPORTS/cruft_summary.txt'","r",encoding="utf-8",errors="replace").read().splitlines()
d={}
d={}
for line in txt:
for line in txt:
    if '=' in line:
    if '=' in line:
        k,v=line.split('=',1)
        k,v=line.split('=',1)
        d[k]=v
        d[k]=v
print(json.dumps(d))
print(json.dumps(d))
PY
PY
)"
)"
  weird_count="$(wc -l < "$GC_REPORTS/weird_paths.txt" | tr -d ' ')"
  weird_count="$(wc -l < "$GC_REPORTS/weird_paths.txt" | tr -d ' ')"
  weird_by_cat="$(python3 - <<'PY'
  weird_by_cat="$(python3 - <<'PY'
import collections
import collections
c=collections.Counter()
c=collections.Counter()
for line in open("$GC_REPORTS/weird_paths.txt'","r",encoding="utf-8",errors="replace"):
for line in open("$GC_REPORTS/weird_paths.txt'","r",encoding="utf-8",errors="replace"):
    line=line.strip()
    line=line.strip()
    if not line: continue
    if not line: continue
    parts=line.split('\t',1)
    parts=line.split('\t',1)
    cats=parts[1].split(',') if len(parts)>1 else []
    cats=parts[1].split(',') if len(parts)>1 else []
    for cat in cats: c[cat]+=1
    for cat in cats: c[cat]+=1
print(__import__('json').dumps(c))
print(__import__('json').dumps(c))
PY
PY
)"
)"
  large_summary="$(python3 - <<'PY'
  large_summary="$(python3 - <<'PY'
import os, json
import os, json
total=0
total=0
count=0
count=0
top=[]
top=[]
for line in open("$GC_REPORTS/large_files.txt'","r",encoding="utf-8",errors="replace"):
for line in open("$GC_REPORTS/large_files.txt'","r",encoding="utf-8",errors="replace"):
    line=line.strip()
    line=line.strip()
    if not line: continue
    if not line: continue
    sz_s, path = line.split('\t',1)
    sz_s, path = line.split('\t',1)
    sz=int(sz_s)
    sz=int(sz_s)
    total += sz
    total += sz
    count += 1
    count += 1
    if len(top)<50:
    if len(top)<50:
        top.append({'bytes':sz,'path':path})
        top.append({'bytes':sz,'path':path})
print(json.dumps({'count':count,'bytes_total':total,'top_50':top}))
print(json.dumps({'count':count,'bytes_total':total,'top_50':top}))
PY
PY
)"
)"


  branches_summary="$(python3 - <<'PY'
  branches_summary="$(python3 - <<'PY'
import re, json
import re, json
report=open("$GC_REPORTS/branches.txt'","r",encoding="utf-8",errors="replace").read().splitlines()
report=open("$GC_REPORTS/branches.txt'","r",encoding="utf-8",errors="replace").read().splitlines()
d={}
d={}
merged=[]
merged=[]
mode=None
mode=None
for line in report:
for line in report:
    if line.startswith('local_branches_total='):
    if line.startswith('local_branches_total='):
        d['local_branches_total']=int(line.split('=',1)[1])
        d['local_branches_total']=int(line.split('=',1)[1])
    elif line.startswith('remote_branches_total='):
    elif line.startswith('remote_branches_total='):
        d['remote_branches_total']=int(line.split('=',1)[1])
        d['remote_branches_total']=int(line.split('=',1)[1])
    elif line.strip()=='merged_remote_branches_into_origin/main:':
    elif line.strip()=='merged_remote_branches_into_origin/main:':
        mode='merged'
        mode='merged'
    elif mode=='merged' and line.strip():
    elif mode=='merged' and line.strip():
        merged.append(line.strip())
        merged.append(line.strip())
d['merged_remote_branches_into_main']=merged
d['merged_remote_branches_into_main']=merged
print(json.dumps(d))
print(json.dumps(d))
PY
PY
)"
)"
  stale_count="$(wc -l < "$GC_REPORTS/branches_stale.txt" | tr -d ' ')"
  stale_count="$(wc -l < "$GC_REPORTS/branches_stale.txt" | tr -d ' ')"
  merged_count="$(python3 - <<'PY'
  merged_count="$(python3 - <<'PY'
import json
import json
d=json.loads(''''"$branches_summary"''''')
d=json.loads(''''"$branches_summary"''''')
print(len(d.get('merged_remote_branches_into_main',[])))
print(len(d.get('merged_remote_branches_into_main',[])))
PY
PY
)"
)"


  # Task durations
  # Task durations
  local durations_json slowest3
  local durations_json slowest3
  durations_json="$(python3 - <<'PY'
  durations_json="$(python3 - <<'PY'
import json
import json
rows=[]
rows=[]
try:
try:
    for line in open("$GC_REPORTS/_task_durations.txt'","r",encoding="utf-8",errors="replace"):
    for line in open("$GC_REPORTS/_task_durations.txt'","r",encoding="utf-8",errors="replace"):
        name, sec = line.strip().split('|',1)
        name, sec = line.strip().split('|',1)
        rows.append({'task':name,'seconds':int(sec)})
        rows.append({'task':name,'seconds':int(sec)})
except FileNotFoundError:
except FileNotFoundError:
    pass
    pass
rows_sorted=sorted(rows, key=lambda x: x['seconds'], reverse=True)
rows_sorted=sorted(rows, key=lambda x: x['seconds'], reverse=True)
print(json.dumps({'by_task':rows, 'slowest_3':rows_sorted[:3]}))
print(json.dumps({'by_task':rows, 'slowest_3':rows_sorted[:3]}))
PY
PY
)"
)"
  slowest3="$(python3 - <<'PY'
  slowest3="$(python3 - <<'PY'
import json
import json
d=json.loads(''''"$durations_json"''''')
d=json.loads(''''"$durations_json"''''')
print(json.dumps(d.get('slowest_3',[])))
print(json.dumps(d.get('slowest_3',[])))
PY
PY
)"
)"


  # Compute Junk Score (simple, stable; normalized components)
  # Compute Junk Score (simple, stable; normalized components)
  # Normalization: bytes and counts are log-scaled to keep stable across repos.
  # Normalization: bytes and counts are log-scaled to keep stable across repos.
  local junk_json
  local junk_json
  junk_json="$(python3 - <<'PY'
  junk_json="$(python3 - <<'PY'
import json, math
import json, math
cruft=json.loads(''''"$cruft_kv"''''')
cruft=json.loads(''''"$cruft_kv"''''')
cruft_bytes=int(cruft.get('cruft_bytes_total','0') or 0)
cruft_bytes=int(cruft.get('cruft_bytes_total','0') or 0)
weird_count=int('''"$weird_count"''')
weird_count=int('''"$weird_count"''')
large=json.loads(''''"$large_summary"''''')
large=json.loads(''''"$large_summary"''''')
large_bytes=int(large.get('bytes_total',0))
large_bytes=int(large.get('bytes_total',0))
stale=int('''"$stale_count"''')
stale=int('''"$stale_count"''')


W_CRUFT=float('''"$W_CRUFT_BYTES"''')
W_CRUFT=float('''"$W_CRUFT_BYTES"''')
W_WEIRD=float('''"$W_WEIRD_PATHS"''')
W_WEIRD=float('''"$W_WEIRD_PATHS"''')
W_LARGE=float('''"$W_LARGE_BYTES"''')
W_LARGE=float('''"$W_LARGE_BYTES"''')
W_STALE=float('''"$W_STALE_BRANCHES"''')
W_STALE=float('''"$W_STALE_BRANCHES"''')


def n_log(x):  # 0..~1-ish
def n_log(x):  # 0..~1-ish
    return 0.0 if x<=0 else min(1.0, math.log10(x+1)/10.0)
    return 0.0 if x<=0 else min(1.0, math.log10(x+1)/10.0)


score = (
score = (
    W_CRUFT*n_log(cruft_bytes) +
    W_CRUFT*n_log(cruft_bytes) +
    W_WEIRD*n_log(weird_count) +
    W_WEIRD*n_log(weird_count) +
    W_LARGE*n_log(large_bytes) +
    W_LARGE*n_log(large_bytes) +
    W_STALE*n_log(stale)
    W_STALE*n_log(stale)
) * 100.0
) * 100.0


out={
out={
  'score': round(score,2),
  'score': round(score,2),
  'weights': {
  'weights': {
    'cruft_bytes': W_CRUFT,
    'cruft_bytes': W_CRUFT,
    'weird_paths': W_WEIRD,
    'weird_paths': W_WEIRD,
    'large_bytes': W_LARGE,
    'large_bytes': W_LARGE,
    'stale_branches': W_STALE
    'stale_branches': W_STALE
  },
  },
  'components': {
  'components': {
    'cruft_bytes': cruft_bytes,
    'cruft_bytes': cruft_bytes,
    'weird_paths': weird_count,
    'weird_paths': weird_count,
    'large_bytes': large_bytes,
    'large_bytes': large_bytes,
    'stale_branches': stale
    'stale_branches': stale
  },
  },
  'normalization': 'log10(x+1)/10 capped at 1.0'
  'normalization': 'log10(x+1)/10 capped at 1.0'
}
}
print(json.dumps(out))
print(json.dumps(out))
PY
PY
)"
)"


  # Deltas vs previous run (if any)
  # Deltas vs previous run (if any)
  local deltas_json baseline_note
  local deltas_json baseline_note
  if [[ -n "$prev_metrics" ]]; then
  if [[ -n "$prev_metrics" ]]; then
    baseline_note="baseline=previous_run"
    baseline_note="baseline=previous_run"
    deltas_json="$(python3 - <<PY
    deltas_json="$(python3 - <<PY
import json
import json
cur = {
cur = {
  "junk": json.loads('''$junk_json'''),
  "junk": json.loads('''$junk_json'''),
  "cruft_bytes": int(json.loads('''$cruft_kv''').get("cruft_bytes_total","0") or 0),
  "cruft_bytes": int(json.loads('''$cruft_kv''').get("cruft_bytes_total","0") or 0),
  "cruft_count": int(json.loads('''$cruft_kv''').get("cruft_file_count_total","0") or 0),
  "cruft_count": int(json.loads('''$cruft_kv''').get("cruft_file_count_total","0") or 0),
  "weird_count": int($weird_count),
  "weird_count": int($weird_count),
  "large": json.loads('''$large_summary'''),
  "large": json.loads('''$large_summary'''),
  "stale_branches": int($stale_count),
  "stale_branches": int($stale_count),
  "merged_branches": int($merged_count),
  "merged_branches": int($merged_count),
}
}
prev = json.load(open("$prev_metrics","r",encoding="utf-8"))
prev = json.load(open("$prev_metrics","r",encoding="utf-8"))
p = prev.get("summary",{})
p = prev.get("summary",{})
def get_int(x, default=0):
def get_int(x, default=0):
    try: return int(x)
    try: return int(x)
    except: return default
    except: return default
prev_cruft_bytes=get_int(p.get("cruft",{}).get("bytes_total",0))
prev_cruft_bytes=get_int(p.get("cruft",{}).get("bytes_total",0))
prev_cruft_count=get_int(p.get("cruft",{}).get("file_count_total",0))
prev_cruft_count=get_int(p.get("cruft",{}).get("file_count_total",0))
prev_weird=get_int(p.get("weird_paths",{}).get("count_total",0))
prev_weird=get_int(p.get("weird_paths",{}).get("count_total",0))
prev_large_bytes=get_int(p.get("large_files",{}).get("bytes_total",0))
prev_large_bytes=get_int(p.get("large_files",{}).get("bytes_total",0))
prev_large_count=get_int(p.get("large_files",{}).get("count_total",0))
prev_large_count=get_int(p.get("large_files",{}).get("count_total",0))
prev_stale=get_int(p.get("branches",{}).get("stale_count",0))
prev_stale=get_int(p.get("branches",{}).get("stale_count",0))
prev_merged=get_int(p.get("branches",{}).get("merged_remote_count",0))
prev_merged=get_int(p.get("branches",{}).get("merged_remote_count",0))
prev_junk=float(p.get("junk_score",{}).get("score",0.0) or 0.0)
prev_junk=float(p.get("junk_score",{}).get("score",0.0) or 0.0)


delta={
delta={
  "junk_score": round(cur["junk"]["score"]-prev_junk,2),
  "junk_score": round(cur["junk"]["score"]-prev_junk,2),
  "cruft_bytes": cur["cruft_bytes"]-prev_cruft_bytes,
  "cruft_bytes": cur["cruft_bytes"]-prev_cruft_bytes,
  "cruft_count": cur["cruft_count"]-prev_cruft_count,
  "cruft_count": cur["cruft_count"]-prev_cruft_count,
  "weird_paths": cur["weird_count"]-prev_weird,
  "weird_paths": cur["weird_count"]-prev_weird,
  "large_bytes": cur["large"]["bytes_total"]-prev_large_bytes,
  "large_bytes": cur["large"]["bytes_total"]-prev_large_bytes,
  "large_count": cur["large"]["count"]-prev_large_count,
  "large_count": cur["large"]["count"]-prev_large_count,
  "stale_branches": cur["stale_branches"]-prev_stale,
  "stale_branches": cur["stale_branches"]-prev_stale,
  "merged_remote_branches": cur["merged_branches"]-prev_merged,
  "merged_remote_branches": cur["merged_branches"]-prev_merged,
  "prev_metrics_path": "$prev_metrics"
  "prev_metrics_path": "$prev_metrics"
}
}
print(json.dumps(delta))
print(json.dumps(delta))
PY
PY
)"
)"
  else
  else
    baseline_note="baseline=none"
    baseline_note="baseline=none"
    deltas_json="$(python3 - <<'PY'
    deltas_json="$(python3 - <<'PY'
import json
import json
print(json.dumps({"note":"no_prior_baseline"}))
print(json.dumps({"note":"no_prior_baseline"}))
PY
PY
)"
)"
  fi
  fi


  # Build final metrics.json (schema v1.0)
  # Build final metrics.json (schema v1.0)
  python3 - <<PY > "$GC_METRICS"
  python3 - <<PY > "$GC_METRICS"
import json
import json
g=json.loads('''$gkv_json''')
g=json.loads('''$gkv_json''')
cr=json.loads('''$cruft_kv''')
cr=json.loads('''$cruft_kv''')
branches=json.loads('''$branches_summary''')
branches=json.loads('''$branches_summary''')
large=json.loads('''$large_summary''')
large=json.loads('''$large_summary''')
junk=json.loads('''$junk_json''')
junk=json.loads('''$junk_json''')
dur=json.loads('''$durations_json''')
dur=json.loads('''$durations_json''')


out={
out={
  "schema_version":"1.0",
  "schema_version":"1.0",
  "run_id":"$GC_RUN_ID",
  "run_id":"$GC_RUN_ID",
  "timestamp":g.get("timestamp"),
  "timestamp":g.get("timestamp"),
  "repo_root":g.get("repo_root"),
  "repo_root":g.get("repo_root"),
  "git_sha":g.get("git_sha"),
  "git_sha":g.get("git_sha"),
  "git_branch":g.get("git_branch"),
  "git_branch":g.get("git_branch"),


  "config":{
  "config":{
    "large_file_mb": int("$LARGE_FILE_MB"),
    "large_file_mb": int("$LARGE_FILE_MB"),
    "stale_branch_days": int("$STALE_BRANCH_DAYS"),
    "stale_branch_days": int("$STALE_BRANCH_DAYS"),
    "exclude_dirs": "$GC_EXCLUDE_DIRS",
    "exclude_dirs": "$GC_EXCLUDE_DIRS",
    "timeout_per_task_seconds": int("$GC_TIMEOUT_PER_TASK_SECONDS"),
    "timeout_per_task_seconds": int("$GC_TIMEOUT_PER_TASK_SECONDS"),
    "apply_mode": int("$GC_APPLY"),
    "apply_mode": int("$GC_APPLY"),
    "overnight": {"nice":"$NICE_CMD","ionice":"$IONICE_CMD"}
    "overnight": {"nice":"$NICE_CMD","ionice":"$IONICE_CMD"}
  },
  },


  "timing":{
  "timing":{
    "task_seconds": dur.get("by_task",[]),
    "task_seconds": dur.get("by_task",[]),
    "slowest_3_tasks": dur.get("slowest_3",[])
    "slowest_3_tasks": dur.get("slowest_3",[])
  },
  },


  "summary":{
  "summary":{
    "junk_score": junk,
    "junk_score": junk,


    "repo":{
    "repo":{
      "total_files": int(g.get("repo_total_files","0") or 0),
      "total_files": int(g.get("repo_total_files","0") or 0),
      "total_bytes": int(g.get("repo_total_bytes","0") or 0)
      "total_bytes": int(g.get("repo_total_bytes","0") or 0)
    },
    },


    "cruft":{
    "cruft":{
      "file_count_total": int(cr.get("cruft_file_count_total","0") or 0),
      "file_count_total": int(cr.get("cruft_file_count_total","0") or 0),
      "bytes_total": int(cr.get("cruft_bytes_total","0") or 0),
      "bytes_total": int(cr.get("cruft_bytes_total","0") or 0),
      "by_pattern": json.loads(cr.get("cruft_by_pattern","[]")),
      "by_pattern": json.loads(cr.get("cruft_by_pattern","[]")),
      "top_dirs_by_bytes": json.loads(cr.get("cruft_top_dirs_by_bytes","[]"))
      "top_dirs_by_bytes": json.loads(cr.get("cruft_top_dirs_by_bytes","[]"))
    },
    },


    "weird_paths":{
    "weird_paths":{
      "count_total": int("$weird_count"),
      "count_total": int("$weird_count"),
      "by_category": json.loads('''$weird_by_cat''')
      "by_category": json.loads('''$weird_by_cat''')
    },
    },


    "large_files":{
    "large_files":{
      "count_total": int(large.get("count",0)),
      "count_total": int(large.get("count",0)),
      "bytes_total": int(large.get("bytes_total",0)),
      "bytes_total": int(large.get("bytes_total",0)),
      "top_50": large.get("top_50",[])
      "top_50": large.get("top_50",[])
    },
    },


    "branches":{
    "branches":{
      "local_total": int(branches.get("local_branches_total",0)),
      "local_total": int(branches.get("local_branches_total",0)),
      "remote_total": int(branches.get("remote_branches_total",0)),
      "remote_total": int(branches.get("remote_branches_total",0)),
      "merged_remote_count": len(branches.get("merged_remote_branches_into_main",[])),
      "merged_remote_count": len(branches.get("merged_remote_branches_into_main",[])),
      "stale_count": int("$stale_count")
      "stale_count": int("$stale_count")
    },
    },


    "unused_scripts":{
    "unused_scripts":{
      "candidates_count": sum(1 for _ in open("$GC_REPORTS/unused_scripts.txt","r",encoding="utf-8",errors="replace")) if __import__("os").path.exists("$GC_REPORTS/unused_scripts.txt") else 0
      "candidates_count": sum(1 for _ in open("$GC_REPORTS/unused_scripts.txt","r",encoding="utf-8",errors="replace")) if __import__("os").path.exists("$GC_REPORTS/unused_scripts.txt") else 0
    },
    },


    "deltas": json.loads('''$deltas_json''')
    "deltas": json.loads('''$deltas_json''')
  }
  }
}
}
print(json.dumps(out, indent=2, sort_keys=True))
print(json.dumps(out, indent=2, sort_keys=True))
PY
PY


  # Generate README (Morning Brief first, then details)
  # Generate README (Morning Brief first, then details)
  python3 - <<PY > "$GC_README"
  python3 - <<PY > "$GC_README"
import json, datetime
import json, datetime
m=json.load(open("$GC_METRICS","r",encoding="utf-8"))
m=json.load(open("$GC_METRICS","r",encoding="utf-8"))
s=m["summary"]
s=m["summary"]
d=s.get("deltas",{})
d=s.get("deltas",{})
def fmt_bytes(n):
def fmt_bytes(n):
    n=int(n)
    n=int(n)
    for unit in ["B","KB","MB","GB","TB"]:
    for unit in ["B","KB","MB","GB","TB"]:
        if n<1024: return f"{n}{unit}"
        if n<1024: return f"{n}{unit}"
        n//=1024
        n//=1024
    return f"{n}PB"
    return f"{n}PB"
def fmt_delta(x, kind="int"):
def fmt_delta(x, kind="int"):
    if isinstance(x,str): return x
    if isinstance(x,str): return x
    try:
    try:
        v=float(x)
        v=float(x)
    except:
    except:
        return "n/a"
        return "n/a"
    sign="+" if v>0 else ""
    sign="+" if v>0 else ""
    if kind=="bytes":
    if kind=="bytes":
        return sign + fmt_bytes(int(v))
        return sign + fmt_bytes(int(v))
    if kind=="float":
    if kind=="float":
        return f"{sign}{v:.2f}"
        return f"{sign}{v:.2f}"
    return f"{sign}{int(v)}"
    return f"{sign}{int(v)}"


junk=s["junk_score"]["score"]
junk=s["junk_score"]["score"]
print(f"# GC Run — {m['timestamp']}")
print(f"# GC Run — {m['timestamp']}")
print("")
print("")
print("## Morning Brief")
print("## Morning Brief")
print("")
print("")
print(f"- **Junk Score:** `{junk}` ({fmt_delta(d.get('junk_score',0),'float')})")
print(f"- **Junk Score:** `{junk}` ({fmt_delta(d.get('junk_score',0),'float')})")
print(f"- **Cruft:** `{fmt_bytes(s['cruft']['bytes_total'])}` in `{s['cruft']['file_count_total']}` files ({fmt_delta(d.get('cruft_bytes',0),'bytes')}, {fmt_delta(d.get('cruft_count',0))})")
print(f"- **Cruft:** `{fmt_bytes(s['cruft']['bytes_total'])}` in `{s['cruft']['file_count_total']}` files ({fmt_delta(d.get('cruft_bytes',0),'bytes')}, {fmt_delta(d.get('cruft_count',0))})")
print(f"- **Weird paths:** `{s['weird_paths']['count_total']}` ({fmt_delta(d.get('weird_paths',0))})")
print(f"- **Weird paths:** `{s['weird_paths']['count_total']}` ({fmt_delta(d.get('weird_paths',0))})")
print(f"- **Large files:** `{s['large_files']['count_total']}` totaling `{fmt_bytes(s['large_files']['bytes_total'])}` ({fmt_delta(d.get('large_count',0))}, {fmt_delta(d.get('large_bytes',0),'bytes')})")
print(f"- **Large files:** `{s['large_files']['count_total']}` totaling `{fmt_bytes(s['large_files']['bytes_total'])}` ({fmt_delta(d.get('large_count',0))}, {fmt_delta(d.get('large_bytes',0),'bytes')})")
print(f"- **Branches:** merged-remote `{s['branches']['merged_remote_count']}` ({fmt_delta(d.get('merged_remote_branches',0))}), stale `{s['branches']['stale_count']}` ({fmt_delta(d.get('stale_branches',0))})")
print(f"- **Branches:** merged-remote `{s['branches']['merged_remote_count']}` ({fmt_delta(d.get('merged_remote_branches',0))}), stale `{s['branches']['stale_count']}` ({fmt_delta(d.get('stale_branches',0))})")
print("")
print("")
print("### Runtime")
print("### Runtime")
print("")
print("")
slow=s.get("timing",{}).get("slowest_3_tasks",[])
slow=s.get("timing",{}).get("slowest_3_tasks",[])
if slow:
if slow:
    print(f"- **Slowest 3 tasks:** " + ", ".join([f\"`{t['task']}` {t['seconds']}s\" for t in slow]))
    print(f"- **Slowest 3 tasks:** " + ", ".join([f\"`{t['task']}` {t['seconds']}s\" for t in slow]))
else:
else:
    print("- **Slowest 3 tasks:** n/a")
    print("- **Slowest 3 tasks:** n/a")
print("")
print("")
print("### Top 5: Do this next")
print("### Top 5: Do this next")
print("")
print("")
# simple recommendation ordering by impact
# simple recommendation ordering by impact
recs=[]
recs=[]
if s["weird_paths"]["count_total"]>0:
if s["weird_paths"]["count_total"]>0:
    recs.append("Review `reports/weird_paths.txt` and the proposed rename map `reports/weird_paths_rename_map.txt` (recommend-only).")
    recs.append("Review `reports/weird_paths.txt` and the proposed rename map `reports/weird_paths_rename_map.txt` (recommend-only).")
if s["cruft"]["bytes_total"]>0:
if s["cruft"]["bytes_total"]>0:
    recs.append("Clean top cruft directories (see `cruft_top_dirs_by_bytes` in `metrics.json` and `reports/cruft_paths.txt`).")
    recs.append("Clean top cruft directories (see `cruft_top_dirs_by_bytes` in `metrics.json` and `reports/cruft_paths.txt`).")
if s["large_files"]["count_total"]>0:
if s["large_files"]["count_total"]>0:
    recs.append("Inspect the top large files list in `reports/large_files.txt` and decide which are expected artifacts vs mistakes.")
    recs.append("Inspect the top large files list in `reports/large_files.txt` and decide which are expected artifacts vs mistakes.")
if s["branches"]["merged_remote_count"]>0:
if s["branches"]["merged_remote_count"]>0:
    recs.append("If safe, run `proposed_actions/delete_merged_remote_branches.sh` manually after review.")
    recs.append("If safe, run `proposed_actions/delete_merged_remote_branches.sh` manually after review.")
if s["branches"]["stale_count"]>0:
if s["branches"]["stale_count"]>0:
    recs.append("Review `reports/branches_stale.txt` and close/rebase stale local branches.")
    recs.append("Review `reports/branches_stale.txt` and close/rebase stale local branches.")
# pad to 5
# pad to 5
while len(recs)<5: recs.append("No-op / monitor: rerun nightly to establish trend baseline and catch regressions early.")
while len(recs)<5: recs.append("No-op / monitor: rerun nightly to establish trend baseline and catch regressions early.")
for i,r in enumerate(recs[:5],1):
for i,r in enumerate(recs[:5],1):
    print(f"{i}. {r}")
    print(f"{i}. {r}")
print("")
print("")
print("## Details")
print("## Details")
print("")
print("")
print(f"- Output dir: `{m['repo_root']}/var/gc/runs/{'$GC_DATE'}`")
print(f"- Output dir: `{m['repo_root']}/var/gc/runs/{'$GC_DATE'}`")
print(f"- HTML dashboard: `report.html`")
print(f"- HTML dashboard: `report.html`")
print(f"- Metrics: `metrics.json` (schema_version={m['schema_version']})")
print(f"- Metrics: `metrics.json` (schema_version={m['schema_version']})")
print("")
print("")
print("### Notes")
print("### Notes")
print("")
print("")
if isinstance(d,dict) and d.get("note")=="no_prior_baseline":
if isinstance(d,dict) and d.get("note")=="no_prior_baseline":
    print("- No prior baseline found; deltas will appear starting next run.")
    print("- No prior baseline found; deltas will appear starting next run.")
else:
else:
    print(f\"- Baseline: `{d.get('prev_metrics_path','(unknown)')}`\")
    print(f\"- Baseline: `{d.get('prev_metrics_path','(unknown)')}`\")
print("")
print("")
print("### Junk Score formula")
print("### Junk Score formula")
print("")
print("")
w=s["junk_score"]["weights"]
w=s["junk_score"]["weights"]
print(f\"- weights: cruft_bytes={w['cruft_bytes']}, weird_paths={w['weird_paths']}, large_bytes={w['large_bytes']}, stale_branches={w['stale_branches']}\")
print(f\"- weights: cruft_bytes={w['cruft_bytes']}, weird_paths={w['weird_paths']}, large_bytes={w['large_bytes']}, stale_branches={w['stale_branches']}\")
print(f\"- normalization: {s['junk_score']['normalization']}\")
print(f\"- normalization: {s['junk_score']['normalization']}\")
PY
PY


  # Generate self-contained HTML dashboard
  # Generate self-contained HTML dashboard
  python3 - <<'PY' > "$GC_HTML"
  python3 - <<'PY' > "$GC_HTML"
import json, html
import json, html
m=json.load(open("'"$GC_METRICS"'","r",encoding="utf-8"))
m=json.load(open("'"$GC_METRICS"'","r",encoding="utf-8"))
s=m["summary"]
s=m["summary"]
d=s.get("deltas",{})
d=s.get("deltas",{})
def fmt_bytes(n):
def fmt_bytes(n):
    n=int(n)
    n=int(n)
    units=["B","KB","MB","GB","TB","PB"]
    units=["B","KB","MB","GB","TB","PB"]
    i=0
    i=0
    while n>=1024 and i<len(units)-1:
    while n>=1024 and i<len(units)-1:
        n//=1024; i+=1
        n//=1024; i+=1
    return f"{n}{units[i]}"
    return f"{n}{units[i]}"
def esc(x): return html.escape(str(x))
def esc(x): return html.escape(str(x))
def delta_cell(val, kind="int"):
def delta_cell(val, kind="int"):
    if isinstance(val,str): return esc(val)
    if isinstance(val,str): return esc(val)
    try: v=float(val)
    try: v=float(val)
    except: return "n/a"
    except: return "n/a"
    sign="+" if v>0 else ""
    sign="+" if v>0 else ""
    if kind=="bytes": return sign + fmt_bytes(int(v))
    if kind=="bytes": return sign + fmt_bytes(int(v))
    if kind=="float": return f"{sign}{v:.2f}"
    if kind=="float": return f"{sign}{v:.2f}"
    return f"{sign}{int(v)}"
    return f"{sign}{int(v)}"


# tables
# tables
cruft_pats=s["cruft"]["by_pattern"]
cruft_pats=s["cruft"]["by_pattern"]
cruft_dirs=s["cruft"]["top_dirs_by_bytes"]
cruft_dirs=s["cruft"]["top_dirs_by_bytes"]
large=s["large_files"]["top_50"]
large=s["large_files"]["top_50"]
slow=m.get("timing",{})
slow=m.get("timing",{})


html_out=f"""<!doctype html>
html_out=f"""<!doctype html>
<html>
<html>
<head>
<head>
<meta charset="utf-8"/>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>GC Report — {esc(m['timestamp'])}</title>
<title>GC Report — {esc(m['timestamp'])}</title>
<style>
<style>
  :root {{
  :root {{
    --bg:#0b0f14; --panel:#111824; --text:#e6edf3; --muted:#9aa4b2;
    --bg:#0b0f14; --panel:#111824; --text:#e6edf3; --muted:#9aa4b2;
    --good:#3fb950; --warn:#d29922; --bad:#f85149; --border:#233041;
    --good:#3fb950; --warn:#d29922; --bad:#f85149; --border:#233041;
    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
    --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
  }}
  }}
  body {{ background:var(--bg); color:var(--text); font-family:var(--sans); margin:0; padding:24px; }}
  body {{ background:var(--bg); color:var(--text); font-family:var(--sans); margin:0; padding:24px; }}
  .wrap {{ max-width: 1200px; margin: 0 auto; }}
  .wrap {{ max-width: 1200px; margin: 0 auto; }}
  h1 {{ margin:0 0 8px 0; font-size: 22px; }}
  h1 {{ margin:0 0 8px 0; font-size: 22px; }}
  .sub {{ color:var(--muted); margin-bottom: 16px; }}
  .sub {{ color:var(--muted); margin-bottom: 16px; }}
  .grid {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin: 12px 0 18px; }}
  .grid {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin: 12px 0 18px; }}
  .card {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:12px; }}
  .card {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:12px; }}
  .k {{ color:var(--muted); font-size: 12px; }}
  .k {{ color:var(--muted); font-size: 12px; }}
  .v {{ font-family:var(--mono); font-size: 18px; margin-top:6px; }}
  .v {{ font-family:var(--mono); font-size: 18px; margin-top:6px; }}
  details {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:10px 12px; margin: 10px 0; }}
  details {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:10px 12px; margin: 10px 0; }}
  summary {{ cursor:pointer; font-weight: 600; }}
  summary {{ cursor:pointer; font-weight: 600; }}
  table {{ width:100%; border-collapse: collapse; margin-top:10px; }}
  table {{ width:100%; border-collapse: collapse; margin-top:10px; }}
  th, td {{ border-bottom:1px solid var(--border); padding:8px; text-align:left; }}
  th, td {{ border-bottom:1px solid var(--border); padding:8px; text-align:left; }}
  th {{ color:var(--muted); font-size: 12px; user-select:none; cursor:pointer; }}
  th {{ color:var(--muted); font-size: 12px; user-select:none; cursor:pointer; }}
  td.mono {{ font-family:var(--mono); }}
  td.mono {{ font-family:var(--mono); }}
  .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; border:1px solid var(--border); font-family:var(--mono); font-size:12px; color:var(--muted); }}
  .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; border:1px solid var(--border); font-family:var(--mono); font-size:12px; color:var(--muted); }}
  .row {{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 10px; }}
  .row {{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 10px; }}
  .muted {{ color:var(--muted); }}
  .muted {{ color:var(--muted); }}
  .ok {{ color:var(--good); }}
  .ok {{ color:var(--good); }}
  .warn {{ color:var(--warn); }}
  .warn {{ color:var(--warn); }}
  .bad {{ color:var(--bad); }}
  .bad {{ color:var(--bad); }}
  .copy {{ cursor:pointer; }}
  .copy {{ cursor:pointer; }}
</style>
</style>
</head>
</head>
<body>
<body>
<div class="wrap">
<div class="wrap">
  <h1>GC Report</h1>
  <h1>GC Report</h1>
  <div class="sub">{esc(m['timestamp'])} • {esc(m['git_branch'])} • {esc(m['git_sha'][:12])} • run_id={esc(m['run_id'])}</div>
  <div class="sub">{esc(m['timestamp'])} • {esc(m['git_branch'])} • {esc(m['git_sha'][:12])} • run_id={esc(m['run_id'])}</div>


  <div class="grid">
  <div class="grid">
    <div class="card"><div class="k">Junk Score (Δ)</div><div class="v">{esc(s['junk_score']['score'])} <span class="pill">{esc(delta_cell(d.get('junk_score',0),'float'))}</span></div></div>
    <div class="card"><div class="k">Junk Score (Δ)</div><div class="v">{esc(s['junk_score']['score'])} <span class="pill">{esc(delta_cell(d.get('junk_score',0),'float'))}</span></div></div>
    <div class="card"><div class="k">Cruft bytes (Δ)</div><div class="v">{esc(fmt_bytes(s['cruft']['bytes_total']))} <span class="pill">{esc(delta_cell(d.get('cruft_bytes',0),'bytes'))}</span></div></div>
    <div class="card"><div class="k">Cruft bytes (Δ)</div><div class="v">{esc(fmt_bytes(s['cruft']['bytes_total']))} <span class="pill">{esc(delta_cell(d.get('cruft_bytes',0),'bytes'))}</span></div></div>
    <div class="card"><div class="k">Weird paths (Δ)</div><div class="v">{esc(s['weird_paths']['count_total'])} <span class="pill">{esc(delta_cell(d.get('weird_paths',0)))}</span></div></div>
    <div class="card"><div class="k">Weird paths (Δ)</div><div class="v">{esc(s['weird_paths']['count_total'])} <span class="pill">{esc(delta_cell(d.get('weird_paths',0)))}</span></div></div>
    <div class="card"><div class="k">Large files bytes (Δ)</div><div class="v">{esc(fmt_bytes(s['large_files']['bytes_total']))} <span class="pill">{esc(delta_cell(d.get('large_bytes',0),'bytes'))}</span></div></div>
    <div class="card"><div class="k">Large files bytes (Δ)</div><div class="v">{esc(fmt_bytes(s['large_files']['bytes_total']))} <span class="pill">{esc(delta_cell(d.get('large_bytes',0),'bytes'))}</span></div></div>
  </div>
  </div>


  <div class="row muted">
  <div class="row muted">
    <span class="pill">repo_files={esc(s['repo']['total_files'])}</span>
    <span class="pill">repo_files={esc(s['repo']['total_files'])}</span>
    <span class="pill">repo_bytes={esc(fmt_bytes(s['repo']['total_bytes']))}</span>
    <span class="pill">repo_bytes={esc(fmt_bytes(s['repo']['total_bytes']))}</span>
    <span class="pill">stale_branches={esc(s['branches']['stale_count'])} (Δ {esc(delta_cell(d.get('stale_branches',0)))})</span>
    <span class="pill">stale_branches={esc(s['branches']['stale_count'])} (Δ {esc(delta_cell(d.get('stale_branches',0)))})</span>
    <span class="pill">merged_remote={esc(s['branches']['merged_remote_count'])} (Δ {esc(delta_cell(d.get('merged_remote_branches',0)))})</span>
    <span class="pill">merged_remote={esc(s['branches']['merged_remote_count'])} (Δ {esc(delta_cell(d.get('merged_remote_branches',0)))})</span>
    <span class="pill">schema={esc(m['schema_version'])}</span>
    <span class="pill">schema={esc(m['schema_version'])}</span>
  </div>
  </div>


  <details open>
  <details open>
    <summary>Slowest tasks</summary>
    <summary>Slowest tasks</summary>
    <table class="sortable">
    <table class="sortable">
      <thead><tr><th data-type="text">task</th><th data-type="num">seconds</th></tr></thead>
      <thead><tr><th data-type="text">task</th><th data-type="num">seconds</th></tr></thead>
      <tbody>
      <tbody>
      {''.join([f"<tr><td class='mono'>{esc(t['task'])}</td><td class='mono'>{esc(t['seconds'])}</td></tr>" for t in m.get('timing',{}).get('slowest_3_tasks',[])])}
      {''.join([f"<tr><td class='mono'>{esc(t['task'])}</td><td class='mono'>{esc(t['seconds'])}</td></tr>" for t in m.get('timing',{}).get('slowest_3_tasks',[])])}
      </tbody>
      </tbody>
    </table>
    </table>
  </details>
  </details>


  <details>
  <details>
    <summary>Cruft by pattern</summary>
    <summary>Cruft by pattern</summary>
    <table class="sortable">
    <table class="sortable">
      <thead><tr><th data-type="text">pattern</th><th data-type="num">count</th><th data-type="num">bytes</th></tr></thead>
      <thead><tr><th data-type="text">pattern</th><th data-type="num">count</th><th data-type="num">bytes</th></tr></thead>
      <tbody>
      <tbody>
      {''.join([f"<tr><td class='mono'>{esc(r['pattern'])}</td><td class='mono'>{esc(r['count'])}</td><td class='mono'>{esc(r['bytes'])}</td></tr>" for r in cruft_pats])}
      {''.join([f"<tr><td class='mono'>{esc(r['pattern'])}</td><td class='mono'>{esc(r['count'])}</td><td class='mono'>{esc(r['bytes'])}</td></tr>" for r in cruft_pats])}
      </tbody>
      </tbody>
    </table>
    </table>
  </details>
  </details>


  <details>
  <details>
    <summary>Top cruft directories (by bytes)</summary>
    <summary>Top cruft directories (by bytes)</summary>
    <table class="sortable">
    <table class="sortable">
      <thead><tr><th data-type="text">dir</th><th data-type="num">count</th><th data-type="num">bytes</th></tr></thead>
      <thead><tr><th data-type="text">dir</th><th data-type="num">count</th><th data-type="num">bytes</th></tr></thead>
      <tbody>
      <tbody>
      {''.join([f"<tr><td class='mono copy' title='click to copy'>{esc(r['dir'])}</td><td class='mono'>{esc(r['count'])}</td><td class='mono'>{esc(r['bytes'])}</td></tr>" for r in cruft_dirs])}
      {''.join([f"<tr><td class='mono copy' title='click to copy'>{esc(r['dir'])}</td><td class='mono'>{esc(r['count'])}</td><td class='mono'>{esc(r['bytes'])}</td></tr>" for r in cruft_dirs])}
      </tbody>
      </tbody>
    </table>
    </table>
  </details>
  </details>


  <details>
  <details>
    <summary>Large files (top 50)</summary>
    <summary>Large files (top 50)</summary>
    <table class="sortable">
    <table class="sortable">
      <thead><tr><th data-type="num">bytes</th><th data-type="text">path</th></tr></thead>
      <thead><tr><th data-type="num">bytes</th><th data-type="text">path</th></tr></thead>
      <tbody>
      <tbody>
      {''.join([f"<tr><td class='mono'>{esc(r['bytes'])}</td><td class='mono copy' title='click to copy'>{esc(r['path'])}</td></tr>" for r in large])}
      {''.join([f"<tr><td class='mono'>{esc(r['bytes'])}</td><td class='mono copy' title='click to copy'>{esc(r['path'])}</td></tr>" for r in large])}
      </tbody>
      </tbody>
    </table>
    </table>
  </details>
  </details>


  <details>
  <details>
    <summary>How Junk Score works</summary>
    <summary>How Junk Score works</summary>
    <div class="muted">weights: {esc(s['junk_score']['weights'])}</div>
    <div class="muted">weights: {esc(s['junk_score']['weights'])}</div>
    <div class="muted">normalization: {esc(s['junk_score']['normalization'])}</div>
    <div class="muted">normalization: {esc(s['junk_score']['normalization'])}</div>
  </details>
  </details>


  <details>
  <details>
    <summary>Artifacts</summary>
    <summary>Artifacts</summary>
    <ul class="muted">
    <ul class="muted">
      <li><span class="mono">README.md</span> — morning brief</li>
      <li><span class="mono">README.md</span> — morning brief</li>
      <li><span class="mono">metrics.json</span> — automation/trends</li>
      <li><span class="mono">metrics.json</span> — automation/trends</li>
      <li><span class="mono">reports/*.txt</span> — raw evidence</li>
      <li><span class="mono">reports/*.txt</span> — raw evidence</li>
      <li><span class="mono">proposed_actions/*.sh</span> — reviewable scripts (manual)</li>
      <li><span class="mono">proposed_actions/*.sh</span> — reviewable scripts (manual)</li>
    </ul>
    </ul>
  </details>
  </details>


</div>
</div>
<script>
<script>
// sortable tables (no dependencies)
// sortable tables (no dependencies)
document.querySelectorAll('table.sortable th').forEach(th => {{
document.querySelectorAll('table.sortable th').forEach(th => {{
  th.addEventListener('click', () => {{
  th.addEventListener('click', () => {{
    const table = th.closest('table');
    const table = th.closest('table');
    const tbody = table.querySelector('tbody');
    const tbody = table.querySelector('tbody');
    const idx = Array.from(th.parentNode.children).indexOf(th);
    const idx = Array.from(th.parentNode.children).indexOf(th);
    const type = th.getAttribute('data-type') || 'text';
    const type = th.getAttribute('data-type') || 'text';
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const asc = !(th.dataset.asc === '1');
    const asc = !(th.dataset.asc === '1');
    th.dataset.asc = asc ? '1' : '0';
    th.dataset.asc = asc ? '1' : '0';


    rows.sort((a,b) => {{
    rows.sort((a,b) => {{
      const av = a.children[idx].innerText.trim();
      const av = a.children[idx].innerText.trim();
      const bv = b.children[idx].innerText.trim();
      const bv = b.children[idx].innerText.trim();
      if (type === 'num') {{
      if (type === 'num') {{
        const an = Number(av.replace(/[^0-9.-]/g,'')) || 0;
        const an = Number(av.replace(/[^0-9.-]/g,'')) || 0;
        const bn = Number(bv.replace(/[^0-9.-]/g,'')) || 0;
        const bn = Number(bv.replace(/[^0-9.-]/g,'')) || 0;
        return asc ? (an-bn) : (bn-an);
        return asc ? (an-bn) : (bn-an);
      }}
      }}
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    }});
    }});


    rows.forEach(r => tbody.appendChild(r));
    rows.forEach(r => tbody.appendChild(r));
  }});
  }});
}});
}});


// click-to-copy for monospace path cells
// click-to-copy for monospace path cells
document.querySelectorAll('.copy').forEach(td => {{
document.querySelectorAll('.copy').forEach(td => {{
  td.addEventListener('click', async () => {{
  td.addEventListener('click', async () => {{
    try {{
    try {{
      await navigator.clipboard.writeText(td.innerText.trim());
      await navigator.clipboard.writeText(td.innerText.trim());
      td.classList.add('ok');
      td.classList.add('ok');
      setTimeout(() => td.classList.remove('ok'), 350);
      setTimeout(() => td.classList.remove('ok'), 350);
    }} catch (_) {{}}
    }} catch (_) {{}}
  }});
  }});
}});
}});
</script>
</script>
</body>
</body>
</html>
</html>
"""
"""
print(html_out)
print(html_out)
PY
PY
}
}


# ----------------------
# ----------------------
# Main
# Main
# ----------------------
# ----------------------
main() {
main() {
  require_repo_root
  require_repo_root
  export STALE_BRANCH_DAYS LARGE_FILE_MB GC_EXCLUDE_DIRS
  export STALE_BRANCH_DAYS LARGE_FILE_MB GC_EXCLUDE_DIRS


  # Start README early (append logs later if needed)
  # Start README early (append logs later if needed)
  : > "$GC_README"
  : > "$GC_README"


  log "# GC Run — $GC_DATE"
  log "# GC Run — $GC_DATE"
  log ""
  log ""
  log "- run_id: \`$GC_RUN_ID\`"
  log "- run_id: \`$GC_RUN_ID\`"
  log "- repo_root: \`$GC_ROOT\`"
  log "- repo_root: \`$GC_ROOT\`"
  log "- apply_mode: \`$GC_APPLY\` (0=recommend-only)"
  log "- apply_mode: \`$GC_APPLY\` (0=recommend-only)"
  log "- exclude_dirs: \`$GC_EXCLUDE_DIRS\`"
  log "- exclude_dirs: \`$GC_EXCLUDE_DIRS\`"
  log "- large_file_mb: \`$LARGE_FILE_MB\`"
  log "- large_file_mb: \`$LARGE_FILE_MB\`"
  log "- stale_branch_days: \`$STALE_BRANCH_DAYS\`"
  log "- stale_branch_days: \`$STALE_BRANCH_DAYS\`"
  log ""
  log ""


  require_clean_main_if_apply
  require_clean_main_if_apply


  # Cheap → expensive (overnight-friendly)
  # Cheap → expensive (overnight-friendly)
  task_global_metrics
  task_global_metrics
  task_cruft
  task_cruft
  task_weird_paths
  task_weird_paths
  task_branches
  task_branches
  task_large_files
  task_large_files
  task_unused_scripts
  task_unused_scripts


  generate_metrics_and_reports
  generate_metrics_and_reports


  # Ensure final README is the generated one (the generator overwrote it)
  # Ensure final README is the generated one (the generator overwrote it)
  # Append task status notes (timeouts/errors) at end
  # Append task status notes (timeouts/errors) at end
  if [[ -f "$GC_REPORTS/_task_status.txt" ]]; then
  if [[ -f "$GC_REPORTS/_task_status.txt" ]]; then
    {
    {
      echo ""
      echo ""
      echo "## Task status"
      echo "## Task status"
      echo ""
      echo ""
      echo '```'
      echo '```'
      cat "$GC_REPORTS/_task_status.txt"
      cat "$GC_REPORTS/_task_status.txt"
      echo '```'
      echo '```'
    } >> "$GC_README"
    } >> "$GC_README"
  fi
  fi


  # Provide a tiny pointer file for humans
  # Provide a tiny pointer file for humans
  echo "HTML: $GC_HTML" > "$GC_REPORTS/_pointers.txt"
  echo "HTML: $GC_HTML" > "$GC_REPORTS/_pointers.txt"
  echo "README: $GC_README" >> "$GC_REPORTS/_pointers.txt"
  echo "README: $GC_README" >> "$GC_REPORTS/_pointers.txt"
  echo "METRICS: $GC_METRICS" >> "$GC_REPORTS/_pointers.txt"
  echo "METRICS: $GC_METRICS" >> "$GC_REPORTS/_pointers.txt"
}
}


main "$@"
main "$@"
