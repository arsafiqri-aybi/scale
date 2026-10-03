---

<!-- SOURCE MODULE: README.md -->

# AI Decision Architecture — Architecture Specification

**Status:** Architecture candidate for benchmark; not yet final Skill implementation.  
**Date:** 2026-09-27  
**Input knowledge:** Evidence-audited Research Synthesis.

## Purpose
Specify the executable decision architecture shared by **Scale** and **Governor** without hard-coding fast-moving model/product facts or benchmark-derived thresholds that have not yet been calibrated.

## Core objective
1. Satisfy hard requirements, safety, and the required quality/reliability floor.
2. Within that feasible set, minimize unnecessary total resource.
3. Escalate the actual bottleneck rather than globally increasing every resource.
4. Preserve auditable project state, provenance, and recoverability.

## Architectural boundary
### Scale
Produces the **Execution Contract**: what work should exist, where it should run, what capability/effort/tool/context class each node needs, how it is verified, what can be adapted, and what requires re-planning.

### Governor
Operates **inside the Execution Contract** during execution. It allocates context, retrieval, compute, tools, reuse, verification depth, retries, and stopping based on observed progress and failure signals.

The Governor may not silently weaken:
- the user goal;
- hard constraints;
- critical acceptance criteria;
- risk/safety requirements;
- an Architect-imposed minimum capability;
- an Architect-imposed verification requirement.

## Architectural philosophy
The system is a closed-loop controller:
`State → classify → plan/route → execute → observe → verify → update state → stop/continue/escalate/replan`.

## Non-goals
- No universal numeric complexity weights.
- No permanent “best model” ranking.
- No fixed cheap-first cascade.
- No universal maximum context/reasoning budget.
- No assumption that more agents or more reasoning always improve quality.

---

<!-- SOURCE MODULE: Shared/00-decision-state-schema.md -->

# Shared 00 — Decision State Schema

The shared decision state is the canonical machine-operational representation used by both Skills.

```yaml
decision_state:
  schema_version: "1.0"

  identity:
    task_id: null
    project_id: null
    parent_task_id: null
    phase_id: null
    created_at: null
    updated_at: null

  intent:
    user_goal: ""
    deliverable: ""
    intended_use: ""
    quality_profile: quality_first
    deadline_or_latency: null

  constraints:
    hard: []
    soft: []
    forbidden: []
    preferences: []
    acceptance_criteria:
      critical: []
      important: []
      optional: []

  task_profile:
    ambiguity: unknown
    reasoning_depth: unknown
    constraint_interaction: unknown
    dependency_depth: unknown
    knowledge_context_demand: unknown
    freshness_need: unknown
    search_space: unknown
    novelty: unknown
    tool_dependence: unknown
    environment_dependence: unknown
    planning_horizon: unknown
    verification_difficulty: unknown
    consequence_of_error: unknown
    irreversibility: unknown
    human_judgment_dependence: unknown
    notes: []

  risk:
    reliability_level: R0
    residual_risk_tolerance: null
    approval_boundaries: []
    fail_posture: open_or_degraded
    trust_boundaries: []

  knowledge_state:
    current_project_state_ref: null
    required_context_classes: []
    missing_information: []
    freshness_unknowns: []
    evidence_refs: []
    provenance_required: false

  execution_state:
    status: PLANNING
    current_node: null
    completed_nodes: []
    blocked_nodes: []
    last_known_good_checkpoint: null
    failure_history: []

  resource_state:
    surface_limits: {}
    quota_or_credit_state: {}
    cumulative_usage: {}
    latency_observed: null
    cache_state: {}
```

## Rules
- Unknown is preferable to invented precision.
- Numeric scoring is optional and may only be introduced after benchmark calibration.
- Current state supersedes transcript chronology.
- Exact values, blockers, hard constraints, and provenance pointers must not be lossy-compressed.

---

<!-- SOURCE MODULE: Shared/01-policy-precedence.md -->

