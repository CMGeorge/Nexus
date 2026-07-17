# ADR-0005: File Storage High Availability — MinIO Multi-Site Replication

## Status
Proposed

## Date
2026-07-15

## Context
Nexus has a `files/` domain for document uploads, attachments, and media. In the current Docker Compose dev setup, files are stored on a local volume. For production, we need:

- High availability: no single point of failure for file storage
- Cross-region replication: files available in multiple DCs for DR and latency
- S3-compatible API: standard interface, portable, works with existing S3 SDKs
- Multi-tenant isolation: files must never leak between tenants
- Immutable audit trail: uploaded files must be tamper-evident
- RPO < 5 min for file data, RTO < 15 min for file access after DC failure

### Current Architecture
- Files domain in `backend/app/files/`
- Dev: local filesystem storage via Docker volume
- No current object storage abstraction (this ADR defines it)

## Decision

### Primary: MinIO in Multi-Site Active-Active Replication

| Aspect | Choice |
|--------|--------|
| **Object storage** | MinIO (S3-compatible) |
| **Deployment** | 4-node cluster per DC (minimum for erasure coding) |
| **Replication** | Bucket-level replication between DC-1 (primary) and DC-2 (geo-replica) |
| **Erasure coding** | 2 parity drives per 4 drives (survives 2 disk failures per cluster) |
| **Storage backend** | Local NVMe SSDs on each node (no SAN/NAS dependency) |
| **API** | S3-compatible (use `boto3` / `aioboto3` from backend) |
| **Multi-tenancy** | Per-tenant buckets with IAM policies, or prefix-based isolation within shared bucket |
| **Encryption** | Server-side SSE-S3 (AES-256-GCM) with per-tenant KMS keys |

### Replication Architecture

```mermaid
graph TB
    subgraph "DC-1 (Primary)"
        App1[App Instance] -->|S3 API| MINIO1[MinIO Cluster]
        MINIO1_N1[Node 1] --- MINIO1_N2[Node 2]
        MINIO1_N2 --- MINIO1_N3[Node 3]
        MINIO1_N3 --- MINIO1_N4[Node 4]
        LB1[Load Balancer] --> MINIO_NODES1[Nodes 1-4]
    end
    subgraph "DC-2 (Geo-Replica)"
        MINIO2[MinIO Cluster]
        MINIO2_N1[Node 1] --- MINIO2_N2[Node 2]
        MINIO2_N2 --- MINIO2_N3[Node 3]
        MINIO2_N3 --- MINIO2_N4[Node 4]
    end
    App1 -->|Write| MINIO1
    MINIO1 -- "bucket replication (near-sync)" --> MINIO2
    App1 -.->|Read (failover)| MINIO2
```

### Bucket Design for Multi-Tenancy

```
nexus-files/
  {tenant-uuid}/
    uploads/
    attachments/
    media/
    exports/
  
nexus-backups/       # Weekly offsite DB backup storage
nexus-static/         # Static assets (logos, templates)
```

