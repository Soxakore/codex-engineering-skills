# Example: Trace A UI Regression Before Editing

Request:

> The settings page flashes and resets the toggle after save. Fix it.

Good `repo-pilot` path:

1. Do not patch the toggle immediately.
2. Trace the path:
   component state, save handler, cache invalidation, refetch behavior, and response shape.
3. Identify the owning layer.
   If the toggle resets after a successful refetch, the bug may be stale normalization or optimistic state, not the UI control itself.
4. Pick the narrowest fix.
   Prefer correcting stale state reconciliation over rewriting the settings page.
5. Verify with one focused path.
   Save once, confirm the toggle remains stable, then run the nearest test or smoke proof.

Good handoff:

```text
- Changed: Fixed stale settings reconciliation after save so the toggle reflects the post-save server state.
- Proof: Reproduced once before the fix, then verified the toggle remains enabled after save and refetch.
- Risks: Did not audit every settings field for the same stale-state pattern.
- Not run: Full frontend regression suite.
```
