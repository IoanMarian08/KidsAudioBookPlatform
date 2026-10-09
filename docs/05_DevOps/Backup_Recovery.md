# Backup, Restore and Disaster Recovery

Version: 2.0.0  
Status: Required production runbook framework  
Owner: Platform/SRE, Security, Data Owners

## 1. Recovery objectives

Before production, business owners must approve RTO (maximum tolerated outage) and RPO (maximum tolerable data loss) by dataset. Do not advertise untested numeric guarantees. Plan for accidental deletion, migration failure, region outage, credential compromise, media loss and billing reconciliation drift.

## 2. Data inventory

| Dataset | Source of truth | Recovery approach |
|---|---|---|
| Accounts, profiles, progress, catalog | PostgreSQL | Encrypted backups, PITR/WAL, restore drills |
| Subscriptions and entitlements | PostgreSQL + provider truth | DB restore + provider reconciliation |
| Original audio/illustrations | Versioned private object storage | Versioning/replication, integrity manifests |
| Published derivatives | Object storage | Restore or regenerate from originals |
| Outbox and broker state | PostgreSQL outbox; durable queues | Reprocess idempotently after restore |
| Redis cache | PostgreSQL/other authoritative data | Rebuild; no reliance on Redis-only facts |
| Configuration/keys | Vault/secret manager + IaC | Versioned secure recovery process |
| Audit trail | Protected storage/database | Retention/integrity controls with access audit |

## 3. Backup requirements

- Backup media encrypted at rest/in transit, using independent access controls from the production app.
- Keep at least one isolation boundary against compromised production credentials (immutable/offsite where feasible).
- PostgreSQL backup schedules and WAL/PITR retention selected to meet approved RPO.
- Periodically validate completed backup **and** practical restore, not success messages alone.
- Protect account and child profile data in restores; staging restore exercises use isolated access and appropriate anonymization.
- Document secrets/key recovery separately to avoid storing keys with backups.

## 4. Restoration procedure

1. Incident commander authorizes recovery, scopes affected datasets and freezes destructive jobs.
2. Record source of truth, backup timestamp, target environment, expected RPO impact and rollback plan.
3. Restore to an isolated environment and verify database consistency and checksum/row-count invariants.
4. Validate core journeys: parent sign-in, profile ownership, catalog visibility, story authorization and progress.
5. Reconcile provider purchases/renewals/refunds against authoritative billing events.
6. Rebuild caches, regenerate search indexes and replay outbox/events idempotently.
7. Cut over traffic using approved ingress/config change; monitor error rate, lag and correctness.
8. Close incident only after business checks and user impact are documented.

## 5. Disaster scenarios

| Scenario | Immediate containment | Recovery |
|---|---|---|
| Accidental destructive migration | Stop writes, preserve logs | Restore/PITR or forward repair, validate integrity |
| Compromised credentials | Revoke/rotate, isolate access | Verify immutable backup and secret integrity |
| Region loss | Trigger DR plan | Restore replicas/services in prepared region if available |
| Deleted media objects | Disable broken publication where necessary | Recover versioned originals and regenerate variants |
| Duplicate events after restore | Enable deduplication | Replay idempotently, reconcile materialized read models |
| Wrong entitlements | Fail closed for new unverified grants | Reconcile with provider records and audit corrections |

## 6. Testing cadence and evidence

At minimum exercise staged restores before first production launch, after changes to backup mechanism/schema and on a defined recurring schedule. Retain test timestamp, dataset size, actual recovery time, observed data loss and findings. Test access to keys, DNS/TLS, credentials and external provider reconciliation, not just SQL import.

## 7. Acceptance checklist

[ ] RTO/RPO approved for each critical dataset  
[ ] Offsite/immutable strategy and retention signed off  
[ ] Encryption, least privilege and audit enabled  
[ ] Recent restoration drill completed successfully  
[ ] Signed media and payment reconciliation validated after restore  
[ ] Incident roles, cutover and rollback procedures documented  
[ ] Disaster recovery cost and limitations reviewed

Related: [Infrastructure](Infrastructure.md), [Deployment](Deployment.md), [Monitoring](Monitoring.md), [Architecture DR](../03_Architecture/C4_Model/18_Backup_and_Disaster_Recovery.md).
