# Human Execution Engine (HEE)

## Purpose

This document defines the **Human Execution Engine (HEE)** model used by `tick-task`.

It is a **normative definition**, not a metaphor.

Any system behavior, feature, or design decision that violates this definition
is considered out of scope or incorrect for this project.

---

## Formal Definition

A **Human Execution Engine (HEE)** is a bounded, stateful execution system in which
a human operator is treated as the **primary runtime**, and work is modeled,
scheduled, and evaluated using deterministic orchestration semantics rather than
ad-hoc task completion.

---

## Normative Properties

A system qualifies as a Human Execution Engine **if and only if** it satisfies
**all** of the following properties.

### 1. Execution Target

The execution target is a **single human operator**, explicitly modeled as a
constrained processing unit with finite capacity.

The human is:

- Not a passive assignee
- Not an approval gate
- The execution runtime itself

---

### 2. Executable Units

Work is represented as **executable units**, not reminders or intentions.

Each unit MUST define:

- A start condition
- A completion condition
- Explicit inputs and outputs (even if informal)
- A known or estimated execution cost

Tasks are runnable work units, not notes.

---

### 3. Dependency Graph

Executable units are arranged in an explicit dependency structure
(e.g., a directed acyclic graph).

- A unit MAY NOT enter a runnable state until all upstream dependencies are satisfied
- Ordering is derived, not manually imposed
- Arbitrary reordering without dependency changes is a semantic error

---

### 4. Scheduling Semantics

The system enforces **deterministic scheduling** over the human runtime.

This includes:

- Explicit limits on concurrency (typically 1)
- Controlled task admission
- Prevention of implicit multitasking
- Rejection of parallel execution that exceeds human capacity

Context switching is treated as a cost, not a free operation.

---

### 5. State and Transitions

The engine maintains explicit task state and enforces legal transitions.

Typical states include:

- Pending
- Runnable
- Active
- Blocked
- Completed
- Failed

State transitions are observable, intentional, and auditable.

---

### 6. Failure Semantics

Failure is a first-class outcome.

- Tasks may fail due to interruption, abandonment, or invalid assumptions
- Failure propagates downstream according to dependency rules
- Silent failure (forgotten or abandoned work) is treated as system failure

---

### 7. Throughput-Oriented Metrics

System health is measured by **execution characteristics**, not sentiment.

Valid metrics include:

- Time-to-runnable
- Time-to-completion
- Idle time
- Context switch count
- Flow efficiency
- Dependency wait time

Task completion counts alone are insufficient.

---

### 8. Orchestration Over Recall

The system optimizes execution correctness and flow, not memory augmentation.

- Reminders are secondary
- Notifications are optional
- Decision-making is front-loaded
- Execution is streamlined and constrained

---

## Non-Properties (Explicit Exclusions)

A Human Execution Engine is **not**:

- A to-do list
- A reminder system
- A habit tracker
- A calendar
- A gamified productivity tool
- A BPM engine with "human steps"
- An AI agent coordinator (unless the human remains the primary runtime)

If a user can arbitrarily execute work out of order without violating system
invariants, the system is **not** a Human Execution Engine.

---

## Litmus Test

A system qualifies as a Human Execution Engine **if and only if**:

> The human cannot execute work out of order without breaking the system model.

Most productivity tools fail this test immediately.

---

## Relationship to tick-task

`tick-task` is a **single-operator Human Execution Engine** that applies
deterministic orchestration semantics to human work execution.

It is not a task manager with opinions.
It is an execution runtime with constraints.
