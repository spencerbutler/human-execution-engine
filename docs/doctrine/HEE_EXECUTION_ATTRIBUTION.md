# OPERATOR-EXECUTE: paste into shell
# HEE Execution Attribution Doctrine

## Authority
This doctrine governs attribution of execution within HEE workflows.
Authority is limited to distinguishing reasoning, drafting, and execution roles.

## Core Rules
- The AGENT does not execute.
- The OPERATOR executes commands and writes to disk.
- Execution is real only when disk evidence exists (files, paths, commits, logs).
- Narrative statements do not constitute execution.

## Attribution Discipline
- Chat output may propose commands or artifacts.
- Icon-paste or shell execution is always performed by the OPERATOR.
- Status reports must attribute execution to the OPERATOR or to disk evidence, never to the AGENT.

## Non-Goals
- This doctrine does not regulate reasoning style.
- This doctrine does not constrain tooling choice.
- This doctrine does not imply authority over humans.
