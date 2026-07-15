# Disaster Recovery Runbook — Nexus Platform

## Status
Proposed (Living Document)

## Date
2026-07-15

## RPO and RTO Targets

| Scenario | RPO Target | RTO Target |
|----------|-----------|-----------|
| Single PostgreSQL node failure | 0 (sync replication) | < 60s (Patroni auto-failover) |
| Entire DC-1 failure | < 1 min (WAL + bucket replication lag) | < 15 min (manual promotion + DNS cutover) |
| Accidental data deletion | < 1 min (PITR) | < 30 min (pgBackRest restore) |
| Ransomware / full corruption | < 1 min (offsite WAL) | < 4 hours (full offsite restore) |

---

## Scenario 1: PostgreSQL Primary Failure (Single Node)

### Trigger
- Prometheus alert: `patroni_node_down` OR `pg_replication_lag > 30s`
- Manual observation: primary PostgreSQL unresponsive

### Procedure (Automatic — Patroni)
1. Patroni detects primary failure via etcd health checks (timeout: 30s)
2. Patroni promotes the synchronous standby to new primary
3. etcd leader updates cluster configuration → new primary is writable
4. PgBouncer reconnects to new primary (via `pgbouncer.ini` pointing to Patroni-managed VIP or DNS)
5. Application connections re-established (connection retry logic with exponential backoff)

### Validation
```bash
# Check cluster state
patronictl -c /etc/patroni/patroni.yml list

# Verify replication is running
psql -h <new-primary> -c "SELECT * FROM pg_stat_replication;"

# Verify application health
curl -f https://api.nexus.app/health
```

### Rollback
- Old primary rejoins as standby: `patronictl reinit nexus <old-primary-node>`

---

## Scenario 2: Entire DC-1 Failure (Full Site Failover)

### Trigger
- Prometheus alert: ALL DC-1 nodes unreachable (network partition, power outage, natural disaster)
- Manual decision (no auto-failover for full DC cutover — requires human judgment)

### Pre-requisites
- DC-2 has: async PostgreSQL replica, MinIO replica, pgBackRest offsite backups
- DNS: `api.nexus.app` and `files.nexus.app` controlled via DNS provider with low TTL (60s)

### Procedure (Manual — Estimated time: 10–15 min)

#### Step 1: Promote PostgreSQL in DC-2 (5 min)
```bash
# SSH to DC-2 Patroni node
ssh admin@dc2.nexus.app

# Promote the async standby to primary
patronictl pause nexus  # Pause Patroni to prevent auto-switchback
psql -h dc2-db-standby -c "SELECT pg_promote();"

# Verify promotion
psql -h dc2-db-standby -c "SELECT pg_is_in_recovery();"
# Expected: f (false = primary)

# Reconfigure PgBouncer to point to new primary
sudo sed -i 's/dc1-primary/dc2-standby/' /etc/pgbouncer/pgbouncer.ini
sudo systemctl reload pgbouncer
```

#### Step 2: Promote MinIO in DC-2 (2 min)
```bash
# Access MinIO console
mc alias set dc2 http://dc2-minio:9000 <access-key> <secret-key>

# Make DC-2 bucket writable (disable read-only replication target mode)
mc replicate update dc2/nexus-files --enable-delete-replication

# Verify bucket is accessible
mc ls dc2/nexus-files/
```

#### Step 3: DNS Cutover (3 min)
```bash
# Update DNS records via provider API (example: Cloudflare)
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"content":"<DC2-LOAD-BALANCER-IP>","ttl":60}'

# Verify propagation
dig api.nexus.app +short
```

#### Step 4: Validate (2 min)
```bash
# Application health
curl -f https://api.nexus.app/health

# Database connectivity (create test record)
curl -X POST https://api.nexus.app/api/v1/health/db-check -H "Authorization: Bearer <ADMIN_TOKEN>"

# File upload/download
curl -X POST https://files.nexus.app/nexus-files/test-tenant/health-check.txt -d "DR test OK"
curl https://files.nexus.app/nexus-files/test-tenant/health-check.txt
```

