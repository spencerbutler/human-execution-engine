#!/usr/bin/env bash
set -euo pipefail

rb=""
b=""


# ============================================================
# GC Report Pack — repo hygiene monitoring (recommend-only)
# Outputs per run:
#   var/gc/runs/YYYY-MM-DD/{README.md,report.html,metrics.json,reports/*,proposed_actions/*}
#   var/gc/latest -> current run
#
# Safety:
#   - Default recommend-only
#   - Apply mode requires: GC_APPLY=1, clean tree, on main
#   - Branch deletion NEVER executed automatically; only proposed script
# ============================================================

# ----------------------
# Config (env override)
# ----------------------
GC_ROOT="${GC_ROOT:-$(pwd)}"
GC_OUT_BASE="${GC_OUT_BASE:-$GC_ROOT/var/gc}"
GC_DATE="${GC_DATE:-$(date +%F)}"
GC_RUN_ID="${GC_RUN_ID:-$(date +%Y%m%d)-$(date +%H%M%S)-$$}"
GC_APPLY="${GC_APPLY:-0}"                         # must remain 0 for cron/overnight
GC_EXCLUDE_DIRS="${GC_EXCLUDE_DIRS:-}"            # colon-separated relative dirs to exclude (e.g. "generated:dist:var")
GC_TIMEOUT_PER_TASK_SECONDS="${GC_TIMEOUT_PER_TASK_SECONDS:-0}"  # 0 disables soft timeout

LARGE_FILE_MB="${LARGE_FILE_MB:-50}"
STALE_BRANCH_DAYS="${STALE_BRANCH_DAYS:-30}"

# Junk Score weights (stable & logged)
W_CRUFT_BYTES="${W_CRUFT_BYTES:-0.35}"
W_WEIRD_PATHS="${W_WEIRD_PATHS:-0.20}"
W_LARGE_BYTES="${W_LARGE_BYTES:-0.25}"
W_STALE_BRANCHES="${W_STALE_BRANCHES:-0.20}"

# Overnight niceness
NICE_CMD="${NICE_CMD:-nice -n 10}"
IONICE_CMD="${IONICE_CMD:-ionice -c2 -n7}"

# Derived paths
GC_OUT="$GC_OUT_BASE/runs/$GC_DATE"
GC_LATEST="$GC_OUT_BASE/latest"
GC_CACHE="$GC_OUT_BASE/cache"
GC_REPORTS="$GC_OUT/reports"
GC_PROPOSE="$GC_OUT/proposed_actions"
GC_README="$GC_OUT/README.md"
GC_HTML="$GC_OUT/report.html"
GC_METRICS="$GC_OUT/metrics.json"

mkdir -p "$GC_REPORTS" "$GC_PROPOSE" "$GC_CACHE"
ln -sfn "$GC_OUT" "$GC_LATEST"

# ----------------------
# Utilities
# ----------------------
ts() { date -Is; }
log() { printf "[%s] %s\n" "$(ts)" "$*"; }
die() { echo "ERROR: $*" >&2; exit 2; }

have() { command -v "$1" >/dev/null 2>&1; }

# Soft timeout wrapper (best-effort)
run_task() {
  local name="$1"; shift
  local start_ns end_ns dur_s
  start_ns="$(date +%s%N 2>/dev/null || python3 - <<'PY'
import time; print(int(time.time()*1e9))
PY
)"

  if [[ "$GC_TIMEOUT_PER_TASK_SECONDS" -gt 0 ]] && have timeout; then
    # timeout returns 124 on timeout; do not fail the whole run
    if ! $NICE_CMD $IONICE_CMD timeout "$GC_TIMEOUT_PER_TASK_SECONDS" bash -c "$1"; then
      local rc=$?
      if [[ "$rc" == "124" ]]; then
        echo "$name|timeout|$GC_TIMEOUT_PER_TASK_SECONDS" >> "$GC_REPORTS/_task_status.txt"
      else
        echo "$name|error|$rc" >> "$GC_REPORTS/_task_status.txt"
      fi
    else
      echo "$name|ok|0" >> "$GC_REPORTS/_task_status.txt"
    fi
  else
    if ! $NICE_CMD $IONICE_CMD bash -c "$1"; then
      echo "$name|error|$?" >> "$GC_REPORTS/_task_status.txt"
    else
      echo "$name|ok|0" >> "$GC_REPORTS/_task_status.txt"
    fi
  fi

  end_ns="$(date +%s%N 2>/dev/null || python3 - <<'PY'
import time; print(int(time.time()*1e9))
PY
)"
  dur_s=$(( (end_ns - start_ns) / 1000000000 ))
  echo "$name|$dur_s" >> "$GC_REPORTS/_task_durations.txt"
}

require_repo_root() {
  have git || die "git is required"
  git -C "$GC_ROOT" rev-parse --show-toplevel >/dev/null 2>&1 || die "Not a git repo: $GC_ROOT"
  local top; top="$(git -C "$GC_ROOT" rev-parse --show-toplevel)"
  [[ "$top" == "$GC_ROOT" ]] || die "GC_ROOT must be repo root. top=$top GC_ROOT=$GC_ROOT"
}

require_clean_main_if_apply() {
  if [[ "$GC_APPLY" != "1" ]]; then return 0; fi
  local branch
  branch="$(git -C "$GC_ROOT" rev-parse --abbrev-ref HEAD)"
  [[ "$branch" == "main" ]] || die "Apply mode requires branch=main (got: $branch)"
  git -C "$GC_ROOT" diff --quiet || die "Apply mode requires clean working tree"
  git -C "$GC_ROOT" diff --cached --quiet || die "Apply mode requires clean index"
}

