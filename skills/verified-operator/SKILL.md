---
name: verified-operator
description: Operate across live systems with verification, evidence, recovery, and state tracking. Use when Codex must coordinate files, terminals, browsers, APIs, devices, or external services; take actions instead of only advising; prove each change with receipts such as logs, screenshots, diffs, or API responses; manage approvals for risky steps; or recover from drift in long-running, high-stakes, or multi-step tasks.
---

# Verified Operator

## Goal

Turn a request into verified execution, not plausible narration.

Build a live world model, choose the safest next mutation, verify every action with independent receipts, and recover cleanly when the environment changes underneath you.

For superhuman-complexity tasks — multi-phase migrations, many-system orchestrations, operations with dozens of interdependencies — go further: model dependency graphs, score verification confidence, monitor invariants continuously, classify failure modes precisely, reason about time-dependent operations, and orchestrate across phases that no single human could track.

## Quick Start

For every action you take:

```text
1. BEFORE  → What is the current verified state?
2. RISK    → L0 observe | L1 local+reversible | L2 external | L3 destructive
3. ACT     → One bounded change (L2+ needs user approval)
4. PROVE   → Capture a receipt (output, diff, screenshot, status code)
5. CONFIRM → Does the receipt match what you expected?
              YES → update ledger, continue
              NO  → stop, diagnose, recover or escalate
```

This is the entire skill compressed into five steps. The sections below expand each one with full guidance, edge cases, and templates.

### Complex Mode (§16–§21)

For tasks spanning many systems, phases, or hours, add these before Step 1:

```text
0a. GRAPH    → Map system dependencies as a DAG. Which systems block which?
0b. PHASE    → Break the task into named phases with entry/exit criteria.
0c. INVARIANTS → Define what must NEVER break (hard) and what can flex (soft).
```

And upgrade Step 4–5 with:

```text
4b. CONFIDENCE → Score each receipt 0.0–1.0. Below 0.7? Halt. 0.7–0.9? Add secondary check.
5b. TIMING     → Is this result time-dependent? Wait for propagation before verifying.
5c. FAILURE    → Classify: transient | permanent | cascading | silent | delayed.
```

## Operating Loop

Use this loop in order:

1. Map the world.
2. Grade risk.
3. Design the smallest useful action.
4. Execute one bounded mutation.
5. Verify with receipts.
6. Update the world model.
7. Recover, escalate, or continue.
8. Close only on verified end state.

Do not skip verification just because a command exited successfully.

### Decision Flowchart

```text
                        ┌──────────────┐
                        │  New Request  │
                        └──────┬───────┘
                               ▼
                     ┌─────────────────────┐
                     │  1. Map the world   │
                     │  (build ledger)     │
                     └─────────┬───────────┘
                               ▼
                     ┌─────────────────────┐
                     │  2. Grade risk      │
                     │  (L0/L1/L2/L3)      │
                     └─────────┬───────────┘
                               ▼
                    ┌──────────┴──────────┐
                    │ L2+ ?               │
                    ├────YES──────────────┤
                    │  Pause for approval │
                    │  ↓ approved?        │
                    │  NO → escalate/stop │
                    │  YES → continue ↓   │
                    ├────NO───────────────┤
                    │  Continue ↓         │
                    └──────────┬──────────┘
                               ▼
                     ┌─────────────────────┐
                     │  3. Design smallest │
                     │     useful action   │
                     └─────────┬───────────┘
                               ▼
                     ┌─────────────────────┐
                     │  4. Execute         │
                     └─────────┬───────────┘
                               ▼
                     ┌─────────────────────┐
                     │  5. Verify receipt  │
                     └─────────┬───────────┘
                               ▼
                    ┌──────────┴──────────┐
                    │ Receipt matches?    │
                    ├────YES──────────────┤
                    │  Update ledger      │
                    │  Checkpoint if due  │
                    │  ↓ target reached?  │
                    │  YES → close (§10)  │
                    │  NO  → loop to §2   │
                    ├────NO───────────────┤
                    │  Stop chain         │
                    │  Diagnose drift (§7)│
                    │  Recover or escalate│
                    └─────────────────────┘
```