# Shared 01 — Policy Precedence

When two rules conflict, resolve them in this order:

1. Platform/system safety and legal constraints.
2. User hard constraints and explicit approvals.
3. Critical acceptance criteria and integrity requirements.
4. Reliability/risk constraints.
5. Architect Execution Contract.
6. Governor optimization policy.
7. Latency/convenience preferences.
8. Cosmetic optimization.

## Consequences
- Governor savings never override a critical acceptance criterion.
- A model/surface preference may be overridden only when it is impossible or violates a higher-order hard constraint; the reason must be exposed.
- Dynamic registry facts may invalidate a route, but they do not rewrite stable science.
- If evidence is insufficient for a high-consequence decision, the system may abstain/defer rather than invent certainty.

## Policy states
`REQUIRED`, `DEFAULT`, `HEURISTIC`, `EXPERIMENTAL`.

Experimental policies are not allowed to control high-consequence irreversible actions without stronger validation or human approval.

---

<!-- SOURCE MODULE: Shared/02-execution-node-contract.md -->

# Shared 02 — Execution Node Contract

Every material workflow node uses a structured contract.

```yaml
node:
  node_id: N-001
  goal: ""
  dependencies: []
  inputs: []
  locked_constraints: []
  flexible_constraints: []
  expected_output: ""
  output_schema: null

  criticality:
    downstream_impact: unknown
    error_consequence: unknown
    irreversibility: unknown
    verification_difficulty: unknown

  execution:
    preferred_surface_class: null
    capability_floor: null
    model_candidates: []
    effort_initial: null
    effort_ceiling: null
    allowed_tools: []
    permission_scope: []
    context_requirements: []

  verification:
    critical_gates: []
    verifier_channels: []
    pass_definition: ""
    false_pass_sensitivity: high

  adaptation_envelope:
    governor_may:
      - trim_or_expand_noncritical_context
      - choose_retrieval_depth
      - reuse_verified_artifacts
      - vary_reasoning_within_bounds
      - add_low-risk_verification
      - stop_when_passed
    governor_must_not:
      - weaken_hard_constraints
      - lower_capability_below_floor
      - skip_required_critical_gates
      - perform_unapproved_side_effects

  escalation:
    reasoning_deficit: ""
    information_deficit: ""
    model_ceiling: ""
    environment_deficit: ""
    verification_deficit: ""
    state_corruption: ""
    workflow_defect: ""

  checkpoint:
    commit_on_pass: true
    artifact_refs: []
```

Small tasks may use a compact projection of this schema rather than materializing every field.

---

<!-- SOURCE MODULE: Scale/00-architect-state-machine.md -->

# Scale 00 — Architect State Machine

```text
INGEST
  ↓
INTENT_NORMALIZATION
  ↓
MISSING_INFORMATION_CHECK
  ├─ resolvable safely → continue
  ├─ retrieval needed → ACQUIRE_INFORMATION
  └─ user decision essential → CLARIFY/DEFER
  ↓
TASK_RISK_PROFILE
  ↓
ENVIRONMENT_REQUIREMENTS
  ↓
DECOMPOSE_IF_JUSTIFIED
  ↓
DEPENDENCY + CRITICALITY MAP
  ↓
CANDIDATE_ROUTE_GENERATION
  ↓
REMOVE_INFEASIBLE / DOMINATED ROUTES
  ↓
SELECT INITIAL EXECUTION CONTRACT
  ↓
ATTACH QUALITY GATES + ESCALATION POLICY
  ↓
EMIT CONTRACT
```

## Re-planning triggers
Architect is re-entered when:
- a hard assumption is invalidated;
- required surface/model/tool becomes unavailable;
- repeated failure indicates workflow-level defect;
- dependency structure materially changes;
- Governor reaches an adaptation boundary without satisfying the gate;
- user changes a material goal/constraint.

The Architect is not re-entered for routine context trimming, retrieval-depth adjustment, or within-envelope effort changes.

---

