# Data Migration and Backfill Strategy

Version: 1.0.0  
Status: Active  
Owners: Architecture, Backend Engineering, Data Engineering, DevOps  
Last reviewed: 2026-07-15

## 1. Purpose

This document defines how KidsAudioBookPlatform changes persisted data safely across schema evolution, service extraction, provider replacement, historical corrections, and large backfills. The objective is to preserve correctness, availability, auditability, and rollback options without exposing users to inconsistent behavior.

## 2. Scope

The strategy applies to:

- PostgreSQL schema and data migrations;
- Redis cache format changes;
- object-storage key or metadata migrations;
- event and read-model rebuilds;
- local mobile database migrations;
- service extraction and data ownership transfer;
- historical entitlement, subscription, notification, and playback corrections;
- bulk administrative imports.

## 3. Core Principles

1. Production data is never modified manually without an approved and auditable procedure.
2. Schema changes and large data backfills are separated when combined execution creates operational risk.
3. Migrations are forward-first and idempotent where practical.
4. Application versions remain compatible throughout rolling deployment.
5. Every migration has an owner, validation plan, stop conditions, and recovery procedure.
6. User-visible and security-sensitive data receives stricter reconciliation.
7. Backfills are rate-limited to protect transactional workloads.
8. Migration progress and anomalies are observable.

## 4. Migration Classes

| Class | Example | Default execution |
|---|---|---|
| Schema-only | Add nullable column or index | Flyway deployment migration |
| Small deterministic data change | Populate bounded configuration values | Flyway or controlled job |
| Large backfill | Recompute millions of progress summaries | Resumable background job |
| Ownership transfer | Extract subscription data to a service | Dual-read/write migration plan |
| Binary asset migration | Change object key layout or rendition format | Manifest-driven worker |
| Corrective migration | Repair incorrect entitlement state | Audited reconciliation job |
| Mobile local migration | Change offline queue schema | Versioned transactional client migration |

## 5. Expand-and-Contract

Breaking changes use this sequence:

1. expand the schema or contract;
2. deploy code compatible with old and new representations;
3. backfill historical data;
4. verify completeness and correctness;
5. switch readers to the new representation;
6. switch writers and stop producing the old representation;
7. observe for an agreed stability window;
8. remove obsolete fields, tables, topics, or storage objects in a later release.

No destructive contraction occurs in the same release that introduces the replacement.

## 6. Backfill Job Design

Every large backfill must support:

- deterministic selection of work;
- stable pagination using primary-key or cursor ranges;
- bounded batches;
- checkpoint persistence;
- idempotent processing;
- retry with classified errors;
- pause, resume, and cancellation;
- configurable concurrency and rate limits;
- dry-run or report-only mode where useful;
- per-batch and aggregate reconciliation metrics.

Example checkpoint:

```json
{
  "jobType": "PLAYBACK_SUMMARY_BACKFILL",
  "jobVersion": 2,
  "lastProcessedId": "018f...",
  "processed": 153200,
  "succeeded": 153180,
  "failed": 20,
  "startedAt": "2026-07-15T08:00:00Z",
  "updatedAt": "2026-07-15T08:42:10Z"
}
```

## 7. Validation Strategy

Validation must include relevant combinations of:

- source and destination row counts;
- checksums or deterministic aggregates;
- required-field completeness;
- uniqueness and referential-integrity checks;
- domain invariant checks;
- sampled record comparisons;
- independent reconciliation queries;
- API behavior before and after the migration;
- security and entitlement verification;
- object checksum and manifest verification.

A migration is not complete merely because the job reached its final cursor.

## 8. Performance Protection

Backfills must not exhaust shared resources. Controls include:

- low-priority worker pools;
- adaptive throttling based on database latency and queue depth;
- batch commits;
- avoidance of full-table locks;
- production-safe index creation;
- statement and lock timeouts;
- maintenance windows for unavoidable high-impact operations;
- automatic pause when SLO or saturation thresholds are exceeded.

## 9. Failure Handling

Failures are classified as:

- transient: retry with bounded backoff;
- data-specific: quarantine the record and continue where safe;
- systemic: pause the migration and alert the owner;
- invariant violation: stop writes to the affected destination when correctness is uncertain;
- security-sensitive: stop immediately and trigger incident handling.

Failed records must retain enough non-sensitive context for diagnosis and replay.

## 10. Rollback and Recovery

Rollback options depend on the migration stage:

- before reader switch: disable new writes and continue using the old representation;
- during dual operation: reconcile and repair destination data while the source remains authoritative;
- after reader switch but before contraction: revert readers and preserve new data for investigation;
- after contraction: use corrective forward migration or validated restore procedures.

A migration must define the last point at which simple rollback remains possible.

## 11. Data Ownership Transfer

Service extraction requires:

1. a declared source and future owner;
2. a canonical data contract;
3. initial snapshot migration;
4. change-data propagation or dual writing;
5. lag and divergence monitoring;
6. destination shadow reads;
7. controlled reader cutover;
8. source write retirement;
9. final reconciliation;
10. removal of obsolete access paths.

Dual writing without reconciliation and idempotency is prohibited.

## 12. Object Storage Migration

Object migrations use manifests containing:

- source key;
- destination key;
- asset and content version;
- expected size;
- checksum;
- encryption or access classification;
- migration status;
- verification timestamp.

Objects are not deleted from the source until destination verification and a retention window complete.

## 13. Mobile Database Migration

Mobile migrations must:

- run transactionally where supported;
- preserve queued offline operations;
- tolerate interrupted upgrades;
- include downgrade behavior or minimum-version enforcement;
- avoid deleting downloaded media before entitlement and manifest reconciliation;
- emit privacy-safe migration diagnostics.

## 14. Security and Privacy

- Migration jobs use least-privilege credentials.
- Production extracts are encrypted and access-controlled.
- Temporary files have explicit retention and secure deletion.
- Logs exclude credentials, raw tokens, child names, and unnecessary personal data.
- Data-subject deletion and legal holds remain effective during migration.
- Administrative corrective jobs require authorization and immutable audit records.

## 15. Observability

Track:

- records scanned, processed, skipped, failed, and retried;
- throughput and estimated remaining work;
- checkpoint age;
- database latency and lock waits;
- destination divergence;
- reconciliation mismatches;
- object-copy and checksum failures;
- paused or abandoned migrations.

Every long-running migration has a dashboard and alert ownership.

## 16. Approval Checklist

Before production execution, confirm:

- owner and communication channel;
- affected datasets and users;
- reviewed script or worker version;
- tested execution against production-like volume;
- backup and restore readiness;
- stop and rollback conditions;
- rate limits and maintenance window;
- reconciliation queries;
- dashboards and alerts;
- privacy and security review;
- post-migration cleanup plan.

## 17. Completion Criteria

A migration is complete only when:

1. all intended records are processed;
2. reconciliation passes within approved tolerances;
3. application readers and writers use the intended representation;
4. no unresolved high-severity failures remain;
5. observability confirms stable behavior;
6. temporary resources are removed;
7. documentation and ownership maps are updated;
8. obsolete structures are scheduled for controlled removal.