## 1. Map The World

Translate the user request into a concrete target state before acting.

Capture:

- objective: what must be true when the task is finished
- systems: which files, apps, services, devices, or accounts are involved
- source of truth: where each fact should be verified
- access path: which tool or interface can observe or change that system
- invariants: data that must not change, downtime limits, privacy rules, cost limits, deadlines
- blockers: missing auth, missing permissions, unsupported platforms, or unclear ownership

Prefer direct sources of truth over summaries:

- use the shell for local files, processes, and installed tools
- use the browser for UI state and flows
- use the authoritative API for service state when available
- use official docs for current vendor behavior
- use screenshots, logs, IDs, timestamps, and responses instead of memory

If a fact could have changed recently, verify it before building on it.

## 2. Grade Risk

Classify the next action before you take it.

`L0` Observe only
- Read, inspect, list, search, trace, or gather state.

`L1` Local and reversible
- Edit a local file, restart a local process, install a package in an isolated environment, or create a reversible config change.

`L2` External or user-visible
- Send a message, modify a remote service, change production settings, alter a live account, or trigger user-facing behavior.

`L3` Destructive, financial, security-sensitive, or hard to undo
- Delete data, rotate credentials, expose a network surface, spend money, affect billing, revoke access, or perform an irreversible migration.

Default behavior:

- Execute `L0` and `L1` when they clearly serve the request.
- Pause and confirm before `L2` or `L3` unless the user already gave explicit approval for that exact class of action.
- Reduce risk first when possible by observing, dry-running, scoping, or creating a rollback path.

## 3. Design The Smallest Useful Action

Choose the smallest mutation that increases certainty or moves the system toward the target state.

For each step, define:

- precondition: what must already be true
- action: one bounded change
- receipt: what evidence will prove it worked
- rollback: how to undo or contain the change if needed

Prefer short action chains:

- one system at a time
- one mutation at a time
- one verification immediately after each mutation

Avoid broad, opaque batches when a smaller step can be verified independently.

### Idempotency

Prefer idempotent mutations (create-if-not-exists, upsert, PUT over POST).

When an action is not naturally idempotent:

- check for prior success before retrying
- use unique request or operation IDs when the target system supports them
- document why a non-idempotent path was chosen

### Parallel Execution

When multiple actions target independent systems with no shared state:

- group them by system boundary
- execute groups in parallel
- verify each group independently before merging results into the ledger
- if any group fails, halt all groups and recover from the verified state

Only use parallelism for L0 and L1 actions. L2+ actions must remain sequential.

## 4. Keep A Working Ledger

Maintain a compact internal ledger while working. Surface it to the user when it helps clarity.

Use this shape:

```text
Objective:
Systems:
Current state:
Next action:
Expected receipt:
Risk level:
Rollback:
Deadline:
Timeout:
Estimated cost:
Cumulative spend:
Budget:
```

Update the ledger after every meaningful observation or mutation.

If the environment diverges from the plan, rewrite the ledger before continuing.

If cumulative spend would exceed budget, escalate before proceeding.

### Audit Trail (High-Stakes Tasks)

For L2+ tasks, maintain an append-only log alongside the ledger:

```text
| # | Timestamp | Action | Risk | Receipt | Status |
|---|-----------|--------|------|---------|--------|
| 1 | ...       | ...    | L2   | ...     | ✅/❌   |
```

This log must never be edited after the fact — only appended to. Attach it to the final response when the task involves external systems.

Redact secrets from audit trail entries before writing them. Log the receipt shape and confirmation, not raw credentials. See §5 "Redacting Secrets From Receipts."

### Checkpointing

After every 3 verified mutations (or after any L2+ mutation):

- snapshot the current verified state as a named checkpoint
- record how to return to this checkpoint
- prune rollback plans older than the last checkpoint

## 5. Execute With Receipts

Before each mutation, state the intent briefly in plain language.

Set an explicit timeout for each external call. If the timeout fires:

1. capture whatever partial output exists
2. treat the action as failed (do not assume success)
3. enter drift recovery (§7)

Then:

1. perform one bounded action
2. capture the result immediately
3. compare the result against the expected receipt
4. stop if the receipt is missing, ambiguous, or contradictory

Good receipts include:

- command output that names the changed object
- file diffs or exact file contents
- HTTP status codes and response fields
- screenshots of the resulting UI state
- message IDs, deployment IDs, build IDs, or job IDs
- timestamps, versions, model names, or process IDs
- a second read from the system of record after the write

Do not treat a green exit code as sufficient proof when stronger evidence is available.

### Redacting Secrets From Receipts

Receipts often contain sensitive material. Before logging, checkpointing, or surfacing a receipt:

1. identify secrets: API keys, tokens, webhook URLs, signed URLs, passwords, cookies, session IDs, PII
2. replace the secret portion with a masked placeholder: `https://hooks.slack.com/services/T▒▒/B▒▒/▒▒▒▒`
3. keep enough structure to confirm the receipt is valid (protocol, domain, response shape) without exposing the credential
4. never log a raw secret in the audit trail, ledger, checkpoint, or final response
5. if a receipt is *only* a secret (e.g., a generated API key), log its presence and length, not its value: `API key generated (40 chars, starts with sk-)`

This rule applies equally to:

- text shown to the user in chat
- audit trail rows
- checkpoint descriptions
- ledger fields
- handoff summaries
- sub-agent delegation prompts (do not pass raw secrets unless strictly required by the action)

## 6. Resolve Conflicting Signals

When sources disagree, trust the nearest system of record.

Use this order:

1. direct state from the target system
2. a fresh read through the official API or UI
3. local cache or derived logs
4. prior assumptions or model memory

If the conflict remains:

- capture both signals
- name the exact contradiction
- avoid further writes until the contradiction is resolved

## 7. Recover From Drift

Assume the world can change mid-task.

Drift can come from:

- stale assumptions
- partial writes
- human changes made in parallel
- retries that already succeeded once
- expired auth or missing capabilities
- network or environment changes

When drift appears:

1. stop the current chain
2. restate the actual state using exact names, IDs, and dates
3. decide whether to refresh, retry, rollback, or escalate
4. continue only from the new verified state

Never keep replaying the same write blindly against a drifting system.

## 8. Approval And Safety Rules

Escalate gently when consequences are non-obvious.

Pause and confirm when a step could:

- expose a service beyond the local machine
- spend money or allocate paid resources
- change security posture or credentials
- message third parties or modify external accounts
- delete data or overwrite user work
- create hidden long-term maintenance burden

When asking for confirmation, present:

- the exact action
- why it is needed
- the main tradeoff or risk
- the safer fallback if one exists

### Async Handoffs

When a step requires human action outside the agent's tools:

1. state exactly what the human needs to do
2. state the expected receipt (e.g., "reply with the deployment URL")
3. pause execution — do not guess or simulate the result
4. on resume, verify the human-provided receipt against the system of record

## 9. Delegation

Delegation to sub-agents is optional. Only use this section when:

- sub-agents are available in the current environment (e.g., browser subagent)
- the user has explicitly authorized delegation or parallel agent work

If sub-agents are not available or not authorized, perform the step locally using the tools you have. Skip this section entirely for single-agent execution.

When delegation is appropriate:

- state the exact success criteria in the delegation prompt
- require the sub-agent to return specific receipts (screenshot, status code, etc.)
- redact secrets from the delegation prompt unless the sub-agent strictly needs them to act
- verify the sub-agent's receipts against the system of record yourself
- do not trust a sub-agent's summary without independent verification

### Chaining Multiple Sub-Agents

Only when multiple sub-agents are available and authorized, and when a task requires them (e.g., browser + terminal + API):

1. assign each sub-agent a single, bounded responsibility
2. define explicit data handoff points between agents (e.g., "terminal agent returns the deployment URL, browser agent verifies it")
3. never let one sub-agent depend on another sub-agent's unverified output
4. if two sub-agents return conflicting results, halt both and resolve at the operator level

### Sub-Agent Failure

When a sub-agent fails or returns ambiguous results:

- retry with a more specific prompt (narrower scope, explicit receipt format)
- if the retry fails, attempt the action directly without delegation
- log the failure in the audit trail with the sub-agent's redacted output (mask any secrets per §5 before logging)

## 10. Completion Bar

Declare success only when the target state is verified.

A task is done when one of these is true:

- the desired end state is proven with receipts
- the user intentionally accepted a partial outcome
- a concrete blocker is proven and the missing requirement is named

A task is not done when:

- the steps merely sound correct
- the plan is written but not executed
- a tool ran without proof of outcome
- the first half succeeded but downstream state is unknown

## 11. Final Response Contract

Close with a short operator-style summary:

- what changed
- what evidence proved it
- what remains risky, partial, or blocked
- what the next safe action is

Keep the summary grounded in observed state, not inference.

## 12. Context Management

Long operator chains can overflow available context. Manage this actively.

### Ledger Compression

After reaching a checkpoint, compress the ledger:

1. replace completed steps with a one-line summary and their checkpoint ID
2. keep only the current state, next action, and active rollback plan in full detail
3. preserve the audit trail — it is append-only and must not be compressed

### What To Keep vs. Drop

| Keep in context | Safe to drop |
|---|---|
| Current ledger state | Raw command output from verified steps |
| Active rollback plan | Full output of passing L0 checks |
| Audit trail | Intermediate file contents already checkpointed |
| Unresolved conflicts | Sub-agent prompts that succeeded |
| Last checkpoint | Rolled-back plans from before last checkpoint |

### Long Task Handoff

When context is running low mid-task:

1. write a handoff summary: objective, current state, last checkpoint, remaining steps
2. include the audit trail
3. the next context can resume from the checkpoint without replaying history

## 13. Metrics And Telemetry

Track operator performance across tasks to identify patterns.

After each completed task, record:

```text
| Date | Task | Steps | Retries | Drift Events | L2+ Actions | Duration | Outcome |
|------|------|-------|---------|--------------|-------------|----------|---------|
```

Use these metrics to:

- spot systems that frequently drift (may need better invariant checks)
- identify action types with high retry rates (may need idempotency improvements)
- track L2+ action frequency (indicates risk exposure over time)
- measure average steps-to-completion (reveals over-engineering or under-planning)

A template is available in `templates/templates.md`.

## 14. Anti-Patterns

Avoid these common mistakes:

| Anti-Pattern | Why It Fails | What To Do Instead |
|---|---|---|
| **Narrating instead of executing** | "I would run…" doesn't change state | Run the command, capture the receipt |
| **Exit-code-only verification** | Exit 0 doesn't prove correctness | Read back from the system of record |
| **Batching everything** | One failure hides in a batch of 10 | One mutation → one verification |
| **Trusting sub-agent summaries** | Sub-agents can hallucinate receipts | Independently verify every claim |
| **Skipping rollback planning** | "I'll figure it out if it breaks" | Define rollback before you act |
| **Stale ledger** | Acting on old state causes drift | Re-verify after any pause or interruption |
| **Over-confirming L0 actions** | Asking permission to `ls` wastes time | Observe freely, confirm before mutating |
| **Retrying without checking** | Re-POST can duplicate resources | Check for prior success first (idempotency) |
| **Ignoring partial success** | "First half worked so it's fine" | Verify downstream state, not just the step |
| **Cost blindness** | Deploying 10 GPU instances "to test" | Track spend, set budgets, escalate early |

## 15. Edge Cases

Guidance for situations the main loop doesn't fully cover.

### Cascading Rollbacks

When a failure requires rolling back multiple steps:

1. identify the last verified checkpoint
2. roll back in reverse order from the current step to that checkpoint
3. verify each rollback independently — a failed rollback is itself a drift event
4. if any rollback fails, stop and escalate with the exact stuck state

### Partial System Failures

When some systems succeed and others fail in a multi-system task:

1. do not roll back the successful systems automatically
2. assess whether the partial state is safe to leave in place
3. if unsafe, roll back the successful changes too (cascading rollback)
4. if safe, document the partial state and proceed with fixing the failed system

### Authentication Expiry Mid-Task

When auth tokens expire during execution:

1. treat all subsequent actions as untrusted — do not assume they failed or succeeded
2. refresh credentials
3. re-verify the last action's outcome before continuing
4. do not retry the last action without checking if it already succeeded

### Rate Limits and Throttling

When an API returns 429 or equivalent:

1. record the rate limit response in the audit trail
2. wait the duration specified in the `Retry-After` header (or a safe default)
3. retry exactly once
4. if still throttled, escalate — do not enter a retry loop

### Concurrent Human Changes

When a human modifies the target system while the operator is working:

1. detect via state mismatch at the next verification step
2. halt the chain — do not overwrite the human's changes
3. present both states (expected vs. actual) and ask the user how to proceed
4. never silently merge or overwrite

### Ambiguous Success

When a receipt is technically present but doesn't clearly confirm success:

- example: API returns 200 but the response body says `"status": "pending"`
- do not treat this as verified success
- poll or re-check until the state is definitively confirmed or a timeout fires

---

# Advanced: Superhuman Operations (§16–§21)

The sections below handle tasks too complex for any single human to manage — massive state spaces, multi-phase orchestration, and probabilistic reasoning. Use these when:

- the task involves 5+ interdependent systems
- execution spans multiple phases or long time windows
- failure in one system can cascade to others
- operations have time-dependent verification (DNS, caches, eventual consistency)

For simpler tasks, §1–§15 is sufficient.

## 16. Dependency Graph Reasoning

Before executing a complex task, model the systems as a directed acyclic graph (DAG).

### Building The Graph

For each system involved, identify:

- what it depends on (prerequisites)
- what depends on it (downstream consumers)
- whether the dependency is hard (blocks execution) or soft (degrades gracefully)

```text
Example:
  database ──→ api-server ──→ frontend
      │                          │
      └──→ cache-layer ──────────┘
            (soft dep)
```

### Using The Graph

1. **Identify the critical path** — the longest chain of hard dependencies. This determines minimum execution time.
2. **Find parallel branches** — independent sub-graphs can execute concurrently (subject to §3 parallel execution rules).
3. **Detect cycles** — if A depends on B and B depends on A, halt and redesign. Do not attempt circular execution.
4. **Re-evaluate after mutations** — a mutation can change the graph (e.g., creating a new service adds a new node). Update the graph before continuing.

### Graph In The Ledger

Add to the ledger:

```text
Dependency graph:
  [system-a] ──hard──→ [system-b] ──hard──→ [system-c]
  [system-a] ──soft──→ [system-d]
Critical path: system-a → system-b → system-c (3 steps)
Parallel branches: system-d (independent after system-a)
```

## 17. Confidence-Scored Verification

Replace binary pass/fail with confidence scores for complex tasks.

### Scoring Receipts

| Score | Meaning | Action |
|-------|---------|--------|
| 1.0 | Direct confirmation from system of record | Proceed |
| 0.9 | Strong indirect evidence (e.g., HTTP 200 + correct body) | Proceed |
| 0.7–0.9 | Partial confirmation (e.g., 200 but body unchecked) | Add secondary verification |
| 0.5–0.7 | Ambiguous (e.g., "status: pending") | Re-poll with timeout |
| < 0.5 | Contradictory or missing evidence | Halt, diagnose |

### Chain Confidence

Track cumulative confidence across the execution chain:

```text
Step 1: 0.95 → chain: 0.95
Step 2: 0.90 → chain: 0.95 × 0.90 = 0.855
Step 3: 0.85 → chain: 0.855 × 0.85 = 0.727
```

- If chain confidence drops below **0.7**, pause and re-verify from the last checkpoint.
- If any single step scores below **0.5**, halt immediately.

### Scoring In The Audit Trail

Extend the audit trail:

```text
| # | Timestamp | Action | Risk | Receipt | Confidence | Status |
|---|-----------|--------|------|---------|------------|--------|
| 1 | ...       | ...    | L1   | ...     | 0.95       | ✅      |
```

## 18. Invariant Monitoring

Define system invariants at task start. Check them proactively, not just on failure.

### Defining Invariants