# Exclude find patterns
build_find_excludes() {
  local ex=()
  ex+=( -path "./.git" -prune )
  if [[ -n "$GC_EXCLUDE_DIRS" ]]; then
    IFS=':' read -r -a parts <<<"$GC_EXCLUDE_DIRS"
    for d in "${parts[@]}"; do
      [[ -z "$d" ]] && continue
      # prune ./dir
      ex+=( -o -path "./$d" -prune )
    done
  fi
  printf "%s " "${ex[@]}"
}

# Prior run detection
find_previous_run_dir() {
  if [[ ! -d "$GC_OUT_BASE/runs" ]]; then
    echo ""
    return 0
  fi
  # pick most recent run directory != current date
  ls -1 "$GC_OUT_BASE/runs" 2>/dev/null \
    | sort -r \
    | awk -v cur="$GC_DATE" '$0!=cur {print; exit}' \
    | awk -v base="$GC_OUT_BASE/runs" '{print base "/" $0}'
}

# ----------------------
# Task: global repo metrics + cache filelist
# ----------------------
task_global_metrics() {
  local report="$GC_REPORTS/global.txt"
  local excludes; excludes="$(build_find_excludes)"

  run_task "global_metrics" "
    set -euo pipefail
    cd '$GC_ROOT'
    {
      echo 'repo_root=$GC_ROOT'
      echo 'timestamp=$(date -Is)'
      echo 'git_sha='\"\$(git rev-parse HEAD)\"
      echo 'git_branch='\"\$(git rev-parse --abbrev-ref HEAD)\"
    } > '$report'

    # File inventory (excluding .git and excluded dirs). Cache compressed if possible.
    mkdir -p '$GC_CACHE'
    if command -v zstd >/dev/null 2>&1; then
      find . $excludes -o -type f -print0 | zstd -q -T0 -19 -o '$GC_CACHE/filelist.zst' || true
      echo 'filelist_cache=var/gc/cache/filelist.zst' >> '$report'
    elif command -v gzip >/dev/null 2>&1; then
      find . $excludes -o -type f -print0 | gzip -c > '$GC_CACHE/filelist.gz' || true
      echo 'filelist_cache=var/gc/cache/filelist.gz' >> '$report'
    else
      find . $excludes -o -type f -print0 > '$GC_CACHE/filelist.bin' || true
      echo 'filelist_cache=var/gc/cache/filelist.bin' >> '$report'
    fi

    # Approx counts/sizes (exclude .git and excludes)
    python3 - <<'PY' >> '$report'
import os
root = os.getcwd()
exclude = {'.git'}
extra = os.environ.get('GC_EXCLUDE_DIRS','')
if extra:
    exclude |= set([p.strip().lstrip('./') for p in extra.split(':') if p.strip()])
total_files = 0
total_bytes = 0
for dirpath, dirnames, filenames in os.walk(root):
    rel = os.path.relpath(dirpath, root)
    # prune excludes
    parts = [] if rel == '.' else rel.split(os.sep)
    if parts and parts[0] in exclude:
        dirnames[:] = []
        continue
    if rel != '.' and rel.split(os.sep)[0] in exclude:
        dirnames[:] = []
        continue
    # also prune .git anywhere
    dirnames[:] = [d for d in dirnames if d != '.git' and d not in exclude]
    for fn in filenames:
        if fn == '.git': continue
        p = os.path.join(dirpath, fn)
        try:
            st = os.stat(p)
        except OSError:
            continue
        total_files += 1
        total_bytes += st.st_size
print(f'repo_total_files={total_files}')
print(f'repo_total_bytes={total_bytes}')
PY
  "
}

# ----------------------
# Task: cruft detection
# ----------------------
task_cruft() {
  local report="$GC_REPORTS/cruft_paths.txt"
  local report2="$GC_REPORTS/cruft_summary.txt"
  local excludes; excludes="$(build_find_excludes)"

  run_task "cruft_scan" "
    set -euo pipefail
    cd '$GC_ROOT'
    find . $excludes -o -type f \\( \
      -name '*.bak' -o -name '*~' -o -name '*.swp' -o -name '*.tmp' -o -name '*.orig' -o -name '*.rej' -o \
      -name '.DS_Store' -o -name 'Thumbs.db' -o -name '*.log' \
    \\) -print > '$report' || true

    # Fix: allow variable expansion in heredoc to resolve GC_REPORTS path
    python3 - <<PY > '$report2'
import os, json, re
root = os.getcwd()
paths = []
with open('$report','r',encoding='utf-8',errors='replace') as f:
    for line in f:
        p=line.strip()
        if not p: continue
        paths.append(p)
def pat(p):
    base=os.path.basename(p)
    for k in ['.bak','~','.swp','.tmp','.orig','.rej','.DS_Store','Thumbs.db','.log']:
        if base==k or base.endswith(k): return k
    return 'other'
by_pat={}
by_dir={}
total_bytes=0
for p in paths:
    ap=os.path.join(root,p)
    try:
        sz=os.stat(ap).st_size
    except OSError:
        sz=0
    total_bytes += sz
    k=pat(p)
    by_pat.setdefault(k, {'count':0,'bytes':0})
    by_pat[k]['count']+=1
    by_pat[k]['bytes']+=sz
    d=os.path.dirname(p) or '.'
    by_dir.setdefault(d, {'count':0,'bytes':0})
    by_dir[d]['count']+=1
    by_dir[d]['bytes']+=sz

top_dirs=sorted(by_dir.items(), key=lambda kv: kv[1]['bytes'], reverse=True)[:20]
top_pats=sorted(by_pat.items(), key=lambda kv: kv[1]['bytes'], reverse=True)
print(f'cruft_file_count_total={len(paths)}')
print(f'cruft_bytes_total={total_bytes}')
print('cruft_by_pattern=' + json.dumps([{ 'pattern':k, **v } for k,v in top_pats]))
print('cruft_top_dirs_by_bytes=' + json.dumps([{ 'dir':k, **v } for k,v in top_dirs]))
PY
  "
}

