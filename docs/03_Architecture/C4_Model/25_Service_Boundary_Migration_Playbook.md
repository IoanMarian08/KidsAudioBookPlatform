# Service Boundary and Data Migration Playbook

Version: 2.0
Status: Active; applies to changes between **already deployed microservices**
Owners: Architecture, Backend, DevOps, Security
Decision: [ADR-0015](../../00_Project/ADR/ADR-0015-microservices-from-first-release.md)

> This playbook governs **service split, merge, domain ownership transfer and database migration** between independently deployed microservices.

## 1. Purpose

Microservices are independently deployed from the first release. Changes to existing boundaries must preserve child safety, profile ownership, subscription correctness, business continuity, data integrity, privacy and independent operability. A service boundary migration is never just moving Java classes.

## 2. Preconditions

A proposed change requires:
- an ADR naming the old and new authoritative service owner;
- an inventory of REST endpoints, event types/versions, DB tables, storage objects, cache keys, jobs and consumers;
- data-classification and child-privacy impact analysis;
- before/after dependency and trust-boundary diagrams;
- coexistence/compatibility period and older-mobile-client policy;
- replay/rollback/reconciliation plan, error budget and responsible on-call;
- estimated deployment, storage, egress and monitoring costs.

## 3. Target ownership

The target service owns its own executable image, unique logical PostgreSQL database/user, Flyway history, private contracts, API handlers, outbox/inbox, secrets, dashboards and restore procedure. **Direct SQL, FK or shared JPA entity references across service boundaries remain prohibited.** If one physical PostgreSQL cluster hosts several databases, that does not relax isolation.

## 4. Contract-first migration

1. Introduce or extend a versioned target REST/OpenAPI operation and event schema.
2. Add consumer-driven tests against old/new peers, gateway routing and authorization.
3. Add idempotency, timeout, retries/compensation and dead-letter policy.
4. Deploy target service in shadow or read-only mode when feasible.
5. Start publishing versioned transition events through the source owner's transactional outbox.
6. Backfill target projections/data by stable IDs and checkpoints.
7. Validate counts, checksums, referential semantics and business invariants.
8. Change read ownership behind safe routing/flag, then write ownership at a defined cutover.
9. Observe all dependent clients/consumers before retiring old paths.
10. Remove obsolete grants, job handlers, migrations and shared compatibility code once verified.

## 5. Data migration options

| Strategy | Suitable when | Must verify |
|---|---|---|
| New data only | No historical records required by new owner | Historical access contract stays supported |
| Snapshot + change events | Live migration of existing authoritative data | Monotonic checkpoints, deduplication, catch-up |
| Read model projection | Target needs query view, not ownership | Rebuildability and stale-data policy |
| Online backfill and cutover | High availability required | Dual-read comparison and rollback plan |

Avoid unsupervised dual writes to two databases. If temporary dual writing is unavoidable, designate one authoritative writer and a reconciled outbox delivery path; record divergence alert/repair procedure.

## 6. Example cutover

~~~mermaid
sequenceDiagram
  participant Router as API Gateway
  participant Source as Original service
  participant Broker as RabbitMQ
  participant Target as New owning service
  Router->>Source: Current write request
  Source->>Source: Commit mutation + outbox
  Source->>Broker: Publish versioned change
  Broker->>Target: At-least-once replay
  Target->>Target: Inbox dedup + projection/backfill
  Note over Source,Target: Compare and reconcile before switch
  Router->>Target: New write route after approved cutover
  Target->>Target: Persist as authoritative owner
~~~

Never simultaneously grant two services unrestricted write ownership. Propagate correlation IDs, service identity and end-user actor context safely.

## 7. Security and privacy checks

- The new service independently enforces parent identity, profile ownership and Parent Zone proof where needed.
- Secrets and database credentials are scoped only to the target.
- Data-minimization/retention and deletion saga handlers are updated for the new owner.
- Suspended content and revoked entitlements continue to fail closed during migration.
- Administrative audit events preserve actor, action and transition reason.
- Signed media URL validity/refresh remains safe through deployment overlap.

## 8. Failure and rollback

| Failure | Response |
|---|---|
| Event backlog or repeated delivery | Pause cutover; retain inbox/outbox and replay idempotently |
| Divergent source/target data | Halt write migration, compare/reconcile by version |
| Gateway route/regression | Restore old route if source remains write-compatible |
| Target database inaccessible | Reject unsafe writes; no unapproved foreign-DB fallback |
| Subscription/provider event ordering | Re-query provider authority and protect newer versions |
| Partial account deletion saga | Keep durable pending state until all owners acknowledge |

Rollback after irreversible writes requires an explicit forward-repair/data reconciliation plan; changing container image alone cannot undo data ownership changes.

## 9. Observability, performance and cost

Before cutover record per-service p50/p95/p99, error rate, timeouts, queue age, inbox duplicates, database pool usage, security denials, subscription mismatch rates and storage/egress. During cutover track correlation IDs across source, gateway, target and broker. Alert on a missing consumer, stale projection or privacy-deletion handler.

## 10. Test matrix

- Unit: business policy unaffected by service ownership change.
- Contract: old and new API/event schema compatibility, routing and auth claims.
- Integration: separately migrated databases; no foreign SQL privileges.
- Resilience: timeout/retry/circuit-breaker/DLQ, kill source/target during cutover.
- End-to-end: parent login, child profile, story authorization, purchase restore, offline sync and account deletion.
- Recovery: restore owning service DB and replay outbox without resurrecting deleted/forbidden access.

## 11. Completion criteria

The ADR is accepted, data ownership is unambiguous, only one service remains authoritative, consumers work across version windows, unauthorized foreign-database access is denied, end-to-end security tests pass, dashboards and operational runbooks are updated, and old compatibility routes can be removed without a user-facing regression.

Related: [Microservices Architecture](../Microservices_Architecture.md), [Contracts](../Microservices_Contracts_and_Flows.md), [Database Design](../Database_Design.md), [Deployment](../../05_DevOps/Deployment.md).
