# shellboss fs write-stdin

## Purpose

Write stdin to a file **without clobbering** existing files.

## Command

- `shellboss fs write-stdin <path>`

## Behavior

- Creates parent directories as needed.
- Refuses to overwrite an existing `<path>`.

## Return codes

- `0` ok
- `2` usage / invalid command
- `73` clobber refused (target exists)

## Machine-readable footer

On success, prints:

- `SB_STATUS=ok`
- `SB_RC=0`
- `SB_OP=fs.write-stdin`
- `SB_PATH=<path>`
- `sha256sum <path>`