# ----------------------
# Task: weird paths
# ----------------------
task_weird_paths() {
  local report="$GC_REPORTS/weird_paths.txt"
  local mapping="$GC_REPORTS/weird_paths_rename_map.txt"

  run_task "weird_paths" "
    set -euo pipefail
    cd '$GC_ROOT'
    { git ls-files -z; git ls-files --others --exclude-standard -z; } \
      | python3 - <<'PY' > '$report'
import sys, unicodedata
data = sys.stdin.buffer.read().split(b'\x00')
def classify(s: str):
    cats=set()
    if s.endswith(' '): cats.add('trailing_space')
    if any(ord(c) < 32 or ord(c) == 127 for c in s): cats.add('control_chars')
    if '\t' in s or '\r' in s or '\n' in s: cats.add('tabs_newlines')
    # suspicious non-printing unicode
    for c in s:
        if unicodedata.category(c) in ('Cf',):  # format chars
            cats.add('format_chars')
    return cats

out=[]
for p in data:
    if not p: continue
    s=p.decode('utf-8', errors='replace')
    cats=classify(s)
    if cats:
        out.append((s, sorted(cats)))
for s,cats in out:
    sys.stdout.write(s + '\t' + ','.join(cats) + '\n')
PY

    # Proposed rename mapping (recommend-only)
    python3 - <<'PY' > '$mapping'
import re, sys
def normalize(name: str) -> str:
    # replace control chars and whitespace oddities with underscores
    name = ''.join('_' if (ord(c)<32 or ord(c)==127) else c for c in name)
    name = name.replace('\t','_').replace('\r','_').replace('\n','_')
    name = re.sub(r'\s+$','',name)           # drop trailing spaces
    name = re.sub(r'__+','_',name)
    return name

lines=open('$report','r',encoding='utf-8',errors='replace').read().splitlines()
for line in lines:
    if not line.strip(): continue
    path=line.split('\t',1)[0]
    n=normalize(path)
    if n!=path:
        print(f'{path} -> {n}')
PY
  "
}

# ----------------------
# Task: branch hygiene (recommend-only + proposed script)
# ----------------------
task_branches() {
  local report="$GC_REPORTS/branches.txt"
  local propose="$GC_PROPOSE/delete_merged_remote_branches.sh"
  local stale_report="$GC_REPORTS/branches_stale.txt"

  run_task "branch_hygiene" "
    set -eo pipefail
    cd '$GC_ROOT'
    git fetch --prune >/dev/null 2>&1 || true

    {
      echo 'local_branches_total='\"\$(git branch --format='%(refname:short)' | wc -l | tr -d ' ')\"
      echo 'remote_branches_total='\"\$(git branch -r --format='%(refname:short)' | wc -l | tr -d ' ')\"
    } > '$report'

    echo 'merged_remote_branches_into_origin/main:' >> '$report'
    git branch -r --merged origin/main | sed 's/^  //' | grep -vE 'origin/(main|master|HEAD)\$' >> '$report' || true

    # stale branches: last commit older than STALE_BRANCH_DAYS
    python3 - <<'PY' > '$stale_report'
import subprocess, datetime, os
days=int(os.environ.get('STALE_BRANCH_DAYS','30'))
cut=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
cmd=['git','for-each-ref','--format=%(refname:short)\t%(committerdate:iso8601)','refs/heads']
out=subprocess.check_output(cmd, text=True, errors='replace')
rows=[]
for line in out.splitlines():
    b, d = line.split('\t',1)
    try:
        dt=datetime.datetime.fromisoformat(d.replace('Z','+00:00'))
    except Exception:
        continue
    if dt < cut:
        rows.append((dt, b))
rows.sort()
for dt,b in rows:
    print(f'{b}\t{dt.isoformat()}')
PY

    # Proposed deletion script (NEVER auto-run)
    : > "$propose"
    printf '%s\n' \
      '#!/usr/bin/env bash' \
      'set -euo pipefail' \
      'git fetch --prune' \
      '# REVIEW BEFORE RUNNING.' \
      '# Deletes ONLY merged remote branches (origin/*) excluding main/master/HEAD.' \
      'git branch -r --merged origin/main | sed '\''s/^  //'\'' | grep -vE '\''origin/(main|master|HEAD)$'\'' | while IFS= read -r rb; do' \
      '  [[ -z ${rb:-} ]] && continue' \
      '  b=${rb#origin/}' \
      '  echo Deleting remote branch: $b' \
      '  git push origin --delete $b' \
      'done' \
      > "$propose"
    chmod +x "$propose"
  "
}

# ----------------------
# Task: large files
# ----------------------
task_large_files() {
  local report="$GC_REPORTS/large_files.txt"
  local excludes; excludes="$(build_find_excludes)"

  run_task "large_files" "
    set -euo pipefail
    cd '$GC_ROOT'
    # size in bytes + path, sorted desc
    python3 - <<'PY' > '$report'
import os
root=os.getcwd()
threshold_mb=int(os.environ.get('LARGE_FILE_MB','50'))
threshold=threshold_mb*1024*1024
exclude={'.git'}
extra=os.environ.get('GC_EXCLUDE_DIRS','')
if extra:
    exclude |= set([p.strip().lstrip('./') for p in extra.split(':') if p.strip()])
hits=[]
for dirpath, dirnames, filenames in os.walk(root):
    rel=os.path.relpath(dirpath, root)
    parts=[] if rel == '.' else rel.split(os.sep)
    if parts and parts[0] in exclude:
        dirnames[:] = []
        continue
    dirnames[:] = [d for d in dirnames if d!='.git' and d not in exclude]
    for fn in filenames:
        p=os.path.join(dirpath, fn)
        try:
            st=os.stat(p)
        except OSError:
            continue
        if st.st_size >= threshold:
            rp=os.path.relpath(p, root)
            hits.append((st.st_size, rp))
hits.sort(reverse=True)
for sz, rp in hits[:200]:
    print(f'{sz}\t{rp}')
PY
  "
}