```text
Hard invariants (must NEVER break):
- database is accessible and accepting writes
- production traffic is being served (HTTP 200 on health endpoint)
- disk usage < 90% on all nodes

Soft invariants (acceptable temporarily, must restore):
- cache hit rate > 80%
- response latency < 500ms p95
```

### Monitoring Schedule

- **After every L2+ mutation:** check all hard invariants
- **At every checkpoint:** check all invariants (hard and soft)
- **After any drift recovery:** check all invariants before resuming

### Invariant Breach Protocol

Hard invariant breach:

1. halt all execution immediately — this is priority zero
2. assess blast radius — what downstream systems are affected?
3. roll back to last checkpoint where the invariant held
4. escalate to user with exact state

Soft invariant breach:

1. log in audit trail with timestamp
2. continue if the breach is expected and temporary (document why)
3. schedule re-check after the expected recovery window
4. escalate if the soft invariant hasn't recovered by the next checkpoint

## 19. Failure Mode Taxonomy

Classify every failure precisely. Each type has a different recovery playbook.

| Failure Mode | Definition | Recovery | Example |
|---|---|---|---|
| **Transient** | Temporary, likely self-resolving | Wait (with backoff), retry once | Network timeout, 503 |
| **Permanent** | The action cannot succeed as designed | Escalate, redesign the step | Permission denied, resource doesn't exist |
| **Cascading** | Failure in system A causes failure in B, C, D… | Emergency rollback to last checkpoint, check all invariants | DB down → API down → frontend down |
| **Silent** | No error, but the action didn't actually take effect | Add deeper verification probes | Write acknowledged but not replicated |
| **Delayed** | Action will eventually fail, but not immediately | Schedule re-verification after expected delay | Certificate provisioning, async job still queued |

### Using The Taxonomy

1. On failure, classify it before choosing recovery.
2. Do not apply a transient-failure recovery (retry) to a permanent failure (permission denied).
3. For cascading failures, trace the dependency graph to the root cause system.
4. For silent failures, design a deeper probe: read back from a replica, check downstream effects, verify the mutation is visible from a different access path.
5. For delayed failures, set a timer and return to verify later — do not block on it.

## 20. Multi-Phase Orchestration

Break superhuman-complexity tasks into named phases.

### Phase Structure

```text
Phase 1: Preparation
  Entry criteria: all systems accessible, backups verified
  Actions: create migration scripts, validate schema, test in dev
  Exit criteria: all dev tests pass, migration script verified
  Checkpoint: cp-phase-1

Phase 2: Staging Deployment
  Entry criteria: Phase 1 exit criteria met
  Actions: deploy to staging, run integration tests
  Exit criteria: staging mirrors expected state, tests pass
  Checkpoint: cp-phase-2

Phase 3: Production Deployment
  Entry criteria: Phase 2 exit criteria met + user approval (L3)
  Actions: deploy to production, verify, monitor
  Exit criteria: production healthy, invariants holding
  Checkpoint: cp-phase-3
```

### Phase Rules

1. **Isolation:** each phase has its own ledger, audit trail, and checkpoint. Compress previous phases per §12.
2. **Gate transitions:** never start Phase N+1 until all exit criteria for Phase N are verified with receipts.
3. **Phase-level rollback:** if Phase N fails catastrophically, roll back the entire phase, not individual steps. Return to Phase N-1's checkpoint.
4. **Resumption:** after context loss (timeout, crash, new session), resume from the last verified phase checkpoint. Re-verify phase exit criteria before continuing.
5. **Partial phase success:** if some exit criteria pass and others fail, do not advance. Fix or roll back within the phase.

### Phase Ledger Extension

Add to the main ledger:

```text
Phase: [name]
Phase entry criteria: [met? YES/NO with receipts]
Phase exit criteria: [list]
Phase checkpoint: cp-phase-N
Previous phases: [compressed summaries]
```

## 21. Temporal Reasoning

Model time as a first-class concern in complex operations.

### Time-Dependent Operations

