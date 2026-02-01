# hee-sqz-roll-v1

## Definition
A **SQZ roll** converts one UNKNOWN axis into one KNOWN signal using exactly one source artifact.

## Hard rules
- One roll = one signal = one axis
- Output summary ≤5 lines
- No vibes, only observable facts
- UNKNOWN ≠ negative
- If source is unreachable/unreadable → axis remains UNKNOWN

## Invariants (required)
- NOW_UTC
- evaluator_id
- source_pointer

## Axes (allowed)
- execution_history
- signal_to_noise
- hee_alignment
- scope_scale
- teaching_doctrine
- locality_overlap

## Confidence (allowed)
- low
- med
- high

## Output format (≤5 lines)
NOW_UTC=<iso8601>
EVALUATOR=<id>
CANDIDATE=<name>
AXIS=<axis>
SIGNAL=<one concrete, observable fact>
CONFIDENCE=<low|med|high>
SOURCE=<pointer>

(If you must stay ≤5 lines, fold CANDIDATE+AXIS and fold SOURCE into SIGNAL.)

## Stop conditions
- Axis reaches CONFIDENCE=high
- Two consecutive rolls yield no new signal
- SQZ-10 limit reached

## Doctrine tests
- PTS-RESISTANCE-01: missing/unreadable source cannot produce derived facts
- SQZ-ROLL-≤5-01: rendered roll summary ≤5 lines
- SQZ-ROLL-INVARIANTS-01: NOW_UTC + evaluator_id + source_pointer required
