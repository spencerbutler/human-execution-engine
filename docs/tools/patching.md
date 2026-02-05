# Patching in HEE (CBA safe)

This repo standardizes patch application to reduce:

- terminal and UI failures from large paste blocks
- git apply failures from malformed hunks
- confusion about wrapper tools versus implementation
- wrong branch commits

## Tools

- tools/git/apply-var-patch is a wrapper.
  - It execs tools/git/patch-apply.

- tools/git/patch-apply is the implementation.
  - Input precedence:
    1. --file PATH
    2. --patch TEXT
    3. stdin (non TTY, non empty)
    4. env VAR (supports indirection and file path)
  - Normalization:
    - CRLF to LF
    - strips BOM
    - trims leading whitespace
    - ensures trailing newline
  - Validation:
    - hard fails unless patch starts with: diff --git
  - Apply:
    - default: git apply
    - --check: git apply --check
    - --index: git apply --index

## Canonical operator workflow (recommended)

Avoid large diffs pasted into the terminal. Prefer patch files on disk.

1. Create a patch file.

   - /tmp/TOPIC-NNN-DESC.patch

2. Validate.

   - VAR=/tmp/TOPIC-NNN-DESC.patch tools/git/apply-var-patch --check

3. Apply.

   - VAR=/tmp/TOPIC-NNN-DESC.patch tools/git/apply-var-patch

## Common failure modes and diagnosis

### error: corrupt patch at line N

This usually indicates a syntactically malformed patch, not a context mismatch.

High probability causes:

- incorrect hunk header line counts (the @@ header does not match the diff body)
- missing diff header lines (diff --git, --- , +++)
- patch file polluted by paste collisions or line wrapping

Fast diagnosis:

- nl -ba /tmp/TOPIC-NNN-DESC.patch | sed -n "1,120p"
- python3 tools/git/patch-apply --debug --file /tmp/TOPIC-NNN-DESC.patch --check

### Wrong branch

Always verify branch before applying or committing.

Recommended guard:

- hee_ensure_branch EXPECTED_BRANCH

## Notes

- VAR may point directly to a patch file path. This exists to keep patches file based and reduce terminal paste risk.
- --terse may be used for tight automation loops where output is undesirable.

## Notes: ripgrep regex engine

- `rg` (Rust regex) does **not** support look-around (look-ahead / look-behind). Avoid patterns like `^(?!tools/)`.
- Prefer invert-match gates instead, e.g. `rg -v '^tools/'` or `grep -v '^tools/'`.