<!-- SOURCE MODULE: Scale/01-routing-engine.md -->

# Scale 01 — Routing Engine

## Stage A — Feasibility filtering
Eliminate configurations that cannot satisfy environment, freshness, tool, permission, persistence, or hard capability requirements.

## Stage B — Capability matching
Map task profile to required capability dimensions. Build a small candidate pool from the dynamic registry.

## Stage C — Surface selection
Select the environment that provides the needed feedback and action loop. Surface is not a prestige hierarchy.

## Stage D — Model × effort selection
Choose an initial capability/effort point that is expected to meet the quality floor. Prefer direct strong routing when high capability need is predictable and expensive failure would make cheap-first escalation wasteful.

## Stage E — Verification assignment
Assign verifier channels to actual failure modes. Required verification is part of the route, not an afterthought.

## Stage F — Adaptation envelope
Set:
- capability floor;
- effort initial/ceiling;
- allowed alternate model/surface candidates;
- mandatory tools;
- mandatory quality gates;
- maximum same-strategy retries before re-plan.

## Router outputs
The router must explain:
- why the chosen environment fits;
- which requirement excludes cheaper/simpler alternatives;
- what evidence is uncertain;
- what event would cause effort/model/surface escalation.

---

<!-- SOURCE MODULE: Scale/02-project-orchestrator.md -->

# Scale 02 — Project Orchestrator

## Decomposition decision
Decompose only when it improves at least one of:
- specialization;
- dependency control;
- verification;
- safe parallelism;
- state isolation;
- recoverability.

Do not decompose merely because a project is large.

## Dependency rules
- Lock material upstream decisions before launching dependent work.
- Parallelize nodes only when dependencies are satisfied or intentionally independent.
- Mark critical-path nodes and high downstream-impact decisions.

## Intelligence placement
Spend stronger planning/review capability on nodes where an error has high downstream consequence or is difficult to verify. Use efficient workers for bounded, clear, verifiable execution.

## Topology choices
- Single agent.
- Planner → worker.
- Planner → worker → verifier.
- Manager → bounded specialists → manager synthesis.
- Independent candidates → verifier.
- Selective debate/search topology only when benchmark evidence justifies it.

## Durable project state
Maintain:
- current goals;
- active constraints;
- accepted decisions;
- artifact versions;
- milestone status;
- unresolved issues;
- dependency versions;
- evidence/provenance;
- last-known-good checkpoints.

---

<!-- SOURCE MODULE: Scale/03-architect-output-contract.md -->

# Scale 03 — Architect Output Contract

The default user-facing output is concise but operational.

```yaml
execution_architecture:
  summary:
    task_type: ""
    quality_target: ""
    risk_level: ""
    architecture_mode: single_task | multi_stage_project

  stages:
    - id: S1
      purpose: ""
      dependencies: []
      surface_class: ""
      model_or_capability_class: ""
      reasoning_policy: ""
      tools: []
      context_packet: []
      verifier: []
      pass_condition: ""
      escalation: ""
      handoff: ""

  global:
    project_state_strategy: ""
    checkpoint_policy: ""
    replan_triggers: []
    human_approval_boundaries: []
    dynamic_registry_facts_used: []
    unresolved_uncertainties: []
```

## Output discipline
- For a small task, collapse the schema into a short route recommendation.
- For a large project, show stages/dependencies explicitly.
- Do not expose internal numeric confidence that has not been calibrated.
- Do not claim a model is “best” universally; state task-specific fit and evidence status.

---

<!-- SOURCE MODULE: Governor/00-governor-control-loop.md -->

# Governor 00 — Governor Control Loop

The Governor runs after or inside an Architect Execution Contract.