# ----------------------
# Task: unused scripts (recommend-only heuristic)
# ----------------------
task_unused_scripts() {
  local report="$GC_REPORTS/unused_scripts.txt"
  local reasons="$GC_REPORTS/unused_scripts_reasons.txt"

  run_task "unused_scripts" "
    set -euo pipefail
    cd '$GC_ROOT'
    git ls-files | grep -E '\\.(sh|py|rb|pl|js|ts)$' > '$GC_REPORTS/_scripts_all.txt' || true

    # gather reference surfaces (best-effort)
    touch '$GC_REPORTS/_refs.txt'
    if command -v rg >/dev/null 2>&1; then
      rg -n --no-heading -S \"scripts/|\\./scripts/\" .github Makefile makefile docs prompts 2>/dev/null \
        | awk -F: '{print \$0}' >> '$GC_REPORTS/_refs.txt' || true
    else
      # fallback: grep (no PCRE)
      grep -RIn \"scripts/\" .github Makefile makefile docs prompts 2>/dev/null >> '$GC_REPORTS/_refs.txt' || true
    fi

    python3 - <<'PY' > '$report'
import os, re, subprocess, datetime
root=os.getcwd()
scripts=open('$GC_REPORTS/_scripts_all.txt','r',encoding='utf-8',errors='replace').read().splitlines()
refs=open('$GC_REPORTS/_refs.txt','r',encoding='utf-8',errors='replace').read()
cands=[]
for s in scripts:
    if not s.strip(): continue
    if s in refs or ('./'+s) in refs:
        continue
    cands.append(s)
for s in cands:
    print(s)
PY

    python3 - <<'PY' > '$reasons'
import os, subprocess, datetime
root=os.getcwd()
def git_mtime(path):
    try:
        out=subprocess.check_output(['git','log','-1','--format=%ct','--',path], text=True).strip()
        return int(out) if out else 0
    except Exception:
        return 0
def loc(path):
    try:
        with open(path,'rb') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

now=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
paths=open('$report','r',encoding='utf-8',errors='replace').read().splitlines()
for p in paths:
    ts=git_mtime(p)
    age_days=(now-ts)//86400 if ts else 999999
    lines=loc(p)
    # simple confidence score: older + smaller => higher confidence it's unused
    score=0
    score += 40 if age_days > 180 else (20 if age_days > 60 else 5)
    score += 30 if lines < 80 else (15 if lines < 250 else 5)
    score += 30  # base: not referenced
    if score > 100: score = 100
    print(f'{p}\tconfidence={score}\tlast_commit_age_days={age_days}\tloc={lines}\treason=not_referenced_in_common_surfaces')
PY
  "
}

# ----------------------
# Metrics + HTML + README generation
# ----------------------
parse_kv_file() {
  # parse key=value lines into env-like export map (python returns json)
  local file="$1"
  python3 - <<PY
import json
d={}
for line in open("$file","r",encoding="utf-8",errors="replace"):
    line=line.strip()
    if not line or line.startswith("#"): continue
    if "=" in line:
        k,v=line.split("=",1)
        d[k.strip()]=v.strip()
print(json.dumps(d))
PY
}

generate_metrics_and_reports() {
  local prev_dir prev_metrics
  prev_dir="$(find_previous_run_dir)"
  prev_metrics=""
  if [[ -n "$prev_dir" ]] && [[ -f "$prev_dir/metrics.json" ]]; then
    prev_metrics="$prev_dir/metrics.json"
  fi

  # Gather global info
  local gkv_json
  gkv_json="$(parse_kv_file "$GC_REPORTS/global.txt")"
  local cruft_kv weird_count weird_by_cat large_summary branches_summary stale_count merged_count

  cruft_kv="$(python3 - <<'PY'
import json, re
txt=open("'$GC_REPORTS/cruft_summary.txt'","r",encoding="utf-8",errors="replace").read().splitlines()
d={}
for line in txt:
    if '=' in line:
        k,v=line.split('=',1)
        d[k]=v
print(json.dumps(d))
PY
)"
  weird_count="$(wc -l < "$GC_REPORTS/weird_paths.txt" | tr -d ' ')"
  weird_by_cat="$(python3 - <<'PY'
import collections
c=collections.Counter()
for line in open("'$GC_REPORTS/weird_paths.txt'","r",encoding="utf-8",errors="replace"):
    line=line.strip()
    if not line: continue
    parts=line.split('\t',1)
    cats=parts[1].split(',') if len(parts)>1 else []
    for cat in cats: c[cat]+=1
print(__import__('json').dumps(c))
PY
)"
  large_summary="$(python3 - <<'PY'
import os, json
total=0
count=0
top=[]
for line in open("'$GC_REPORTS/large_files.txt'","r",encoding="utf-8",errors="replace"):
    line=line.strip()
    if not line: continue
    sz_s, path = line.split('\t',1)
    sz=int(sz_s)
    total += sz
    count += 1
    if len(top)<50:
        top.append({'bytes':sz,'path':path})
print(json.dumps({'count':count,'bytes_total':total,'top_50':top}))
PY
)"

  branches_summary="$(python3 - <<'PY'
