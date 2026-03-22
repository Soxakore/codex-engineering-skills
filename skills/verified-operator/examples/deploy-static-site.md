# Example: Deploy a Static Site to Vercel

This walkthrough demonstrates the Verified Operator loop on a real task.

---

## Ledger

```text
Objective: Deploy ./site to Vercel and verify it's live
Systems: local filesystem, Vercel API, browser
Current state: ./site exists, Vercel CLI installed, not yet deployed
Next action: verify local files exist
Expected receipt: ls output showing index.html
Risk level: L0
Rollback: n/a
Deadline: none
Timeout: 10s per command
Estimated cost: $0 (free tier)
Cumulative spend: $0
Budget: $0
```

---

## Execution

### Step 1 — Verify source exists (L0)

**Intent:** Confirm the site directory has an index.html before deploying.

```bash
ls -la ./site/index.html
```

**Receipt:** File listed, 2.4 KB, last modified today. ✅

---

### Step 2 — Deploy to Vercel (L2 — confirmed by user)

**Intent:** Push the site to production on Vercel's free tier.

```bash
vercel --prod ./site
```

**Receipt:** Deployment URL `https://site-xyz.vercel.app` returned. ✅

**Checkpoint:** `cp-1` — site deployed, URL known, can rollback with `vercel rm <id>`.

---

### Step 3 — Verify live site (L0)

**Intent:** Confirm the deployment is actually serving the correct content.

```bash
curl -s -o /dev/null -w "%{http_code}" https://site-xyz.vercel.app
# → 200

curl -s https://site-xyz.vercel.app | grep "<title>"
# → <title>My Site</title>
```

**Receipt:** HTTP 200, correct title tag. ✅

---

### Audit Trail

| # | Timestamp        | Action              | Risk | Receipt                     | Status |
|---|------------------|----------------------|------|-----------------------------|--------|
| 1 | 2026-03-22 01:00 | ls ./site/index.html | L0   | file exists, 2.4 KB        | ✅      |
| 2 | 2026-03-22 01:01 | vercel --prod        | L2   | URL returned                | ✅      |
| 3 | 2026-03-22 01:02 | curl site URL        | L0   | HTTP 200, correct `<title>` | ✅      |

---

## Final Summary

- **Changed:** Deployed `./site` to Vercel at `https://site-xyz.vercel.app`
- **Evidence:** HTTP 200, correct `<title>` tag in response body
- **Remaining:** None
- **Next safe action:** Share URL with user
