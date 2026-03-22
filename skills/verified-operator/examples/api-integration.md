# Example: Wire a Slack Webhook to a Monitoring Service

Demonstrates receipt-driven API integration across two external services.

> **Note on secrets:** All credentials and webhook URLs in this example use masked
> placeholders (`▒▒▒▒`) to demonstrate the redaction rule from §5 of SKILL.md.
> In real use, capture enough structure to confirm validity without exposing secrets.

---

## Ledger

```text
Objective:      POST alerts from UptimeRobot to a Slack channel
Systems:        UptimeRobot API, Slack Incoming Webhooks, terminal (curl)
Current state:  UptimeRobot monitor exists, Slack workspace accessible, no webhook configured
Next action:    L0 — read current UptimeRobot alert contacts
Expected receipt: JSON list of existing alert contacts
Risk level:     L0
Rollback:       n/a
Deadline:       none
Timeout:        15s per API call
Estimated cost: $0
Cumulative spend: $0
Budget:         $0
```

---

## Execution

### Step 1 — List existing alert contacts (L0)

**Intent:** See what alert contacts already exist so we don't create a duplicate.

```bash
curl -s -X POST "https://api.uptimerobot.com/v2/getAlertContacts" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"▒▒▒▒▒▒▒▒"}' | jq '.alert_contacts'
```

**Receipt:** JSON returned, 2 existing email contacts, no Slack webhook. ✅

---

### Step 2 — Create Slack Incoming Webhook (L2 — user confirmed)

**Intent:** Create a webhook URL in Slack to receive alert messages.

```
Slack App → Incoming Webhooks → Add New Webhook → #ops-alerts channel
```

**Receipt:** Webhook URL returned: `https://hooks.slack.com/services/T▒▒/B▒▒/▒▒▒▒` (masked). ✅

---

### Step 3 — Test the webhook directly (L2)

**Intent:** Verify Slack actually receives messages at this URL before wiring it up.

```bash
curl -s -X POST "$SLACK_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"text":"✅ Webhook test from verified-operator"}' \
  -w "\nHTTP %{http_code}"
```

**Receipt:** HTTP 200, message appeared in #ops-alerts. ✅ (screenshot captured)

**Checkpoint:** `cp-1` — Slack webhook works, not yet wired to UptimeRobot.

---

### Step 4 — Add webhook as UptimeRobot alert contact (L2)

**Intent:** Register the Slack URL as a new alert contact in UptimeRobot.

```bash
curl -s -X POST "https://api.uptimerobot.com/v2/newAlertContact" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key":"▒▒▒▒▒▒▒▒",
    "type":11,
    "friendly_name":"Slack #ops-alerts",
    "value":"'"$SLACK_WEBHOOK_URL"'"
  }' | jq '.alertcontact'
```

**Receipt:** `"id": "12345"`, `"status": 2` (active). ✅

---

### Step 5 — Verify round-trip with a test alert (L1)

**Intent:** Trigger a test notification through UptimeRobot to confirm the full chain.

```bash
curl -s -X POST "https://api.uptimerobot.com/v2/getAlertContacts" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"▒▒▒▒▒▒▒▒","alert_contacts":"12345"}' | jq '.alert_contacts[0]'
```

**Receipt:** Contact exists, status active. Triggered test → message arrived in Slack. ✅

---

### Audit Trail

| # | Timestamp        | Action                          | Risk | Receipt                              | Status |
|---|------------------|---------------------------------|------|--------------------------------------|--------|
| 1 | 2026-03-22 01:00 | List alert contacts             | L0   | 2 emails, no webhook                 | ✅      |
| 2 | 2026-03-22 01:02 | Create Slack webhook            | L2   | Webhook URL returned (masked)        | ✅      |
| 3 | 2026-03-22 01:03 | Test webhook directly           | L2   | HTTP 200, message in channel         | ✅      |
| 4 | 2026-03-22 01:04 | Add contact to UptimeRobot      | L2   | Contact ID 12345, active             | ✅      |
| 5 | 2026-03-22 01:05 | Verify round-trip test alert    | L1   | Message in Slack channel             | ✅      |

---

## Final Summary

- **Changed:** Created Slack webhook in #ops-alerts, registered as UptimeRobot alert contact ID 12345
- **Evidence:** Test alert flowed from UptimeRobot → Slack, message visible in channel
- **Remaining:** Only "down" alerts are configured; "up" recovery alerts need a separate contact if desired
- **Next safe action:** Attach alert contact 12345 to specific monitors
