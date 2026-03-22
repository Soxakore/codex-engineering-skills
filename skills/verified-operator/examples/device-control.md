# Example: Push a Config to an Android Device via ADB

Demonstrates device control with verification and rollback.

---

## Ledger

```text
Objective:      Push updated config.json to Android app's data directory and verify the app loads it
Systems:        local filesystem, ADB (USB-connected device), Android app
Current state:  Device connected, app installed, old config active
Next action:    L0 — verify ADB connection and current config
Expected receipt: device serial in `adb devices`, current config contents
Risk level:     L0
Rollback:       restore backed-up config
Deadline:       none
Timeout:        10s per adb command
Estimated cost: $0
Cumulative spend: $0
Budget:         $0
```

---

## Execution

### Step 1 — Verify device connection (L0)

```bash
adb devices -l
```

**Receipt:** `R5CT12345  device  usb:1-1  product:starqltesq model:SM_G965U`. ✅

---

### Step 2 — Backup current config (L0)

**Intent:** Create a rollback point before overwriting.

```bash
adb pull /sdcard/Android/data/com.example.app/files/config.json ./config.backup.json
```

**Receipt:** `1 file pulled. 0.1 MB/s`, local file exists and is valid JSON. ✅

**Checkpoint:** `cp-1` — backup saved locally as `./config.backup.json`.

---

### Step 3 — Push new config (L1)

```bash
adb push ./config.json /sdcard/Android/data/com.example.app/files/config.json
```

**Receipt:** `1 file pushed. 0.2 MB/s`. ✅

---

### Step 4 — Verify file on device (L0)

**Intent:** Read the file back to confirm it wasn't corrupted or blocked.

```bash
adb shell "cat /sdcard/Android/data/com.example.app/files/config.json | head -5"
```

**Receipt:** Output matches first 5 lines of local `./config.json`. ✅

---

### Step 5 — Restart app and verify it loaded the config (L1)

```bash
adb shell "am force-stop com.example.app"
adb shell "am start -n com.example.app/.MainActivity"
sleep 3
adb logcat -d -s AppConfig --format=brief | tail -5
```

**Receipt:** Logcat shows `AppConfig: Loaded config v2.1, 12 rules active`. ✅

---

### Audit Trail

| # | Timestamp        | Action             | Risk | Receipt                          | Status |
|---|------------------|--------------------|------|----------------------------------|--------|
| 1 | 2026-03-22 01:00 | Verify ADB device  | L0   | Device serial R5CT12345          | ✅      |
| 2 | 2026-03-22 01:01 | Backup config      | L0   | File pulled, valid JSON          | ✅      |
| 3 | 2026-03-22 01:01 | Push new config    | L1   | 1 file pushed                    | ✅      |
| 4 | 2026-03-22 01:02 | Read back from device | L0 | Content matches source           | ✅      |
| 5 | 2026-03-22 01:02 | Restart + logcat   | L1   | Config v2.1 loaded, 12 rules     | ✅      |

---

## Final Summary

- **Changed:** Replaced `config.json` on device with v2.1
- **Evidence:** File readback matches, logcat confirms loaded version
- **Remaining:** Backup file `./config.backup.json` should be kept until next verified session
- **Next safe action:** Delete local backup after confirming app stability over 24h
