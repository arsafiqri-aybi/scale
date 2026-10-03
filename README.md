# Scale

**Design the execution architecture for AI work: decomposition, dependencies, capability floors, model/effort ranges, tools, verification, handoff, and re-planning.**

Scale decides **what execution structure should exist** before or during complex work. It creates an execution contract that Governor can optimize inside without silently weakening the user's goal, hard constraints, or required quality gates.

## Runtime identifier

`scale`

## Core boundary

- **Scale**: architecture, routing envelope, dependencies, quality gates, verification, re-plan triggers.
- **Governor**: dynamic resource allocation inside that envelope: context, retrieval, effort, retries, reuse, and stopping.

Small tasks should stay small. Scale should not add orchestration when the direct path is already clear.

## Repository structure

- `SKILL.md` — canonical runtime behavior.
- `references/` — execution contract, failure/escalation, model/effort, and handoff guidance.
- `knowledge/` — deeper shared decision architecture.
- `scripts/validate_contract.py` — deterministic contract checker.
- `scripts/audit_skill.py` — read-only repository/Skill audit.
- `evaluation/STATUS.md` — evidence boundaries.
- `assets/execution-contract.json` — example contract.

## Knowledge loading

Start with `SKILL.md`. Open a reference only when that decision is material. Use `knowledge/README.md` for deeper architectural rationale. Full access does not mean loading the full knowledge base into every task.
