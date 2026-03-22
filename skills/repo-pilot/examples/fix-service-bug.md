# Example: Fix A Backend Bug In An Unfamiliar Repo

Request:

> Fix the API so `GET /profile` stops returning `null` for users who have a preferred name.

Good `repo-pilot` path:

1. Map the ownership path first.
   Start from the route handler, then inspect the serializer or mapper that shapes the profile response.
2. Write a tiny change brief.
   The likely fix is in the response shaping path, not auth or database setup.
3. Choose the minimum-diff edit.
   Prefer fixing the mapper or field selection over rewriting profile loading.
4. Verify cheaply.
   Run the nearest unit or integration test for the profile response before broader API tests.
5. Review the diff.
   Check for accidental changes to unrelated fields or fallback-name logic.

Good handoff:

```text
- Changed: Updated the profile response mapper to prefer `preferred_name` when present.
- Proof: Targeted profile response test now passes; response payload includes the expected name.
- Risks: Did not run the full API suite.
- Not run: Workspace-wide integration tests.
```
