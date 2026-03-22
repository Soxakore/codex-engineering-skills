---
name: repo-pilot
description: Map unfamiliar repositories quickly, choose the smallest safe implementation path, and land verified code changes with minimal diff. Use when Codex is asked to fix bugs, add small or medium features, refactor existing code, trace behavior through an unknown codebase, or prepare review-ready changes in an existing repo while preserving local patterns and minimizing regression risk.
---

# Repo Pilot

Enter an existing codebase, build only the context you need, and ship the safest useful change.

Use this skill to avoid two common failures:

- editing before understanding repo ownership and verification paths
- widening a small request into a sprawling refactor

## Core Loop

1. map the repo shape before editing
2. write a compact change brief
3. choose the smallest viable change surface
4. implement in narrow slices
5. verify from cheapest to strongest
6. hand off with proof, not guesses

## 1. Map The Repo Before Editing

Inspect the repo first. Build a compact mental model before touching files.

Capture:

- project type and stack
- package manager and workspace layout
- likely entrypoints for the requested behavior
- nearest tests, lint, typecheck, or build commands
- dirty-worktree context and any user-owned changes
- risk surfaces such as config, migrations, auth, shared utilities, and public interfaces
- local patterns worth preserving

Prefer reading outward from the likely ownership point:

1. the file named in the request, failing test, stack trace, or visible UI path
2. its imports, callers, nearby tests, and configuration
3. broader framework entrypoints only if the local picture is still unclear

Do not start refactoring just because nearby code is messy.

If you need quick stack or command inference, read `references/repo-signals.md`.

## 2. Write A Change Brief

Before editing, state the smallest credible plan.

Capture:

- requested outcome
- current behavior and how it differs
- likely files or modules to touch
- safest verification path
- rollback or fallback if the first path fails

Keep the brief short. The point is to reduce drift, not create paperwork.

Use the templates in `references/templates.md` when useful.

## 3. Prefer The Minimum-Diff Path

Default to the change that:

- touches the fewest files
- preserves existing abstractions
- follows the repo's current style and framework patterns
- avoids changing public interfaces unless required
- keeps verification local and cheap

Prefer:

- extending an existing module over introducing a new layer
- reusing a nearby helper over creating a cross-cutting abstraction
- fixing the caller or boundary where the bug appears over rewriting the whole flow

Escalate only when the small path would clearly produce worse behavior, duplicate logic in a risky way, or fight the repo's architecture.

## 4. Implement In Narrow Slices

Work one concern at a time.

Good slice boundaries:

- data shape or parsing
- business logic branch
- UI state or rendering path
- wiring or integration boundary
- test coverage for the changed behavior

Before each edit cluster:

- reread the immediate surrounding code
- check for existing helper functions or conventions
- confirm you are editing the owning layer, not a symptom far downstream

When the path is still unclear:

- add temporary instrumentation only if it materially improves certainty
- prefer targeted tracing, logging, or search over speculative edits

Remove temporary debugging artifacts before finishing.

## 5. Verify From Cheapest To Strongest

Do not jump straight to the heaviest command.

Use this ladder:

1. static or file-local proof
2. targeted test nearest the change
3. narrow integration or smoke proof
4. broader suite only if the risk justifies it

Examples:

- lint or typecheck a touched package before a full workspace pass
- run one test file before the whole suite
- open one route or one CLI command before an end-to-end matrix

If no verification exists, add the smallest meaningful test when reasonable.

If you cannot run verification:

- say exactly what blocked it
- name the unverified behavior
- name the residual risk plainly

Use evidence such as diffs, test output, rendered UI state, logs, or API responses.

## 6. Handle Unknown Or Messy Repos Carefully

When the repo is unfamiliar or inconsistent:

- anchor to the nearest working pattern instead of inventing a new one
- avoid "cleanups" unrelated to the requested change
- isolate framework or tooling uncertainty before editing core logic
- treat monorepos as multiple systems until proven otherwise
- preserve unrelated local changes in a dirty worktree

If you cannot explain how execution reaches the behavior in question, stop and trace it before editing.

If two plausible implementation paths remain after inspection, choose the one with:

1. fewer touched files
2. fewer callsites
3. a clearer verification route
4. lower chance of widening future maintenance burden

## 7. Review Before Handoff

Before declaring success:

- inspect the final diff for accidental churn
- check for debug leftovers, naming drift, and formatting noise
- confirm the requested behavior changed and nearby behavior did not regress
- mention any tests or checks that were not run

End with:

- what changed
- what proved it
- what remains risky, partial, or unverified

Use `references/templates.md` for a compact handoff shape.

## Common Traps

Avoid:

- editing before mapping entrypoints and ownership
- widening a bug fix into an architecture project
- introducing new abstractions because they feel cleaner
- running the full suite before cheap local proof
- touching unrelated files in a dirty repo
- claiming success from exit codes alone when stronger proof exists

## Resources

- `references/repo-signals.md`
  Use for fast stack detection, monorepo signals, and verification-command selection.
- `references/templates.md`
  Use for repo-map, change-brief, verification, and final-handoff templates.
- `examples/fix-service-bug.md`
  Example bug fix in an unfamiliar backend service.
- `examples/add-small-feature.md`
  Example feature addition with a minimum-diff path.
- `examples/trace-unknown-ui-regression.md`
  Example of tracing an unfamiliar UI flow before editing.
