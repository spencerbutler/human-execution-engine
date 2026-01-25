# HEE Tooling

This directory contains *derivative* tools for distributing and validating Human Execution Engine (HEE) doctrine.

Authoritative doctrine:

- docs/
- prompts/
- contracts/

Tools:

- tooling/bin/hee-vendor  : vendor doctrine into a repo (vendored mode)
- tooling/bin/hee-attach  : attach doctrine locally without committing it (detached mode)
- tooling/bin/hee-sync-cursor-prompts : derive .cursor/prompts from the active policy source
- tooling/bin/hee-check   : boundary/compliance checks
