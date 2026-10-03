# Model and reasoning-effort guide

This is a routing guide, not a permanent ranking. Model names, availability, effort labels, quotas, tools, and surfaces can change; verify current facts before applying a route.

## Selection order

1. Choose an environment that actually has the required files, tools, permissions, state, and feedback loop.
2. Set the minimum capability floor implied by reasoning depth, constraint interaction, novelty, error consequence, and verification difficulty.
3. Choose an available model that meets that floor.
4. Choose the lowest reasoning effort likely to pass required gates without creating expensive rework.
5. Define an effort ceiling and escalation trigger.

## Effort semantics

- **none / low** — bounded transformations, extraction, formatting, local edits, or highly verifiable work.
- **medium** — normal multi-step analysis, coding, synthesis, and planning.
- **high** — interacting constraints, harder diagnosis, edge cases, or costly mistakes.
- **xhigh / max** — deepest available reasoning only when a material gap remains and verification can detect improvement.

Effort is not IQ, output length, confidence, or permission. A stronger model at lower effort may outperform a lighter model at higher effort. More effort cannot replace missing information, unavailable tools, or broken state.

## Escalation

Escalate when the current route fails for a diagnosed reasoning/capability reason. Change information, context, tools, environment, or verifier instead when those are the actual bottleneck. Do not force a low→medium→high→max ladder.

## Dynamic registry

Stable architecture should not hard-code a universal model leaderboard. Current model/surface facts belong in a dated registry with:
- availability by surface;
- reasoning options;
- tool support;
- context limits;
- pricing/quota facts;
- latency;
- known regressions;
- evidence sources and last-verified date.

Historical benchmark snapshots may guide priors but never replace task-specific verification.