#### Step 5: Communicate (1 min)
- Post status update to status page (status.nexus.app)
- Notify team in Slack/Teams: "DC-1 failover complete. Running from DC-2."

### Rollback (When DC-1 Recovers)
1. Resync PostgreSQL: `pg_basebackup` from DC-2 primary to DC-1 node → rejoin as standby
2. Resync MinIO: `mc replicate resync dc1/nexus-files --remote-dc2`
3. DNS cutback to DC-1 (reverse of Step 3)
4. Patroni unpause: `patronictl resume nexus`

---

## Scenario 3: Point-in-Time Recovery (Data Deletion)

### Trigger
- Accidental `DELETE` or `DROP` reported
- Time of incident identified (from audit logs: `SELECT * FROM audit_logs WHERE table_name = '...' ORDER BY created_at DESC LIMIT 10;`)

### Procedure (Estimated time: 20–30 min)

```bash
# 1. Stop application (prevent further writes)
ssh admin@dc1.nexus.app
sudo systemctl stop nexus-api

# 2. Restore to point-in-time (e.g., 5 minutes before incident)
sudo -u postgres pgbackrest --stanza=nexus --type=time \
  --target="2026-07-15 14:23:00+00" \
  --target-action=promote \
  restore

# 3. Start PostgreSQL with restored data
sudo systemctl start postgresql@16-main

# 4. Verify data integrity
psql -c "SELECT count(*) FROM <affected_table>;"

# 5. Re-establish replication
patronictl reinit nexus dc1-standby1

# 6. Restart application
sudo systemctl start nexus-api
curl -f https://api.nexus.app/health
```

---

## Scenario 4: Ransomware / Full Corruption

### Trigger
- Widespread data corruption detected
- Backup repositories verified intact

### Procedure (Estimated time: 2–4 hours)

```bash
# 1. Isolate: take DC-1 offline entirely
# 2. Provision fresh PostgreSQL instance in DC-2
# 3. Restore from latest offsite backup
sudo -u postgres pgbackrest --stanza=nexus --repo=2 restore

# 4. Replay WAL to latest available point
sudo -u postgres pgbackrest --stanza=nexus --repo=2 \
  --type=time --target=latest restore

# 5. Promote and validate
psql -c "SELECT pg_is_in_recovery();"  # should be false

# 6. Restore MinIO from DC-2 replica (already read-only, data intact)
# 7. DNS cutover to DC-2 (see Scenario 2)
```

---

## Monitoring & Alerting (Required)

| Alert | Severity | Threshold |
|-------|----------|-----------|
| `pg_replication_lag` > 1s | Warning | 1 minute |
| `pg_replication_lag` > 30s | Critical | Immediate |
| `patroni_node_down` | Critical | Immediate |
| `etcd_leader_changes` > 2 in 10min | Warning | 10 minutes |
| `pgbackrest_stanza_check_failed` | Critical | Immediate |
| `wal_archive_lag` > 5min | Critical | Immediate |
| `minio_node_down` | Critical | Immediate |
| `minio_replication_lag` > 60s | Warning | 5 minutes |
| `disk_usage` > 80% | Warning | 30 minutes |
| `disk_usage` > 95% | Critical | Immediate |

---

## Testing Schedule

| Test | Frequency | Owner |
|------|----------|-------|
| Patroni switchover (planned) | Monthly | DevOps |
| pgBackRest restore + smoke test | Monthly | DevOps |
| Full DC failover drill | Quarterly | DevOps + Backend Lead |
| Offsite restore test | Quarterly | DevOps |

---

## References
- Redmine issue: #502
- Related ADRs: ADR-0003 (PostgreSQL replication), ADR-0004 (backup strategy), ADR-0005 (file storage HA)
