# Execution contract

Use JSON when a task needs auditability, durable handoff, or multi-stage verification. Small tasks can keep a compact internal projection. Schema `1.0` is a local repository format, not an OpenAI product standard.

| Field | Meaning |
|---|---|
| schema_version, contract_id, revision | format, identity, positive revision |
| goal, deliverable | user goal and concrete output |
| protected_constraints | values that may not be silently weakened |
| gates | required property, verifier, status, evidence |
| required_outputs | PRESENT / MISSING / UNKNOWN |
| dependencies | READY / BLOCKED / UNKNOWN with expected and observed versions |
| effects | SUCCESS / FAILED / UNKNOWN_EFFECT / NOT_RUN |
| route | surface, requested/observed model, effort envelope, actuation |
| budget | only limits that are actually known |
| adaptation_envelope | choices Governor may change without re-planning |
| state_ref, next_action | durable state location and continuation point |

Gate states are `PASS`, `FAIL`, `UNCERTAIN`, and `NOT_RUN`. PASS requires evidence appropriate to the property. The validator checks structure and consistency; it does not prove evidence is true.

`COMPLETE` requires required outputs present, required gates passed, required dependencies ready with matching versions, and required effects verified successful.

Protected constraints and required gate definitions may only change through an explicit re-plan grounded in the user's current instructions and host rules.

Run:

```bash
python scripts/validate_contract.py assets/execution-contract.json
```

Use `--baseline <previous.json>` when checking whether a handoff silently weakened protected fields.
