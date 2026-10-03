---
name: scale
description: "Design the execution architecture for AI tasks or projects: decomposition, dependencies, capability and effort ranges, tools, verification, handoff, and re-planning. Use when the execution path materially affects success, when work spans multiple dependent stages, or when the user asks for Scale. Skip simple tasks with an obvious route; Governor manages resources inside the contract."
---

# Scale

Design the smallest execution architecture that can reliably produce the user's accepted result. Preserve the latest goal, hard constraints, authorization boundaries, required quality, and current state. More capability is not automatically better; unnecessary architecture is failure too.

## 1. Establish the task contract

Identify:
- user goal and deliverable;
- intended use and acceptance criteria;
- hard vs soft constraints;
- required inputs, freshness, tools, permissions, and environment;
- consequence of error, reversibility, and verification difficulty.

Do not compress missing information, reasoning difficulty, tool need, and risk into one invented score. If a simple task has a clear route, execute directly with proportional verification.

## 2. Design the route

Filter out infeasible routes first. Then choose only the structure needed:

- direct single-agent execution;
- planner → worker;
- planner → worker → verifier;
- bounded specialists with synthesis;
- independent candidates with verification.

Decompose only when it improves specialization, dependency control, verification, safe parallelism, state isolation, or recoverability.

For each material node define dependencies, output, criticality, capability floor, allowed model/effort range, tools, context needs, verifier, pass condition, and escalation trigger.

Use [model and effort guidance](references/model-effort-guide.md) as a dated prior, not a permanent ranking. Current availability must come from the host or current authoritative sources.

## 3. Emit an execution contract

For work that benefits from audit or handoff, use [the execution contract](references/execution-contract.md) and the example in `assets/execution-contract.json`.

Separate:
- protected constraints;
- required outputs;
- required quality gates;
- dependency versions;
- required external effects;
- routing envelope;
- adaptation envelope;
- budget facts that are actually known.

Scale sets the envelope. **Governor may optimize inside it but may not silently weaken the goal, hard constraints, capability floor, mandatory verifier, or approval boundary.**

## 4. Attach verification and recovery

Verification is part of architecture, not a final decoration. Match verifier channels to the failure mode: parser/schema checks, calculations/tests, authoritative sources, external-state inspection, or human judgment.

Use [failure and escalation](references/failure-and-escalation.md) when progress stalls. Re-enter Scale when:
- a hard assumption is invalidated;
- a required environment/tool becomes unavailable;
- dependency structure materially changes;
- repeated failure indicates workflow defect;
- Governor reaches the contract boundary without passing;
- the user changes a material goal or constraint.

Routine context trimming, retrieval depth, effort changes inside the envelope, and optional verification do not require a full re-plan.

## 5. Preserve project state and handoff

For multi-stage work, use [project and handoff guidance](references/project-and-handoff.md). Lock accepted upstream decisions before dependent work. Invalidate only affected descendants when an upstream dependency changes.

Preserve exact numbers, negations, exceptions, source/version pointers, accepted decisions, unresolved uncertainty, and last-known-good checkpoints.

## 6. Finish with evidence

Use status precisely:
- `COMPLETE`: required outputs exist, required gates pass, required dependencies match, and required effects are verified.
- `BLOCKED`: essential input/access/capability is unavailable.
- `REPLAN_REQUIRED`: current architecture is no longer viable.
- `APPROVAL_REQUIRED`: a genuinely new authorization is needed.
- `BUDGET_EXHAUSTED`: an observed resource limit was reached before completion.
- `FAIL_CLOSED`: stop risky action when integrity or authorization is uncertain.

Validate JSON contracts with `python scripts/validate_contract.py <contract.json>`. The validator checks structure and status consistency, not truth of evidence.

Report only the route, material decisions, verification, and unresolved limits that help the user. Do not narrate every internal control decision.
