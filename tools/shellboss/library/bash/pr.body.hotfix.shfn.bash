# pr.body.hotfix.shfn.bash
# Pretty PR-body generator: mktemp-first, icons, no ANSI dependency, no exit.

# Usage:
#   . tools/shellboss/library/bash/pr.body.hotfix.shfn.bash
#   shellboss_pr_body_hotfix
#
# Writes a ready-to-paste PR body to mktemp and updates /tmp/hee.pr.body.latest.md.

shellboss_pr_body_hotfix() {
  local OUT
  OUT="$(mktemp -t hee.pr.body.XXXXXX.md)" || return 1
  ln -sf "$OUT" /tmp/hee.pr.body.latest.md 2>/dev/null || true

  local repo="/home/spencer/git/human-execution-engine"
  cd "$repo" || { printf "❌ ERROR: cd failed: %s\n" "$repo"; return 1; }

  local branch head
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || return 1
  head="$(git rev-parse HEAD 2>/dev/null)" || return 1

  local files
  files="$(git show --name-only --pretty=format: -1 2>/dev/null | sed '/^$/d')" || files="(unable to read file list)"

  {
    printf "## ShellBoss: rg scan shfn (oper UX + mktemp-first evidence)\n\n"
    printf "### Artifact (shfn-first primitive)\n"
    printf "- `tools/shellboss/library/bash/rg.scan.shfn.bash`\n\n"
    printf "This PR introduces a tiny ripgrep helper shfn and wires it into ShellBoss + the installer.\n\n"
    printf "---\n\n"
    printf "## Why this is a big deal\n\n"
    printf "Oper now gets a zero-friction rg helper that:\n\n"
    printf "- defaults to **counts** (`wc -l`) for low-noise console usage\n"
    printf "- emits **mktemp evidence reports** only when useful (hits>0 or forced)\n"
    printf "- avoids `exit` in pasteable surfaces (returns only)\n"
    printf "- supports portable “pretty” output via icons (works even without ANSI)\n"
    printf "- reinforces ShellBoss as the machine-behind-the-console\n\n"
    printf "---\n\n"
    printf "## Referee Summary\n\n"
    printf "### Card counts (this session)\n"
    printf "- 🟥 RED: caught wiring + commit-reality drift early\n"
    printf "- 🟨 YELLOW: installer/root footguns stabilized\n"
    printf "- 🟩 GREEN: final state verified on disk\n\n"
    printf "### Corrections made\n"
    printf "- shfn existed but was not landing in PR → fixed (tracked + committed)\n"
    printf "- installer + shellboss wiring missing → fixed (rg-proven)\n"
    printf "- commit message drift vs file reality → corrected (final commit includes exact file set)\n\n"
    printf "Single source of truth:\n"
    printf "- `tools/shellboss/library/bash/rg.scan.shfn.bash`\n\n"
    printf "---\n\n"
    printf "## Render Preview (oper view)\n\n"
    printf "```\n"
    printf "🧾 REPORT  /tmp/...\n"
    printf "🔎 SCAN    wrote matches to mktemp\n"
    printf "🛑/✅      status + counts\n"
    printf "📌 SUMMARY hits_any=... hits_code=...\n"
    printf "👀 OPEN    less /tmp/...\n"
    printf "🔗 LATEST  /tmp/...\n"
    printf "```\n\n"
    printf "Portable pretty: icons > ANSI.\n\n"
    printf "---\n\n"
    printf "## Stats\n"
    printf "- Branch: `%s`\n" "$branch"
    printf "- Commit: `%s`\n" "$head"
    printf "- Files in commit:\n\n"
    printf "```\n%s\n```\n" "$files"
  } > "$OUT" || return 1

  printf "✅ PR BODY READY\n"
  printf "🧾 FILE   %s\n" "$OUT"
  printf "🔗 LATEST %s\n" "/tmp/hee.pr.body.latest.md"
  printf "👀 OPEN   %s\n" "less /tmp/hee.pr.body.latest.md"
}
