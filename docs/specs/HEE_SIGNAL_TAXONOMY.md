# HEE Signal Taxonomy Specification

## Overview

This specification defines the complete taxonomy of signals within HEE SVL scope. All signals must be classified into exactly one of the defined classes. Signals that cannot be classified are invalid.

## Signal Classes

### COMMAND
Signals requesting execution of operations.

**Required Properties:**
- `action`: String, one of {EXECUTE, VALIDATE, PRESERVE, RECOVER}
- `target`: String, operation target identifier
- `parameters`: Object, execution parameters
- `timestamp`: ISO 8601 timestamp
- `authority`: String, authority scope declaration

**Valid States:**
- PENDING: Awaiting execution
- EXECUTING: Operation in progress
- COMPLETED: Operation finished successfully
- FAILED: Operation finished with error

### STATE
Signals reporting system or component state.

**Required Properties:**
- `subject`: String, state subject identifier
- `state`: String, current state value
- `evidence`: String, disk-backed evidence path
- `timestamp`: ISO 8601 timestamp
- `scope`: String, observation scope declaration

**Valid States:**
- OBSERVED: State captured from system
- PRESERVED: State written to disk
- VERIFIED: State confirmed against evidence

### VALIDATION
Signals confirming or rejecting signal validity.

**Required Properties:**
- `target_signal`: String, signal being validated
- `result`: Boolean, validation outcome
- `criteria`: String, validation criteria applied
- `timestamp`: ISO 8601 timestamp
- `authority`: String, validation authority scope

**Valid States:**
- PASS: Signal meets all criteria
- FAIL: Signal violates criteria
- UNDEFINED: Signal cannot be evaluated

### ERROR
Signals reporting violations or system failures.

**Required Properties:**
- `violation_type`: String, one of {AUTHORITY, SCOPE, INVARIANT, EXECUTION}
- `description`: String, factual error description
- `evidence`: String, error evidence path
- `timestamp`: ISO 8601 timestamp
- `recovery_required`: Boolean

**Valid States:**
- REPORTED: Error detected and logged
- CONTAINED: Error impact bounded
- RECOVERED: Error resolved with evidence

### BOUNDARY
Signals declaring scope or authority boundaries.

**Required Properties:**
- `boundary_type`: String, one of {AUTHORITY, SCOPE, CONTEXT}
- `declaration`: String, boundary definition
- `constraints`: Array, boundary constraints
- `timestamp`: ISO 8601 timestamp
- `enforcement`: String, enforcement mechanism

**Valid States:**
- DECLARED: Boundary established
- ENFORCED: Boundary actively maintained
- VIOLATED: Boundary breached (triggers ERROR signal)

## Invalid and Undefined States

### Classification Failures
Signals missing required properties for their declared class are invalid.
Signals with malformed required properties are invalid.
Signals claiming undeclared classes are invalid.

### Content Violations
Signals containing aspirational language are invalid.
Signals making claims without disk evidence are invalid.
Signals attempting inference from silence without declared scope are invalid.

### Processing Rules
Invalid signals must be rejected.
Invalid signals must not be transformed.
Invalid signals must trigger ERROR signal with classification failure details.

## This Is Not a Signal

The following are not signals and must not be classified as such:

- Natural language text without structured properties
- File contents without signal metadata
- Network packets without HEE signal headers
- Log entries without signal classification
- Human utterances without signal structure
- Implementation artifacts without signal declaration
- Documentation without executable signal properties

## Implementation Requirements

Signal classification must be deterministic.
Signal validation must be automated.
Signal state transitions must be logged.
Signal authority must be verified before processing.
