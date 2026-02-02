# Hello World Workload (Deterministic)

Purpose:

- Prove CI execution can proceed after governance gates pass.
- Minimal, dependency-free, deterministic.

Behavior:

- Prints a deterministic message and verifies basic CI invariants.
- Exits 0 on success, non-zero on failure.

Constraints:

- No network.
- No external dependencies beyond POSIX shell utilities.