```text
READ CONTRACT + CURRENT STATE
          ↓
CHECK MANDATORY FLOOR/GATES
          ↓
SELECT NEXT RESOURCE ACTION
          ↓
EXECUTE / OBSERVE
          ↓
UPDATE RESOURCE + PROGRESS STATE
          ↓
QUALITY GATE?
  ┌──────────┼───────────┐
 PASS       FAIL       UNCERTAIN
  │           │             │
 STOP     classify       acquire signal
 SUCCESS   failure           │
              ↓              │
      within envelope? ──────┘
        ┌─────┴─────┐
       YES          NO
        │            │
 adapt resource   REPLAN/ESCALATE
        │            │
        └────→ reverify
```

## Governor decisions
`CONTINUE`, `STOP_SUCCESS`, `STOP_STRATEGY`, `ESCALATE_WITHIN_ENVELOPE`, `REQUEST_REPLAN`, `PAUSE_BLOCKED`, `FAIL_CLOSED`.

The Governor never changes the goal or quality floor on its own.

---

<!-- SOURCE MODULE: Governor/01-context-retrieval-controller.md -->

# Governor 01 — Context & Retrieval Controller

## Context selection
Build active context from:
stable rules → current project state → current node contract → relevant accepted artifacts → targeted evidence → ephemeral tool results.

## Preserve
Hard constraints, exact values, blockers, exceptions, accepted decisions, acceptance criteria, provenance pointers, unresolved material uncertainty.

## Compress/archive
Exploratory dialogue, superseded alternatives, redundant tool output, stale logs, duplicated evidence—while retaining raw source externally when audit/recovery value exists.

## Retrieval controller
1. Decide whether external/project retrieval is needed.
2. Choose lexical/semantic/hybrid mode from the information need.
3. Apply metadata/trust/freshness constraints.
4. Retrieve broader candidate set when recall matters.
5. Rerank/deduplicate before active context.
6. Check material coverage and contradictions.
7. Stop when additional evidence is unlikely to change a material conclusion.
8. Re-open retrieval if generation exposes a new material information gap.

No fixed global top-k is specified before benchmark calibration.

---

<!-- SOURCE MODULE: Governor/02-compute-reuse-controller.md -->

# Governor 02 — Adaptive Compute, Cache, and Reuse

## Compute action set
- increase/decrease sequential reasoning effort;
- generate additional independent candidates;
- branch/search;
- add verification;
- targeted refinement;
- retrieve evidence;
- upgrade model within Architect envelope.

Spend on the action expected to attack the diagnosed bottleneck.

## Reuse
Reuse only when:
- semantic/task fit remains valid;
- relevant dependency versions match;
- freshness is acceptable;
- quality status is sufficient;
- privacy/scope permits reuse.

Prefer incremental revalidation to full recomputation when only a subset of dependencies changed.

## Cache classes
- runtime/prefix cache;
- exact result;
- semantic result;
- retrieval result;
- tool result;
- verified artifact;
- workflow template.

Side-effecting actions are not replayed as cached computations. Unknown action status requires state inspection before retry.

## Deduplication
Remove exact/semantic/computational duplication while preserving genuinely independent evidence or solution diversity.

---

<!-- SOURCE MODULE: Governor/03-stopping-and-recovery-controller.md -->

# Governor 03 — Stopping & Recovery Controller

## Stop success
Stop when:
- all critical acceptance criteria pass;
- important criteria meet their required threshold;
- no unresolved material blocker remains;
- additional expensive work has low expected material value.

## Stop strategy, not goal
If a critical gap remains but progress plateaus, stop the current strategy and choose a different intervention or request Architect re-plan.

## Retry rule
Retry only when at least one material condition changes:
- new evidence;
- different strategy;
- different capability/effort;
- corrected state;
- external feedback;
- narrowed failure localization.

## Failure classification
`AMBIGUITY`, `INFORMATION`, `CONTEXT`, `REASONING`, `MODEL_CEILING`, `ENVIRONMENT`, `VERIFICATION`, `STATE`, `WORKFLOW`, `TOOL`, `SECURITY`, `RESOURCE`.

## Recovery
Contain → preserve trace → localize root cause → repair/retrieve/rollback/escalate/replan → reverify → update regression memory.

