# 🟥 RED CARD — Non-canon markdownlint invocation

- Violation: emitted `markdownlint-cli2` direct invocation despite repo canon `npx markdownlint-cli2`.
- Outcome: command not found; operator churn.
- Policy: never assume tool presence; use repo-canon invocation paths.
- Remediation: record addendum and avoid future direct tool invocations unless proven installed.
