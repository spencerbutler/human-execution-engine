# Confidence Score (R2) — evidence-first

We publish a bounded confidence score for release hygiene:

\[
Conf = 1 - \prod_{i}(1 - w_i s_i)
\]

Where each signal \(s_i \in [0,1]\) and weight \(w_i \in (0,1]\).

## Signals (initial)

- T: triad aligned (dev==stage==main)
- C: clean working tree
- R: GitHub Release object exists + published
- P: proof artifact exists and is honest about observation (`head_at_write`)

## Why this form

- bounded [0,1]
- monotonic: adding evidence never decreases confidence
- composable: add new signals without changing the contract

## Next tightening

- validate `head_at_write` ancestry vs tag commit
- incorporate CI green signals
- incorporate reproducible build artifacts (when present)
