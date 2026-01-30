# Logs and Artifacts

Canonical on-disk layout and capture requirements for HEE runtime operations.

## Directory Layout

```
.human-execution-engine/
├── logs/
│   ├── run-{RUN_ID}/
│   │   ├── step-{STEP_ID}/
│   │   │   ├── command.log
│   │   │   ├── output.log
│   │   │   └── error.log
│   │   ├── run-summary.md
│   │   └── run-report.md
│   └── archive/
├── artifacts/
│   ├── run-{RUN_ID}/
│   │   ├── git-status.txt
│   │   ├── git-diff.patch
│   │   └── file-list.txt
│   └── archive/
└── summaries/
    └── latest.md
```

## Naming Conventions

### Run Folder
`run-{YYYYMMDD}-{HHMMSS}-{RUN_ID}`

Examples:
- `run-20260130-002845-step-1643567325`
- `run-20260130-002901-phase-ops-hee-oper-runtime-docs`

### Step Folder
`step-{STEP_ID}`

Examples:
- `step-001`
- `step-create-readme`
- `step-$(date +%s)`

## Required Outputs

### Run Summary
Template for `run-summary.md`:

```markdown
# Run Summary: {RUN_ID}

**Status:** FIN | FAIL
**Branch:** {BRANCH_NAME}
**Started:** {START_TIME}
**Completed:** {END_TIME}
**Duration:** {DURATION}

## Summary
- [Bullet 1]
- [Bullet 2]
- [Bullet 3]

## Commands Executed
1. [Command 1]
2. [Command 2]
3. [Command 3]

## Files Changed
- [File 1]
- [File 2]
- [File 3]
```

### Run Report
Template for `run-report.md`:

```markdown
# Run Report: {RUN_ID}

**Status:** FIN | FAIL
**Branch:** {BRANCH_NAME}
**Changed files:** {FILE_COUNT}
**Summary:** {BULLETED_SUMMARY}
**Commands executed:** {COMMAND_COUNT}
**Notes for operator:** {OPERATOR_NOTES}
**Follow-ups:** {FOLLOW_UP_ITEMS}
```

## What to Capture

### Command Transcript Highlights
- All git commands and their output
- File creation/modification commands
- Error messages and stack traces
- Validation command results

### Git Status/Diff Snapshots
- `git status --porcelain` before and after
- `git diff --stat` for changed files
- `git diff` for actual content changes
- Branch information

### Error Outputs
- Full error messages
- Stack traces
- Exit codes
- Context around failures

### Final File List Changed
- Complete list of modified files
- New files created
- Files deleted
- Directory structure changes

## Retention Policy

### Keep Last N Runs
- Maintain last 10 successful runs
- Keep all failed runs indefinitely
- Archive runs older than 30 days

### Pruning Strategy
```bash
# Archive old runs
find .hee/logs/run-* -mtime +30 -exec mv {} .hee/logs/archive/ \;

# Keep failed runs
find .hee/logs/archive/run-* -name "*FAIL*" -delete
```

### Evidence Preservation
- Never delete evidence during active investigation
- Preserve all logs until failure is resolved
- Maintain chain of custody for audit purposes