# Human Execution Engine Runtime (HEER)

## Purpose

This document defines the **Human Execution Engine Runtime (HEER)** abstraction
layer used by `tick-task`.

HEER is the **enforcement layer** of the Human Execution Engine (HEE) model.
If HEE defines *what the system is*, HEER defines *how the system behaves*.

Any implementation detail, feature, or integration that violates this runtime
contract is considered **non-compliant**.

---

## Relationship to Human Execution Engine (HEE)

- **HEE** defines the conceptual model:
  - A human is the primary execution runtime
  - Work is orchestrated, not recalled
  - Execution is constrained, deterministic, and measurable

- **HEER** defines the operational substrate:
  - State machines
  - Scheduling semantics
  - Admission control
  - Event journaling
  - Deterministic replay

A system may claim HEE intent.
A system only *is* an HEE if it implements a HEER.

See: [Human Execution Engine](HEE.md)

---

## Formal Definition

A **Human Execution Engine Runtime (HEER)** is a deterministic execution runtime
that:

1. Maintains authoritative task state
2. Enforces dependency-aware admissibility
3. Schedules work against a constrained human operator
4. Records all state transitions as durable, replayable events
5. Produces execution metrics derived exclusively from event history

The runtime MUST be deterministic under replay given the same event stream and
policy configuration.

---

## Core Runtime Entities

### Work Unit (Task)

A **Task** is an executable unit of work with defined semantics.

Each Task MUST have:
- A stable identifier
- A specification (title + optional description)
- A start condition
- A completion condition
- Explicit inputs and outputs (may be informal)
- A cost model (estimate, class, or heuristic)
- Zero or more dependency edges

Tasks are runnable work units, not reminders or intentions.

---

### Human Operator

The **Operator** represents the human execution runtime.

Properties:
- Stable identity (often single-operator)
- Finite execution capacity
- Explicit concurrency limits (`max_concurrency`, default = 1)

The operator is not an assignee or approval step.
The operator is the runtime itself.

---

### Runtime Policy

A **Runtime Policy** defines admissibility and scheduling rules.

Examples:
- Concurrency limits
- Time-of-day constraints
- Required execution conditions (location, tooling, focus block)
- Ordering preferences
- Tie-breaking rules

Policies MUST be versioned and recorded as events.

---

### Execution Event

An **Event** is an immutable fact describing a state transition or configuration
change.

Events form the sole source of truth for runtime state and metrics.

---

## Task State Machine (Normative)

A HEER MUST implement and enforce explicit task states.

Minimum required states:

- `PENDING`   — defined but not yet eligible
- `RUNNABLE`  — dependency-satisfied and policy-admitted
- `ACTIVE`    — currently assigned to an operator
- `BLOCKED`   — temporarily non-executable with declared reason
- `COMPLETED` — completion condition satisfied
- `FAILED`    — terminal failure
- `CANCELLED` — terminal cancellation

---

### Legal State Transitions

- `PENDING → RUNNABLE`
  Only when all dependencies are satisfied **and** policy admits.

- `RUNNABLE → ACTIVE`
  Only via scheduler admission. User-driven picking is not allowed.

- `ACTIVE → COMPLETED`
  Only when completion condition is asserted.

- `ACTIVE → FAILED`
  Allowed and must record a failure reason.

- `ANY → BLOCKED`
  Allowed with explicit blocking reason.

- `BLOCKED → RUNNABLE`
  Only when unblocked and dependencies are satisfied.

Illegal transitions MUST be rejected.

---

## Runtime Components

### 1. Task Graph Manager

Responsibilities:
- Maintain dependency edges
- Detect and reject dependency cycles
- Compute dependency readiness
- Propagate completion and failure downstream

Requirements:
- Dependency evaluation MUST be deterministic
- Cycles MUST NOT silently pass

---

### 2. Admission Controller

Responsibilities:
- Determine whether a dependency-ready task may enter the runnable set
- Enforce runtime policy constraints beyond dependency satisfaction

Key distinction:
A task may be dependency-ready but still **not admitted**.

---

### 3. Scheduler

Responsibilities:
- Select the next executable unit(s) from admitted runnable tasks
- Enforce operator capacity constraints
- Minimize context switching according to policy

Normative constraints:
- If `max_concurrency = 1`, the scheduler MUST present at most one ACTIVE task
- Scheduler decisions MUST be deterministic under replay

---

### 4. Execution Journal (Event Store)

Responsibilities:
- Record all meaningful runtime changes as immutable events
- Support full state reconstruction via replay
- Enable metric derivation without mutable counters

Minimum event types:
- `TASK_CREATED`
- `DEPENDENCY_ADDED`
- `DEPENDENCY_REMOVED`
- `TASK_ADMITTED`
- `TASK_ACTIVATED`
- `TASK_BLOCKED`
- `TASK_UNBLOCKED`
- `TASK_COMPLETED`
- `TASK_FAILED`
- `TASK_CANCELLED`
- `POLICY_SET`
- `POLICY_UPDATED`

Metrics MUST be derived from events, not stored as state.

---

### 5. Integration Boundary (Adapters)

Responsibilities:
- Translate external systems into validated runtime commands
- Examples:
  - CLI
  - File imports
  - Calendar signals
  - Notifications

Constraint:
Integrations MUST NOT directly mutate runtime state.
All changes occur through validated commands that emit events.

---

## Runtime Interface (Conceptual)

### Command Interface (Write Path)

- `CreateTask(spec) → task_id`
- `AddDependency(task_id, depends_on_id)`
- `RemoveDependency(task_id, depends_on_id)`
- `BlockTask(task_id, reason)`
- `UnblockTask(task_id)`
- `ActivateNext(operator_id) → task_id | none`
- `CompleteTask(task_id, evidence?)`
- `FailTask(task_id, reason)`
- `CancelTask(task_id, reason)`
- `SetPolicy(policy_version, policy_blob)`

---

### Query Interface (Read Path)

- `GetTask(task_id)`
- `ListRunnable(operator_id)`
- `GetActive(operator_id)`
- `GetNext(operator_id)`
- `GetGraph(task_id?)`
- `GetEvents(filter)`
- `ComputeMetrics(window)`

---

## Determinism and Replay

A HEER MUST support:

- Full state reconstruction via event replay
- Deterministic scheduling decisions under replay
- Stable tie-breaking rules (e.g., task ID, creation time)

Non-deterministic scheduling violates the HEER contract.

---

## Failure Semantics and Propagation

Default behavior:

- If a dependency enters `FAILED` or `CANCELLED`,
  downstream tasks become `BLOCKED` with an explicit reason.

Overrides:
- Allowed only via explicit override commands
- Overrides MUST be recorded as events with rationale

Silent continuation is not permitted.

---

## Metrics (Derived Only)

HEER MUST be able to derive, at minimum:

- Time-to-runnable
- Time-in-runnable-queue
- Active execution time
- Blocked time
- Context switch count
- Flow efficiency

Metrics are computed from event timestamps, not maintained as counters.

---

## Compliance Test (Litmus)

A runtime is HEER-compliant **if and only if**:

> The next executable task is determined by the runtime, not by user choice,
> and executing work out of order constitutes a semantic violation.

---

## Role in tick-task

Within `tick-task`, HEER is the architectural spine:

- CLI is an adapter
- Files are adapters
- UI is a view
- Metrics are journal-derived
- Tests are replay-based

All future features are constrained by this runtime contract.