## Hard ceilings
Architect/implementation may configure max same-class retries, max turns, max spend, max elapsed time, or approval boundaries. Hitting a ceiling is not “success”; report `BUDGET_EXHAUSTED`, `BLOCKED`, or `REPLAN_REQUIRED`.

---

<!-- SOURCE MODULE: Governor/04-governor-output-contract.md -->

# Governor 04 — Governor Output Contract

For every significant adaptation decision, maintain an internal record:

```yaml
governor_decision:
  state_id: ""
  current_node: ""
  observed_status: ""
  quality_gate_status: PASS | FAIL | UNCERTAIN | NOT_RUN
  diagnosed_bottleneck: ""
  resource_action: ""
  expected_benefit: ""
  constraints_checked: []
  cumulative_resource: {}
  adaptation_within_contract: true
  next_stop_or_escalation_trigger: ""
```

## User-facing behavior
Normally do not narrate every micro-decision. Surface:
- major route changes;
- material escalations;
- blocked conditions;
- quality/risk trade-offs;
- human approval needs;
- completion status.

This keeps the Governor operationally useful without turning resource governance into verbose overhead.

---

<!-- SOURCE MODULE: Integration/00-architect-governor-interface.md -->

# Integration 00 — Architect ↔ Governor Interface

## Immutable from Architect unless re-planned
- user goal;
- hard constraints;
- critical acceptance criteria;
- risk/reliability level;
- capability floor;
- required surface/tool capability;
- mandatory verifier channels;
- approval boundaries.

## Governor-adjustable
- active context size/composition;
- retrieval breadth/depth;
- cache/reuse;
- reasoning within allowed range;
- candidate count;
- optional verification;
- retry scheduling;
- local stopping;
- choice among pre-authorized alternatives.

## Governor → Architect re-plan request
```yaml
replan_request:
  reason: ""
  current_node: ""
  failed_gate: ""
  failure_class: ""
  attempts_summary: []
  evidence_observed: []
  current_strategy_plateau: true
  contract_boundary_reached: ""
  suggested_need: stronger_capability | different_surface | changed_decomposition | changed_dependency | human_decision
```

## Architect → Governor contract update
Must include explicit version increment and which fields changed. Governor must not merge incompatible old/new contracts silently.

---

<!-- SOURCE MODULE: Integration/01-lifecycle-and-state-machine.md -->

# Integration 01 — Lifecycle and State Machine

Canonical states:

`NEW → CLASSIFYING → PLANNED → READY → EXECUTING → VERIFYING`

Possible transitions:
- `VERIFYING → ACCEPTED → CHECKPOINTED → COMPLETE`
- `VERIFYING → REPAIRING → EXECUTING`
- `VERIFYING → REPLAN_REQUIRED → PLANNING`
- `EXECUTING/VERIFYING → BLOCKED`
- `EXECUTING/VERIFYING → APPROVAL_REQUIRED`
- `EXECUTING/VERIFYING → BUDGET_EXHAUSTED`
- any sensitive state → `FAIL_CLOSED`
- recoverable state → rollback to `LAST_KNOWN_GOOD`

## State invariants
- `COMPLETE` requires critical gates passed.
- `CHECKPOINTED` contains only accepted state.
- `SUPERSEDED` state remains auditable but is not active.
- Tool `ERROR` or `UNKNOWN_EFFECT` cannot be silently treated as success.
- Contract version mismatch forces reconciliation before execution.

---

<!-- SOURCE MODULE: Integration/02-failure-and-trust-boundaries.md -->

# Integration 02 — Failure & Trust Boundaries

## Trust tiers
T0 system/safety policy  
T1 user-approved current project state  
T2 verified internal artifacts  
T3 authoritative external evidence  
T4 general external content  
T5 arbitrary/untrusted content

Lower-trust data may inform conclusions but must not directly rewrite higher-trust control instructions.

## Consequential action pattern
`Propose → validate → approval if required → execute → verify resulting state → commit`.

