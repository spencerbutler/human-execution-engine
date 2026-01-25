# Git/GitHub Workflow — Strong Admission Control (HEE)

## Objective
This repo enforces **strong Git/GH governance** so agents cannot improvise unsafe sequences. Any **mutating** git/gh operation must be executed through a single guarded entrypoint script:

- `scripts/hee_git_ops.sh`

CI enforces presence + references via:

- `scripts/hee_ci_gitops_enforce.sh`

## Non-Negotiables
1. **No raw git/gh mutations by agents.**
   - Agents may *read* (status/log/diff) directly, but may not mutate via raw `git`/`gh` commands.
2. **All mutating operations route through `scripts/hee_git_ops.sh`.**
3. **Branch gating**: mutation on `main` is refused.
4. **Liveness gating**: if a mutation is requested while the agent remains in PLAN/tool-mode, the agent must emit **BLOCKER** and stop.
   - Mechanism: `scripts/hee_git_ops.sh` requires explicit `--act` and `HEE_TOOL_MODE=ACT` for mutations.
5. **CI must fail** if runbook/script/prompt references are missing.

## Definition: Mutating Operations
Any command that changes repo state, commit graph, tags, branches, remotes, or GitHub artifacts. Examples:
- `git commit`, `git merge`, `git rebase`, `git push`, `git tag`, `git branch` (create/delete)
- `gh pr create`, `gh pr merge`, `gh repo create`, etc.

## Allowed Patterns

### Read-only (allowed without the wrapper)
These are permitted directly:
- `git status`
- `git diff`
- `git log`
- `git show`
- `gh pr view` (read-only)

### Mutations (MUST use wrapper)
All mutations must use:
- `scripts/hee_git_ops.sh <operation> --act --reason "…" [args...]`

Additionally, the environment must indicate liveness:
- `HEE_TOOL_MODE=ACT`

If either is missing, the wrapper will refuse with a **BLOCKER**.

## Standard Workflow (Branch + PR)
1. Ensure you are not on `main`:
   - `git branch --show-current`
2. Make file changes.
3. Stage files (mutation):
   - `HEE_TOOL_MODE=ACT scripts/hee_git_ops.sh add --act --reason "stage files" <paths...>`
4. Commit (mutation):
   - `HEE_TOOL_MODE=ACT scripts/hee_git_ops.sh commit --act --reason "commit changes" -m "…"`
5. Push (mutation):
   - `HEE_TOOL_MODE=ACT scripts/hee_git_ops.sh push --act --reason "push branch"`
6. Open PR (mutation):
   - `HEE_TOOL_MODE=ACT scripts/hee_git_ops.sh pr-create --act --reason "open PR" --base main --title "…" --body "…"`

## Failure Mode Expectations
- If an agent is asked to mutate while in PLAN/tool-mode, it must output:
  - `BLOCKER: Mutation requested but HEE_TOOL_MODE!=ACT or --act missing. Refusing.`
  - Then stop.
- CI fails if governance artifacts are missing or prompts do not reference them.

## Notes on Tags
Tags represent **mainline milestones**. It is acceptable for a tag to point at a merge commit on `main`.