| Operation | Typical Propagation Window | Verification Strategy |
|---|---|---|
| DNS record changes | 30s–48h (TTL dependent) | Wait for TTL + buffer, verify from multiple resolvers |
| TLS certificate issuance | 30s–10min (ACME) | Poll status endpoint until `valid`, timeout at 15min |
| CDN cache invalidation | 5s–15min | Purge, wait, verify cache miss from edge |
| Database replication | ms–seconds (sync), seconds–minutes (async) | Read from replica, compare with primary |
| Container deployment | 10s–5min (depends on image size, health checks) | Poll health endpoint, verify new version string |
| Async job completion | seconds–hours | Poll job status, set hard timeout |

### Temporal Rules

1. **Never verify before the propagation window.** If DNS TTL is 300s, waiting 10s and checking is useless.
2. **Schedule re-verification.** After starting a time-dependent operation, note the expected completion time in the ledger and return to verify at that time.
3. **Handle clock skew.** Always use UTC timestamps. Do not compare timestamps across systems without accounting for potential clock drift.
4. **Set hard timeouts.** Every time-dependent wait must have a maximum: if the operation hasn't completed by the timeout, classify as a delayed failure (§19) and escalate.
5. **Don't block on async when you can parallelize.** If Operation A takes 5 minutes to propagate and Operation B is independent, start B while waiting for A. Rejoin when both are verifiable.

### Temporal Ledger Extension

Add to the ledger:

```text
Active timers:
  - DNS propagation for app.example.com: expected at 01:35 UTC, timeout at 01:50 UTC
  - TLS cert issuance: expected at 01:32 UTC, timeout at 01:45 UTC
Next scheduled verification: 01:35 UTC (DNS)
```

---

## Resources

- **Templates:** `templates/templates.md` — ledger, audit trail, checkpoint, delegation, summary, metrics, dependency graph, phase plan, invariant checklist, and confidence-scored log templates
- **Examples:**
  - `examples/deploy-static-site.md` — simple deployment with verification
  - `examples/api-integration.md` — multi-service API wiring
  - `examples/multi-service-coordination.md` — Docker + Nginx + DNS with drift recovery
  - `examples/device-control.md` — ADB device interaction with backup and rollback
  - `examples/multi-phase-orchestration.md` — zero-downtime DB migration across 3 environments (advanced)

## Trigger Examples

Use this skill for requests like:

- "Connect these services and prove the bot actually works."
- "Install this on a VPS, expose it safely, and verify the route."
- "Control my phone through the bridge and confirm the foreground app changed."
- "Update production config, but stop if the health check fails."
- "Coordinate browser, terminal, and API changes without losing track of state."
- "Deploy this across three environments and verify each one."

Advanced (§16–§21) triggers:

- "Migrate the database across dev, staging, and prod with zero downtime."
- "Set up the entire infrastructure stack — 8 services, all wired together, all verified."
- "Deploy, wait for DNS, provision the cert, then verify the full chain end-to-end."
- "Coordinate a rollout where any failure in one service means rolling back all of them."
- "Run this multi-hour deployment and pick up where you left off if context resets."

## When NOT To Use This Skill

- Pure Q&A or explanation with no system interaction
- Single-file code edits that don't depend on external state
- Creative writing, brainstorming, or hypothetical scenarios
- Tasks where the user explicitly says "just tell me, don't do it"
- Research-only requests where no mutation or verification is needed

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-22 | Initial skill: operating loop, risk grading, receipts, drift recovery, approvals, completion bar |
| 2.0 | 2026-03-22 | Added: parallel execution, timeouts, idempotency, audit trails, delegation, cost tracking, checkpointing, async handoffs, context management, metrics |
| 3.0 | 2026-03-22 | Added: quick start card, decision flowchart, anti-patterns table, edge case guidance, changelog, templates directory, 4 worked examples |
| 3.1 | 2026-03-22 | Security: secret redaction rules, delegation gated behind explicit authorization, examples sanitized |
| 4.0 | 2026-03-22 | Superhuman upgrade: §16 dependency graph reasoning, §17 confidence-scored verification, §18 invariant monitoring, §19 failure mode taxonomy, §20 multi-phase orchestration, §21 temporal reasoning. New example: multi-phase DB migration. Advanced templates added. Complex Mode quick-start extension |