Each tenant's prefix is isolated by MinIO IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
    "Resource": ["arn:aws:s3:::nexus-files/${aws:PrincipalTag/TenantId}/*"]
  }]
}
```

The backend's files service resolves the tenant UUID from `Depends(get_current_tenant)` and scopes all S3 operations to that prefix.

## Rationale

### Why MinIO over alternatives?

| Alternative | Rejected Because |
|-------------|-----------------|
| **AWS S3 + CRR** | Vendor lock-in; cannot run on VPS/bare metal; cross-region replication is asynchronous and has variable lag; egress costs for serving files |
| **GCP Cloud Storage** | Same lock-in; egress pricing at scale |
| **Ceph/Rook** | Kubernetes-only; significant operational complexity; overkill for <100 TB scale; requires dedicated Ceph expertise |
| **SeaweedFS** | Lighter weight, but less mature S3 compatibility; smaller community; fewer production references at our scale |
| **GlusterFS** | POSIX filesystem, not object storage; no built-in S3 API; replication is filesystem-level, not bucket-level |
| **Local NFS + rsync** | No HA; single point of failure; no S3 API; manual failover |

### Why MinIO specifically:
1. **S3-compatible**: Drop-in replacement for AWS S3; use `boto3`/`aioboto3` — no code changes if we ever migrate to AWS S3
2. **Bucket replication**: Near-synchronous replication between clusters; configurable per-bucket rules
3. **Erasure coding**: Survives `m` disk failures out of `n` total; 50% storage overhead at EC 4:2 (better than 3x replication)
4. **Active-active**: Both DCs can serve reads; writes go to primary and replicate
5. **Lightweight**: Single Go binary, <100 MB memory per node at our scale
6. **Kubernetes-native**: Runs as StatefulSet if we adopt k3s
7. **Built-in encryption**: SSE-S3 with KMS integration; audit logging

### Self-hosted vs Managed Trade-off
- MinIO self-hosted on VPS: ~$40–80/month for 4× small NVMe VPS per DC
- AWS S3 equivalent: $23/TB/month storage + $50/TB egress + request costs → unpredictable at scale
- Self-hosting MinIO gives cost predictability and no egress fees (serving files is bandwidth you already pay for)

## Consequences

### Positive
- No vendor lock-in for object storage; S3-compatible API is portable
- Both DCs can serve file reads (low-latency for users in different regions)
- Erasure coding provides durability without 3x storage overhead
- Per-tenant IAM policies enforce isolation at the storage layer
- Server-side encryption protects data at rest and during replication
- Built-in versioning and object locking for immutability

### Negative
- Must manage 8+ MinIO nodes (4 per DC) — more operational surface area
- Bucket replication is near-synchronous, not synchronous → seconds of potential replication lag
- Two concurrent writers to the same object in different DCs require conflict resolution (application must write through primary)
- NVMe storage cost at VPS providers varies widely
- MinIO multi-site requires careful network configuration (low-latency interconnect between DCs if possible)

### Mitigations Required
- Application writes ALWAYS go to DC-1 primary MinIO; DC-2 is read-only unless failed over
- Prometheus alert if replication lag > 60 seconds
- Prometheus alert if any MinIO node is down
- Disk failure alerting (MinIO exposes Prometheus metrics for drive health)
- Monthly restore test: verify DC-2 can serve files independently
- Traefik routes file traffic to MinIO via path-based routing or dedicated subdomain (`files.nexus.app`)

## Validation Plan

| Test | Expected Result |
|------|----------------|
| **Simulate 2 disk failures** (kill 2 of 4 MinIO nodes) | EC 4:2 erasure coding tolerates loss; all files readable; no data corruption |
| **Cross-DC replication** (upload file to DC-1, check DC-2 bucket) | File appears in DC-2 bucket within **30 seconds** |
| **S3 API compatibility** (`aws s3 ls --endpoint-url http://minio:9000`) | Standard S3 commands work against MinIO; listing, upload, download, delete |
| **Bucket policy enforcement** (attempt cross-tenant access) | Tenant A cannot read Tenant B's bucket objects |
| **Storage recovery after full DC-1 loss** (restore from DC-2 replicas) | All files available from DC-2; bucket replication lag **< 1 minute** |
| **Upload throughput** (100 concurrent 5MB uploads) | Throughput > 100 MB/s on local network; no upload failures |

If any test fails, this ADR must be reconsidered.

| Alternative | Rejected Because |
|-------------|-----------------|
| AWS S3 + CRR | Vendor lock-in; egress costs; lag variability |
| Ceph/Rook | K8s-only; operational complexity; overkill at our scale |
| SeaweedFS | Less mature S3 compatibility |
| GlusterFS | POSIX, not object; no S3 API |
| Local NFS + rsync | No HA; manual failover |

## References
- Redmine issue: #502
- Related ADRs: ADR-0003 (PostgreSQL replication), ADR-0004 (backup strategy)
- External docs:
  - [MinIO Multi-Site Replication](https://min.io/docs/minio/linux/operations/install-deploy-manage/multi-site-replication.html)
  - [MinIO Erasure Coding](https://min.io/docs/minio/linux/operations/concepts/erasure-coding.html)
  - [MinIO IAM Policies](https://min.io/docs/minio/linux/administration/identity-access-management/policy-based-access-control.html)