import re, json
report=open("'$GC_REPORTS/branches.txt'","r",encoding="utf-8",errors="replace").read().splitlines()
d={}
merged=[]
mode=None
for line in report:
    if line.startswith('local_branches_total='):
        d['local_branches_total']=int(line.split('=',1)[1])
    elif line.startswith('remote_branches_total='):
        d['remote_branches_total']=int(line.split('=',1)[1])
    elif line.strip()=='merged_remote_branches_into_origin/main:':
        mode='merged'
    elif mode=='merged' and line.strip():
        merged.append(line.strip())
d['merged_remote_branches_into_main']=merged
print(json.dumps(d))
PY
)"
  stale_count="$(wc -l < "$GC_REPORTS/branches_stale.txt" | tr -d ' ')"
  merged_count="$(python3 - <<'PY'
import json
d=json.loads(''''"$branches_summary"''''')
print(len(d.get('merged_remote_branches_into_main',[])))
PY
)"

  # Task durations
  local durations_json slowest3
  durations_json="$(python3 - <<'PY'
import json
rows=[]
try:
    for line in open("'$GC_REPORTS/_task_durations.txt'","r",encoding="utf-8",errors="replace"):
        name, sec = line.strip().split('|',1)
        rows.append({'task':name,'seconds':int(sec)})
except FileNotFoundError:
    pass
rows_sorted=sorted(rows, key=lambda x: x['seconds'], reverse=True)
print(json.dumps({'by_task':rows, 'slowest_3':rows_sorted[:3]}))
PY
)"
  slowest3="$(python3 - <<'PY'
import json
d=json.loads(''''"$durations_json"''''')
print(json.dumps(d.get('slowest_3',[])))
PY
)"

  # Compute Junk Score (simple, stable; normalized components)
  # Normalization: bytes and counts are log-scaled to keep stable across repos.
  local junk_json
  junk_json="$(python3 - <<'PY'
import json, math
cruft=json.loads(''''"$cruft_kv"''''')
cruft_bytes=int(cruft.get('cruft_bytes_total','0') or 0)
weird_count=int('''"$weird_count"''')
large=json.loads(''''"$large_summary"''''')
large_bytes=int(large.get('bytes_total',0))
stale=int('''"$stale_count"''')

W_CRUFT=float('''"$W_CRUFT_BYTES"''')
W_WEIRD=float('''"$W_WEIRD_PATHS"''')
W_LARGE=float('''"$W_LARGE_BYTES"''')
W_STALE=float('''"$W_STALE_BRANCHES"''')

def n_log(x):  # 0..~1-ish
    return 0.0 if x<=0 else min(1.0, math.log10(x+1)/10.0)

score = (
    W_CRUFT*n_log(cruft_bytes) +
    W_WEIRD*n_log(weird_count) +
    W_LARGE*n_log(large_bytes) +
    W_STALE*n_log(stale)
) * 100.0

out={
  'score': round(score,2),
  'weights': {
    'cruft_bytes': W_CRUFT,
    'weird_paths': W_WEIRD,
    'large_bytes': W_LARGE,
    'stale_branches': W_STALE
  },
  'components': {
    'cruft_bytes': cruft_bytes,
    'weird_paths': weird_count,
    'large_bytes': large_bytes,
    'stale_branches': stale
  },
  'normalization': 'log10(x+1)/10 capped at 1.0'
}
print(json.dumps(out))
PY
)"

  # Deltas vs previous run (if any)
  local deltas_json baseline_note
  if [[ -n "$prev_metrics" ]]; then
    baseline_note="baseline=previous_run"
    deltas_json="$(python3 - <<PY
import json
cur = {
  "junk": json.loads('''$junk_json'''),
  "cruft_bytes": int(json.loads('''$cruft_kv''').get("cruft_bytes_total","0") or 0),
  "cruft_count": int(json.loads('''$cruft_kv''').get("cruft_file_count_total","0") or 0),
  "weird_count": int($weird_count),
  "large": json.loads('''$large_summary'''),
  "stale_branches": int($stale_count),
  "merged_branches": int($merged_count),
}
prev = json.load(open("$prev_metrics","r",encoding="utf-8"))
p = prev.get("summary",{})
def get_int(x, default=0):
    try: return int(x)
    except: return default
prev_cruft_bytes=get_int(p.get("cruft",{}).get("bytes_total",0))
prev_cruft_count=get_int(p.get("cruft",{}).get("file_count_total",0))
prev_weird=get_int(p.get("weird_paths",{}).get("count_total",0))
prev_large_bytes=get_int(p.get("large_files",{}).get("bytes_total",0))
prev_large_count=get_int(p.get("large_files",{}).get("count_total",0))
prev_stale=get_int(p.get("branches",{}).get("stale_count",0))
prev_merged=get_int(p.get("branches",{}).get("merged_remote_count",0))
prev_junk=float(p.get("junk_score",{}).get("score",0.0) or 0.0)

delta={
  "junk_score": round(cur["junk"]["score"]-prev_junk,2),
  "cruft_bytes": cur["cruft_bytes"]-prev_cruft_bytes,
  "cruft_count": cur["cruft_count"]-prev_cruft_count,
  "weird_paths": cur["weird_count"]-prev_weird,
  "large_bytes": cur["large"]["bytes_total"]-prev_large_bytes,
  "large_count": cur["large"]["count"]-prev_large_count,
  "stale_branches": cur["stale_branches"]-prev_stale,
  "merged_remote_branches": cur["merged_branches"]-prev_merged,
  "prev_metrics_path": "$prev_metrics"
}
print(json.dumps(delta))
PY
)"
  else
    baseline_note="baseline=none"
    deltas_json="$(python3 - <<'PY'
import json
print(json.dumps({"note":"no_prior_baseline"}))
PY
)"
  fi

  # Build final metrics.json (schema v1.0)
  python3 - <<PY > "$GC_METRICS"
