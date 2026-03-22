# Example: Coordinate Docker, Nginx, and DNS for a New Service

Demonstrates multi-system coordination with checkpointing and drift recovery.

> **Note on secrets:** All credentials in this example use environment variables
> or masked placeholders (`▒▒▒▒`) to demonstrate the redaction rule from §5 of SKILL.md.

---

## Ledger

```text
Objective:      Deploy app container, configure reverse proxy, point DNS — verify end-to-end
Systems:        Docker (VPS), Nginx (VPS), Cloudflare DNS API, browser
Current state:  VPS accessible via SSH, Docker installed, Nginx running, domain on Cloudflare
Next action:    L0 — verify Docker and Nginx are running on the VPS
Expected receipt: `docker info` output + Nginx responding on port 80
Risk level:     L0
Rollback:       per-step (documented below)
Deadline:       none
Timeout:        20s per SSH command
Estimated cost: $0 (existing VPS)
Cumulative spend: $0
Budget:         $5
```

---

## Execution

### Step 1 — Verify infrastructure state (L0, parallel)

**Intent:** Confirm both Docker and Nginx are healthy before making changes.

```bash
# Group A: Docker
ssh vps "docker info --format '{{.ServerVersion}}'"
# → 24.0.7 ✅

# Group B: Nginx
ssh vps "systemctl is-active nginx && curl -s -o /dev/null -w '%{http_code}' http://localhost"
# → active, HTTP 200 ✅
```

**Receipt:** Both systems healthy, parallel L0 verified independently. ✅

---

### Step 2 — Pull and run the app container (L1)

**Intent:** Start the app container on an internal port.

```bash
ssh vps "docker run -d --name myapp --restart unless-stopped -p 127.0.0.1:3000:3000 myapp:latest"
```

**Receipt:** Container ID `a1b2c3d4...`, status "Up 5 seconds", port 3000 bound to localhost. ✅

**Rollback:** `docker stop myapp && docker rm myapp`

---

### Step 3 — Verify app is responding locally (L0)

```bash
ssh vps "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/health"
# → 200
```

**Receipt:** HTTP 200 on health endpoint. ✅

**Checkpoint:** `cp-1` — app running and healthy on localhost:3000.

---

### Step 4 — Configure Nginx reverse proxy (L1)

**Intent:** Add Nginx config to proxy `app.example.com` → `localhost:3000`.

```bash
ssh vps "cat > /etc/nginx/sites-available/myapp << 'EOF'
server {
    listen 80;
    server_name app.example.com;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
ln -sf /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx"
```

**Receipt:** `nginx -t` → syntax OK, `systemctl reload` → exit 0. ✅

**Rollback:** `rm /etc/nginx/sites-enabled/myapp && systemctl reload nginx`

---

### Step 5 — Create DNS A record (L2 — user confirmed)

**Intent:** Point `app.example.com` to the VPS IP via Cloudflare API.

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"A","name":"app","content":"203.0.113.10","proxied":true}' \
  | jq '.result.id, .success'
```

**Receipt:** Record ID `dns_abc123`, `"success": true`. ✅

**Rollback:** `DELETE /dns_records/dns_abc123`

**Checkpoint:** `cp-2` — full stack configured.

---

### Step 6 — End-to-end verification (L0)

```bash
# Wait for DNS propagation
sleep 30

curl -s -o /dev/null -w "%{http_code}" https://app.example.com/health
# → 200

curl -s https://app.example.com/health | jq '.status'
# → "ok"
```

**Receipt:** HTTP 200 through the full chain (DNS → Cloudflare → Nginx → Docker). ✅

---

### Drift Recovery (encountered)

After step 4, Nginx reload initially failed:

```
nginx: [emerg] duplicate server_name "app.example.com"
```

**Recovery:**
1. Stopped chain.
2. Found existing config in `/etc/nginx/sites-enabled/app-old`.
3. Verified it was stale (pointed to non-existent port 8080).
4. Removed stale config, retried reload → success.
5. Updated ledger with new state.

---

### Audit Trail

| # | Timestamp        | Action                    | Risk | Receipt                        | Status |
|---|------------------|---------------------------|------|--------------------------------|--------|
| 1 | 2026-03-22 01:00 | Verify Docker + Nginx     | L0   | Both healthy (parallel)        | ✅      |
| 2 | 2026-03-22 01:01 | Run app container         | L1   | Container up, port 3000       | ✅      |
| 3 | 2026-03-22 01:02 | Curl health (local)       | L0   | HTTP 200                       | ✅      |
| 4 | 2026-03-22 01:03 | Configure Nginx           | L1   | syntax OK, reload OK (after drift fix) | ✅ |
| 5 | 2026-03-22 01:05 | Create DNS record         | L2   | Record ID dns_abc123           | ✅      |
| 6 | 2026-03-22 01:06 | E2E curl via public URL   | L0   | HTTP 200, status "ok"          | ✅      |

---

## Final Summary

- **Changed:** Deployed `myapp` container, configured Nginx proxy, created Cloudflare DNS record
- **Evidence:** End-to-end HTTP 200 at `https://app.example.com/health`
- **Remaining:** No HTTPS cert configured (Cloudflare proxy handles TLS, but origin is HTTP)
- **Next safe action:** Add Let's Encrypt cert to Nginx for origin encryption
