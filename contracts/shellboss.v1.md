# SHELLBOSS v1 (Shell Manager Contract)

## Primary directives (A1)

- NO CLOBBER by default. Refuse overwrite unless explicitly forced.
- Never report success if no write happened.
- Invalid/unknown commands MUST return nonzero.

## CLI

- `shellboss fs write-stdin <path>`: writes stdin to new file, refuses if exists.

## Return codes

- 0 ok
- 2 usage / invalid command
- 73 clobber refused (target exists)

## Repo-managed

- `tools/shellboss/shellboss`
- `tools/shellboss/library/bash/*.shfn.bash`
- `tools/shellboss/install.sh`