import json
g=json.loads('''$gkv_json''')
cr=json.loads('''$cruft_kv''')
branches=json.loads('''$branches_summary''')
large=json.loads('''$large_summary''')
junk=json.loads('''$junk_json''')
dur=json.loads('''$durations_json''')

out={
  "schema_version":"1.0",
  "run_id":"$GC_RUN_ID",
  "timestamp":g.get("timestamp"),
  "repo_root":g.get("repo_root"),
  "git_sha":g.get("git_sha"),
  "git_branch":g.get("git_branch"),

  "config":{
    "large_file_mb": int("$LARGE_FILE_MB"),
    "stale_branch_days": int("$STALE_BRANCH_DAYS"),
    "exclude_dirs": "$GC_EXCLUDE_DIRS",
    "timeout_per_task_seconds": int("$GC_TIMEOUT_PER_TASK_SECONDS"),
    "apply_mode": int("$GC_APPLY"),
    "overnight": {"nice":"$NICE_CMD","ionice":"$IONICE_CMD"}
  },

  "timing":{
    "task_seconds": dur.get("by_task",[]),
    "slowest_3_tasks": dur.get("slowest_3",[])
  },

  "summary":{
    "junk_score": junk,

    "repo":{
      "total_files": int(g.get("repo_total_files","0") or 0),
      "total_bytes": int(g.get("repo_total_bytes","0") or 0)
    },

    "cruft":{
      "file_count_total": int(cr.get("cruft_file_count_total","0") or 0),
      "bytes_total": int(cr.get("cruft_bytes_total","0") or 0),
      "by_pattern": json.loads(cr.get("cruft_by_pattern","[]")),
      "top_dirs_by_bytes": json.loads(cr.get("cruft_top_dirs_by_bytes","[]"))
    },

    "weird_paths":{
      "count_total": int("$weird_count"),
      "by_category": json.loads('''$weird_by_cat''')
    },

    "large_files":{
      "count_total": int(large.get("count",0)),
      "bytes_total": int(large.get("bytes_total",0)),
      "top_50": large.get("top_50",[])
    },

    "branches":{
      "local_total": int(branches.get("local_branches_total",0)),
      "remote_total": int(branches.get("remote_branches_total",0)),
      "merged_remote_count": len(branches.get("merged_remote_branches_into_main",[])),
      "stale_count": int("$stale_count")
    },

    "unused_scripts":{
      "candidates_count": sum(1 for _ in open("$GC_REPORTS/unused_scripts.txt","r",encoding="utf-8",errors="replace")) if __import__("os").path.exists("$GC_REPORTS/unused_scripts.txt") else 0
    },

    "deltas": json.loads('''$deltas_json''')
  }
}
print(json.dumps(out, indent=2, sort_keys=True))
PY

  # Generate README (Morning Brief first, then details)
  python3 - <<PY > "$GC_README"
import json, datetime
m=json.load(open("$GC_METRICS","r",encoding="utf-8"))
s=m["summary"]
d=s.get("deltas",{})
def fmt_bytes(n):
    n=int(n)
    for unit in ["B","KB","MB","GB","TB"]:
        if n<1024: return f"{n}{unit}"
        n//=1024
    return f"{n}PB"
def fmt_delta(x, kind="int"):
    if isinstance(x,str): return x
    try:
        v=float(x)
    except:
        return "n/a"
    sign="+" if v>0 else ""
    if kind=="bytes":
        return sign + fmt_bytes(int(v))
    if kind=="float":
        return f"{sign}{v:.2f}"
    return f"{sign}{int(v)}"

