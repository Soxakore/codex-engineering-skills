# Ledger Template

Copy and fill this template at the start of every verified-operator task.

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

# Audit Trail Template

Append a row after every mutation. Never edit past rows. Redact secrets before writing (see §5).

```text
| # | Timestamp | Action | Risk | Receipt | Status |
|---|-----------|--------|------|---------|--------|
|   |           |        |      |         |        |
```

# Checkpoint Template

Create after every 3 mutations or after any L2+ mutation.

```text
Checkpoint: cp-N
State: <describe the verified state>
Rollback: <how to return here>
```

# Delegation Prompt Template

Use only when sub-agents are available and authorized. Otherwise, perform the step locally. Redact secrets unless the sub-agent strictly needs them.

```text
Task: <exact action>
Success criteria: <what must be true when done>
Required receipts: <screenshot | status code | file diff | etc.>
Timeout: <max duration>
On failure: <stop | retry once | escalate>
```

# Final Summary Template

```text
- Changed: <what changed>
- Evidence: <what proved it>
- Remaining: <what's risky, partial, or blocked>
- Next safe action: <what to do next>
```

# Metrics Row Template

Append to metrics log after each task for trend tracking.

```text
| Date | Task | Steps | Retries | Drift Events | L2+ Actions | Duration | Outcome |
|------|------|-------|---------|--------------|-------------|----------|---------|
|      |      |       |         |              |             |          |         |
```

---

# Advanced Templates (§16–§21)

# Dependency Graph Template

```text
Dependency graph:
  [system-a] ──hard──→ [system-b] ──hard──→ [system-c]
  [system-a] ──soft──→ [system-d]
Critical path: system-a → system-b → system-c
Parallel branches: system-d (independent after system-a)
Cycles detected: none
```

# Phase Plan Template

```text
Phase N: <name>
  Entry criteria:
    - <criterion 1> [MET/NOT MET]
    - <criterion 2> [MET/NOT MET]
  Actions:
    - <action 1>
    - <action 2>
  Exit criteria:
    - <criterion 1> [VERIFIED/PENDING]
    - <criterion 2> [VERIFIED/PENDING]
  Checkpoint: cp-phase-N
  Rollback: <how to return to Phase N-1>
```

# Invariant Checklist Template

```text
Hard invariants (must NEVER break):
  - [ ] <invariant 1> — verification command: <command>
  - [ ] <invariant 2> — verification command: <command>

Soft invariants (temporary breach acceptable):
  - [ ] <invariant 1> — threshold: <value> — recovery window: <duration>
  - [ ] <invariant 2> — threshold: <value> — recovery window: <duration>
```

# Confidence-Scored Audit Trail Template

```text
| # | Phase | Timestamp | Action | Risk | Receipt (redacted) | Confidence | Status |
|---|-------|-----------|--------|------|--------------------|------------|--------|
|   |       |           |        |      |                    |            |        |

Chain confidence: <running product>
Threshold: 0.7 (halt and re-verify if below)
```

# Temporal Timer Template

```text
Active timers:
  - <operation>: expected at <time> UTC, timeout at <time> UTC
  - <operation>: expected at <time> UTC, timeout at <time> UTC
Next scheduled verification: <time> UTC (<what to verify>)
```