## Failure posture
- R0 informational/reversible: fail open or degraded where appropriate.
- R1 project artifacts/reversible: preserve checkpoints and verify mutations.
- R2 connected side effects: approvals/idempotency/status verification.
- R3 high-impact/irreversible: fail closed on missing verification/approval.

Exact risk categorization is benchmark/policy-calibrated; these are architecture classes, not universal legal classifications.

---

<!-- SOURCE MODULE: Registry/00-dynamic-registry-interface.md -->

# Registry 00 — Dynamic Registry Interface

Fast-changing facts are injected through a registry and never baked into stable routing science.

```yaml
registry_snapshot:
  registry_version: ""
  valid_as_of: ""
  source_status: current

  surfaces:
    - id: ""
      availability: ""
      capabilities: []
      state_behavior: ""
      tool_access: []
      local_cloud_modes: []
      constraints: []
      resource_currency: []
      evidence_refs: []

  models:
    - id: ""
      provider: ""
      generation: ""
      availability_by_surface: {}
      capability_profile: {}
      reasoning_options: []
      context_limits: {}
      tool_support: []
      pricing_or_quota: {}
      latency_profile: {}
      known_regressions: []
      evidence_refs: []
      last_verified: ""
      update_triggers: []

  benchmarks:
    - id: ""
      construct: ""
      version: ""
      configuration_notes: ""
      contamination_risk: ""
      saturation_risk: ""
      evidence_refs: []
```

## Registry requirements
- Current facts must carry `valid_as_of`.
- Model comparisons must preserve task/configuration scope.
- Registry refresh is required before benchmark freeze and before final Skill installation.
- A registry change may invalidate routing tests without invalidating stable science.

---

<!-- SOURCE MODULE: Benchmark Contract/00-architecture-test-contract.md -->

# Benchmark Contract 00 — Architecture Test Contract

Architecture is not promoted until benchmarks test behavior, not only answers.

## Scale Architect tests
- task/surface feasibility;
- correct identification of missing information;
- under-routing vs over-routing;
- model-vs-effort choice;
- dependency-aware project decomposition;
- criticality placement;
- appropriate single-agent vs multi-agent choice;
- escalation and re-plan triggers.

## Resource Governor tests
- context preservation vs compression;
- retrieval coverage/noise/stopping;
- cache/reuse validity and invalidation;
- adaptive effort/candidate allocation;
- retry stagnation detection;
- stop-success vs stop-strategy;
- critical-gate preservation;
- total resource per accepted result.

## Integration tests
- Governor never violates Architect floors;
- replan request occurs at contract boundary;
- project state remains consistent across handoff;
- stale/superseded state does not regain authority;
- failure recovery returns to known-good state;
- dynamic registry update changes only affected routes.

## Baselines
- always strongest reasonable configuration;
- always workhorse configuration;
- simple difficulty heuristic;
- no Governor;
- fixed cheap-first cascade.

## Acceptance principle
Quality regression on critical criteria is not traded for resource savings. Resource improvements are counted only when the accepted-outcome requirement is preserved.

---

<!-- SOURCE MODULE: Benchmark Contract/01-open-calibration-items.md -->

# Benchmark Contract 01 — Open Calibration Items

These parameters are intentionally unresolved in Architecture:

1. Current model/surface registry values.
2. Model × effort quality/resource curves.
3. Cross-domain handoff policy.
4. Compression triggers and fidelity thresholds.
5. LLM-judge calibration and pass thresholds.
6. Task-complexity dimension weighting.
7. Resource utility weighting across tokens, latency, quota, and human time.
8. Exact retry/turn ceilings by task/risk class.
9. Retrieval breadth/reranking thresholds.
10. Criteria for spawning additional agents/candidates.

The benchmark phase must either:
- estimate/calibrate them;
- keep them adaptive/qualitative; or
- explicitly decide they are unnecessary.

No arbitrary constants should be promoted merely to make the architecture look complete.