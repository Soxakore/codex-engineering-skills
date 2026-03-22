# Example: Add A Small Feature Without Widening Scope

Request:

> Add a "Copy link" button to the share modal.

Good `repo-pilot` path:

1. Find the owning modal component and the nearest existing button patterns.
2. Reuse the repo's current button, toast, and clipboard helpers if they already exist.
3. Avoid introducing a new modal state system or notification layer for a one-button change.
4. Verify with the cheapest useful proof:
   component test if present, otherwise a narrow browser or render proof.
5. Inspect the final diff for accidental style churn or refactors to unrelated modal code.

Good handoff:

```text
- Changed: Added a copy-link action to the existing share modal using the repo's current button and toast patterns.
- Proof: Share modal interaction test passes and the copied URL matches the current page link.
- Risks: Full cross-browser validation not run.
- Not run: End-to-end suite.
```