junk=s["junk_score"]["score"]
print(f"# GC Run — {m['timestamp']}")
print("")
print("## Morning Brief")
print("")
print(f"- **Junk Score:** `{junk}` ({fmt_delta(d.get('junk_score',0),'float')})")
print(f"- **Cruft:** `{fmt_bytes(s['cruft']['bytes_total'])}` in `{s['cruft']['file_count_total']}` files ({fmt_delta(d.get('cruft_bytes',0),'bytes')}, {fmt_delta(d.get('cruft_count',0))})")
print(f"- **Weird paths:** `{s['weird_paths']['count_total']}` ({fmt_delta(d.get('weird_paths',0))})")
print(f"- **Large files:** `{s['large_files']['count_total']}` totaling `{fmt_bytes(s['large_files']['bytes_total'])}` ({fmt_delta(d.get('large_count',0))}, {fmt_delta(d.get('large_bytes',0),'bytes')})")
print(f"- **Branches:** merged-remote `{s['branches']['merged_remote_count']}` ({fmt_delta(d.get('merged_remote_branches',0))}), stale `{s['branches']['stale_count']}` ({fmt_delta(d.get('stale_branches',0))})")
print("")
print("### Runtime")
print("")
slow=s.get("timing",{}).get("slowest_3_tasks",[])
if slow:
    print(f"- **Slowest 3 tasks:** " + ", ".join([f\"`{t['task']}` {t['seconds']}s\" for t in slow]))
else:
    print("- **Slowest 3 tasks:** n/a")
print("")
print("### Top 5: Do this next")
print("")
# simple recommendation ordering by impact
recs=[]
if s["weird_paths"]["count_total"]>0:
    recs.append("Review `reports/weird_paths.txt` and the proposed rename map `reports/weird_paths_rename_map.txt` (recommend-only).")
if s["cruft"]["bytes_total"]>0:
    recs.append("Clean top cruft directories (see `cruft_top_dirs_by_bytes` in `metrics.json` and `reports/cruft_paths.txt`).")
if s["large_files"]["count_total"]>0:
    recs.append("Inspect the top large files list in `reports/large_files.txt` and decide which are expected artifacts vs mistakes.")
if s["branches"]["merged_remote_count"]>0:
    recs.append("If safe, run `proposed_actions/delete_merged_remote_branches.sh` manually after review.")
if s["branches"]["stale_count"]>0:
    recs.append("Review `reports/branches_stale.txt` and close/rebase stale local branches.")
# pad to 5
while len(recs)<5: recs.append("No-op / monitor: rerun nightly to establish trend baseline and catch regressions early.")
for i,r in enumerate(recs[:5],1):
    print(f"{i}. {r}")
print("")
print("## Details")
print("")
print(f"- Output dir: `{m['repo_root']}/var/gc/runs/{'$GC_DATE'}`")
print(f"- HTML dashboard: `report.html`")
print(f"- Metrics: `metrics.json` (schema_version={m['schema_version']})")
print("")
print("### Notes")
print("")
if isinstance(d,dict) and d.get("note")=="no_prior_baseline":
    print("- No prior baseline found; deltas will appear starting next run.")
else:
    print(f\"- Baseline: `{d.get('prev_metrics_path','(unknown)')}`\")
print("")
print("### Junk Score formula")
print("")
w=s["junk_score"]["weights"]
print(f\"- weights: cruft_bytes={w['cruft_bytes']}, weird_paths={w['weird_paths']}, large_bytes={w['large_bytes']}, stale_branches={w['stale_branches']}\")
print(f\"- normalization: {s['junk_score']['normalization']}\")
PY

  # Generate self-contained HTML dashboard
  python3 - <<'PY' > "$GC_HTML"
import json, html
m=json.load(open("'"$GC_METRICS"'","r",encoding="utf-8"))
s=m["summary"]
d=s.get("deltas",{})
def fmt_bytes(n):
    n=int(n)
    units=["B","KB","MB","GB","TB","PB"]
    i=0
    while n>=1024 and i<len(units)-1:
        n//=1024; i+=1
    return f"{n}{units[i]}"
def esc(x): return html.escape(str(x))
def delta_cell(val, kind="int"):
    if isinstance(val,str): return esc(val)
    try: v=float(val)
    except: return "n/a"
    sign="+" if v>0 else ""
    if kind=="bytes": return sign + fmt_bytes(int(v))
    if kind=="float": return f"{sign}{v:.2f}"
    return f"{sign}{int(v)}"

# tables
cruft_pats=s["cruft"]["by_pattern"]
cruft_dirs=s["cruft"]["top_dirs_by_bytes"]
large=s["large_files"]["top_50"]
slow=m.get("timing",{})

html_out=f"""<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>GC Report — {esc(m['timestamp'])}</title>
<style>
  :root {{
    --bg:#0b0f14; --panel:#111824; --text:#e6edf3; --muted:#9aa4b2;
    --good:#3fb950; --warn:#d29922; --bad:#f85149; --border:#233041;
    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
  }}
  body {{ background:var(--bg); color:var(--text); font-family:var(--sans); margin:0; padding:24px; }}
  .wrap {{ max-width: 1200px; margin: 0 auto; }}
  h1 {{ margin:0 0 8px 0; font-size: 22px; }}
  .sub {{ color:var(--muted); margin-bottom: 16px; }}
  .grid {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin: 12px 0 18px; }}
  .card {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:12px; }}
  .k {{ color:var(--muted); font-size: 12px; }}
  .v {{ font-family:var(--mono); font-size: 18px; margin-top:6px; }}
  details {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:10px 12px; margin: 10px 0; }}
  summary {{ cursor:pointer; font-weight: 600; }}
  table {{ width:100%; border-collapse: collapse; margin-top:10px; }}
  th, td {{ border-bottom:1px solid var(--border); padding:8px; text-align:left; }}
  th {{ color:var(--muted); font-size: 12px; user-select:none; cursor:pointer; }}
  td.mono {{ font-family:var(--mono); }}
  .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; border:1px solid var(--border); font-family:var(--mono); font-size:12px; color:var(--muted); }}
  .row {{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 10px; }}
  .muted {{ color:var(--muted); }}
  .ok {{ color:var(--good); }}
  .warn {{ color:var(--warn); }}
  .bad {{ color:var(--bad); }}
  .copy {{ cursor:pointer; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>GC Report</h1>
  <div class="sub">{esc(m['timestamp'])} • {esc(m['git_branch'])} • {esc(m['git_sha'][:12])} • run_id={esc(m['run_id'])}</div>

  <div class="grid">
    <div class="card"><div class="k">Junk Score (Δ)</div><div class="v">{esc(s['junk_score']['score'])} <span class="pill">{esc(delta_cell(d.get('junk_score',0),'float'))}</span></div></div>
    <div class="card"><div class="k">Cruft bytes (Δ)</div><div class="v">{esc(fmt_bytes(s['cruft']['bytes_total']))} <span class="pill">{esc(delta_cell(d.get('cruft_bytes',0),'bytes'))}</span></div></div>
    <div class="card"><div class="k">Weird paths (Δ)</div><div class="v">{esc(s['weird_paths']['count_total'])} <span class="pill">{esc(delta_cell(d.get('weird_paths',0)))}</span></div></div>
    <div class="card"><div class="k">Large files bytes (Δ)</div><div class="v">{esc(fmt_bytes(s['large_files']['bytes_total']))} <span class="pill">{esc(delta_cell(d.get('large_bytes',0),'bytes'))}</span></div></div>
  </div>

  <div class="row muted">
    <span class="pill">repo_files={esc(s['repo']['total_files'])}</span>
    <span class="pill">repo_bytes={esc(fmt_bytes(s['repo']['total_bytes']))}</span>
    <span class="pill">stale_branches={esc(s['branches']['stale_count'])} (Δ {esc(delta_cell(d.get('stale_branches',0)))})</span>
    <span class="pill">merged_remote={esc(s['branches']['merged_remote_count'])} (Δ {esc(delta_cell(d.get('merged_remote_branches',0)))})</span>
    <span class="pill">schema={esc(m['schema_version'])}</span>
  </div>

  <details open>
    <summary>Slowest tasks</summary>
    <table class="sortable">
      <thead><tr><th data-type="text">task</th><th data-type="num">seconds</th></tr></thead>
      <tbody>
      {''.join([f"<tr><td class='mono'>{esc(t['task'])}</td><td class='mono'>{esc(t['seconds'])}</td></tr>" for t in m.get('timing',{}).get('slowest_3_tasks',[])])}
      </tbody>
    </table>
  </details>

  <details>
    <summary>Cruft by pattern</summary>
    <table class="sortable">
      <thead><tr><th data-type="text">pattern</th><th data-type="num">count</th><th data-type="num">bytes</th></tr></thead>
      <tbody>
      {''.join([f"<tr><td class='mono'>{esc(r['pattern'])}</td><td class='mono'>{esc(r['count'])}</td><td class='mono'>{esc(r['bytes'])}</td></tr>" for r in cruft_pats])}
      </tbody>
    </table>
  </details>

  <details>
    <summary>Top cruft directories (by bytes)</summary>
    <table class="sortable">
      <thead><tr><th data-type="text">dir</th><th data-type="num">count</th><th data-type="num">bytes</th></tr></thead>
      <tbody>
      {''.join([f"<tr><td class='mono copy' title='click to copy'>{esc(r['dir'])}</td><td class='mono'>{esc(r['count'])}</td><td class='mono'>{esc(r['bytes'])}</td></tr>" for r in cruft_dirs])}
      </tbody>
    </table>
  </details>

  <details>
    <summary>Large files (top 50)</summary>
    <table class="sortable">
      <thead><tr><th data-type="num">bytes</th><th data-type="text">path</th></tr></thead>
      <tbody>
      {''.join([f"<tr><td class='mono'>{esc(r['bytes'])}</td><td class='mono copy' title='click to copy'>{esc(r['path'])}</td></tr>" for r in large])}
      </tbody>
    </table>
  </details>

  <details>
    <summary>How Junk Score works</summary>
    <div class="muted">weights: {esc(s['junk_score']['weights'])}</div>
    <div class="muted">normalization: {esc(s['junk_score']['normalization'])}</div>
  </details>

  <details>
    <summary>Artifacts</summary>
    <ul class="muted">
      <li><span class="mono">README.md</span> — morning brief</li>
      <li><span class="mono">metrics.json</span> — automation/trends</li>
      <li><span class="mono">reports/*.txt</span> — raw evidence</li>
      <li><span class="mono">proposed_actions/*.sh</span> — reviewable scripts (manual)</li>
    </ul>
  </details>

</div>
<script>
// sortable tables (no dependencies)
document.querySelectorAll('table.sortable th').forEach(th => {{
  th.addEventListener('click', () => {{
    const table = th.closest('table');
    const tbody = table.querySelector('tbody');
    const idx = Array.from(th.parentNode.children).indexOf(th);
    const type = th.getAttribute('data-type') || 'text';
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const asc = !(th.dataset.asc === '1');
    th.dataset.asc = asc ? '1' : '0';

    rows.sort((a,b) => {{
      const av = a.children[idx].innerText.trim();
      const bv = b.children[idx].innerText.trim();
      if (type === 'num') {{
        const an = Number(av.replace(/[^0-9.-]/g,'')) || 0;
        const bn = Number(bv.replace(/[^0-9.-]/g,'')) || 0;
        return asc ? (an-bn) : (bn-an);
      }}
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    }});

    rows.forEach(r => tbody.appendChild(r));
  }});
}});

// click-to-copy for monospace path cells
document.querySelectorAll('.copy').forEach(td => {{
  td.addEventListener('click', async () => {{
    try {{
      await navigator.clipboard.writeText(td.innerText.trim());
      td.classList.add('ok');
      setTimeout(() => td.classList.remove('ok'), 350);
    }} catch (_) {{}}
  }});
}});
</script>
</body>
</html>
"""
print(html_out)
PY
}

# ----------------------
# Main
# ----------------------
main() {
  require_repo_root
  export STALE_BRANCH_DAYS LARGE_FILE_MB GC_EXCLUDE_DIRS

  # Start README early (append logs later if needed)
  : > "$GC_README"

  log "# GC Run — $GC_DATE"
  log ""
  log "- run_id: \`$GC_RUN_ID\`"
  log "- repo_root: \`$GC_ROOT\`"
  log "- apply_mode: \`$GC_APPLY\` (0=recommend-only)"
  log "- exclude_dirs: \`$GC_EXCLUDE_DIRS\`"
  log "- large_file_mb: \`$LARGE_FILE_MB\`"
  log "- stale_branch_days: \`$STALE_BRANCH_DAYS\`"
  log ""

  require_clean_main_if_apply

  # Cheap → expensive (overnight-friendly)
  task_global_metrics
  task_cruft
  task_weird_paths
  task_branches
  task_large_files
  task_unused_scripts

  generate_metrics_and_reports

  # Ensure final README is the generated one (the generator overwrote it)
  # Append task status notes (timeouts/errors) at end
  if [[ -f "$GC_REPORTS/_task_status.txt" ]]; then
    {
      echo ""
      echo "## Task status"
      echo ""
      echo '```'
      cat "$GC_REPORTS/_task_status.txt"
      echo '```'
    } >> "$GC_README"
  fi

  # Provide a tiny pointer file for humans
  echo "HTML: $GC_HTML" > "$GC_REPORTS/_pointers.txt"
  echo "README: $GC_README" >> "$GC_REPORTS/_pointers.txt"
  echo "METRICS: $GC_METRICS" >> "$GC_REPORTS/_pointers.txt"
}

main "$@"
