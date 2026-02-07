# PR119 Proof Triplet v1

## Issues

- #120 (p2) — disposition: **defer (CBA)**, not a merge blocker.

## Live output

- generator: `library/py/hee_index/gen_indices.py`
- outputs:
  - canon index: <https://raw.githubusercontent.com/spencerbutler/human-execution-engine/89165c1807e621ce6ffeaa48c854c2a0d8ed4509/hee/evidence/index/canon.index.v1.json>
  - repo files: <https://raw.githubusercontent.com/spencerbutler/human-execution-engine/89165c1807e621ce6ffeaa48c854c2a0d8ed4509/hee/evidence/index/repo.files.v1.json>

## Hash math (real)

- policy: `sqz-token-hash.v1`
- aggregate_sha256: `ba7f09d937e8c4704078b13ec2f158e4f593bd680a8468104ff948179d9d01ed`
- token: `ba7f09d937e8c470`

## METs (yaml)

```yaml
mets:
  pr:
    number: 119
    branch: p0/governance-pretty-template-and-placeholder-postmortem
    head_sha: 89165c1807e621ce6ffeaa48c854c2a0d8ed4509
    base: main
    base_sha: e0ca3ffa4c78c15dd8d2610b0577049a2575f608
  diff:
    commits: 3
    files_changed: 9
  evidence:
    outdir: /tmp/hee.pr119.prooftriplet.resume.7aq2EI
```

## Terminal color evidence (tput/hex)

Raw escape proof (hex):

- GREEN: `1b 5b 33 32 6d 47 52 45 45 4e 1b 28 42 1b 5b 6d`
- RED (via pipe/tee): `1b 5b 33 31 6d 52 45 44 1b 28 42 1b 5b 6d`

Interpretation:

- ANSI escapes are present (color is real).
- Color suppression is a TTY-detection behavior; must force color/tty in tee pipelines.
