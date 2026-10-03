# Repository architecture

Scale is a planning and routing capability, not a resource governor.

Authority order:
1. `SKILL.md` — active runtime.
2. `references/` — operational detail.
3. `knowledge/` — deeper architecture and rationale.
4. Git history — change provenance.

Scale outputs an execution contract. Governor may adapt only inside its declared envelope. If the envelope becomes infeasible or a hard assumption changes, control returns to Scale for re-planning.

Fast-changing model/product facts must be kept separate from stable routing science.
