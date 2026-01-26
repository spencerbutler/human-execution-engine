# HEE SVL Doctrine

## Authority

This doctrine defines the authority and invariants of SVL as a signal-level construct within HEE.
Authority is limited to explicit SVL state definitions and behavioral constraints on signal handling.
This doctrine grants no authority beyond SVL-defined boundaries.
Authority stops at system boundaries defined by explicit HEE operational contracts.
No implicit, inherited, or global authority is claimed.

## Scope

SVL applies to the validation, classification, and routing of signals within HEE execution contexts.
SVL applies to signals exchanged across agent–operator boundaries, not to the actors themselves.
SVL applies to signal handling during state preservation and recovery operations.

SVL does not apply to external system integrations.
SVL does not apply to human–human communication.
SVL does not apply to implementation mechanisms outside defined signal boundaries.

## Core Invariants

Silence is an operational construct.
Silence does not imply absence of activity.
No inference may be drawn from silence without a declared observation scope.

Violations represent factual system states.
Violations do not imply intent, fault, or moral failure.

All signal classifications must be explicit and enumerable.
Signals that cannot be classified are invalid.
Invalid signals must be rejected and must not be transformed.

Claims of execution require verifiable disk artifacts.
State preservation requires disk-backed evidence.

## Explicit Non-Goals

SVL does not provide moral guidance.
SVL does not enforce human behavior.
SVL does not interpret intent.
SVL does not generate content.
SVL does not maintain history beyond operational requirements.
SVL does not provide user interfaces.
SVL does not implement business logic.
