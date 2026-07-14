# Resilience and Failure Mode Catalog

Version: 1.0.0  
Status: Active Draft  
Owners: Architecture, Backend Engineering, Mobile Engineering, DevOps  
Last updated: 2026-07-15

## 1. Purpose

This document defines how KidsAudioBookPlatform behaves when dependencies are slow, unavailable, inconsistent, overloaded, or returning invalid data. It identifies expected failure modes, safe degradation paths, retry boundaries, ownership, observability, and recovery actions.

The objective is not to make every dependency mandatory for every request. The objective is to preserve child safety, account integrity, listening continuity, entitlement correctness, and recoverability under partial failure.

## 2. Resilience Principles

1. Core business state remains authoritative in PostgreSQL.
2. A dependency failure must not silently weaken security or entitlement rules.
3. Retried operations must be idempotent.
4. Timeouts are mandatory for all network calls.
5. Retries are bounded and reserved for transient failures.
6. Circuit breakers protect the platform from failing dependencies.
7. Bulkheads isolate unrelated workloads.
8. Async work must survive process restarts.
9. Degraded behavior must be explicit and observable.
10. Recovery procedures must be tested, not assumed.

## 3. Criticality Classes

| Class | Meaning | Examples |
|---|---|---|
| Tier 0 | Security or integrity critical | authentication, authorization, entitlement verification |
| Tier 1 | Core product availability | catalog reads, playback authorization, progress persistence |
| Tier 2 | Important but delay-tolerant | notifications, media processing, recommendations |
| Tier 3 | Optional or analytical | analytics exports, campaign reports, non-critical enrichment |

Tier 0 failures default to denial or safe re-authentication. Tier 1 failures may degrade only when authoritative state remains safe. Tier 2 and Tier 3 work should usually be queued and retried asynchronously.

## 4. Failure Classification

| Failure type | Examples | Default response |
|---|---|---|
| Transient | timeout, temporary network error, provider 503 | bounded retry with backoff |
| Persistent dependency failure | sustained outage, invalid credentials | circuit open, alert, degraded mode |
| Validation failure | malformed request, unsupported value | no retry, return stable error |
| Conflict | stale version, duplicate operation | reconcile or return conflict |
| Security failure | invalid token, denied access, bad signature | no retry, deny and audit |
| Data-integrity failure | broken invariant, missing authoritative reference | stop unsafe write and alert |
| Capacity failure | saturated pool, queue growth, disk pressure | load shed, scale, isolate workload |

## 5. Standard Resilience Controls

### 5.1 Timeouts

Every external or remote operation defines:

- connection timeout;
- request timeout;
- total operation deadline;
- cancellation behavior;
- fallback behavior.

No request may wait indefinitely for Redis, RabbitMQ, object storage, app-store providers, push providers, email providers, or other integrations.

### 5.2 Retries

Retries are allowed only when:

- the failure is classified as transient;
- the operation is idempotent or protected by an idempotency key;
- the remaining deadline permits another attempt;
- the retry does not amplify an outage.

Use exponential backoff with jitter. Do not retry validation failures, authorization failures, invalid signatures, or deterministic business conflicts.

### 5.3 Circuit Breakers

Circuit breakers are appropriate around external providers and remote infrastructure where repeated failures would waste resources or increase latency. Open-circuit behavior must be visible through metrics and must map to a defined error or queued fallback.

### 5.4 Bulkheads

Separate resource pools or queues should isolate:

- interactive API traffic;
- media processing;
- notification delivery;
- subscription reconciliation;
- analytics export;
- administrative bulk jobs.

A backlog in one workload must not consume all threads, connections, or queue capacity for unrelated critical flows.

### 5.5 Load Shedding

Under overload, the platform should reject or defer lower-priority work before critical work. Candidates for shedding include:

- recommendation refresh;
- low-priority notifications;
- non-essential analytics;
- admin exports;
- pre-generation of optional derivatives.

Authentication, authorization, subscription verification, and active playback flows receive higher priority.

## 6. PostgreSQL Failure Modes

| Failure | User impact | Safe behavior | Recovery |
|---|---|---|---|
| Connection pool saturation | slow or failed requests | reject quickly after deadline; do not create unbounded waiting | inspect slow queries, scale pool carefully, reduce load |
| Primary unavailable | writes fail, most reads unavailable | return controlled 503; do not accept writes without durability | failover or restore primary |
| Deadlock | one transaction aborted | retry transaction only when operation is idempotent | inspect lock order and transaction scope |
| Migration failure | deployment blocked | do not route traffic to incompatible release | fix migration or apply forward corrective migration |
| Replica lag | stale read risk | never use lagging replica for security-sensitive decisions | route to primary or wait within bound |
| Constraint violation | rejected write | map to stable conflict/validation error | fix caller or domain logic |
| Data-integrity anomaly | unsafe state | stop affected workflow and alert | investigate, repair through audited procedure |

PostgreSQL failures must never be hidden by writing authoritative business state only to Redis or local memory.

## 7. Redis Failure Modes

| Failure | Affected capabilities | Safe behavior |
|---|---|---|
| Redis unavailable | cache, rate limits, idempotency, elevation state | use PostgreSQL fallback for reconstructable reads; fail conservatively for security-sensitive ephemeral state |
| High latency | API slowdown | enforce short timeout and bypass cache where safe |
| Eviction | cache misses or lost temporary state | rebuild cache; do not assume key existence is durable |
| Stale value | incorrect display or entitlement risk | use short TTL and versioning; authoritative check for sensitive action |
| Split-brain or failover anomaly | temporary inconsistency | avoid using Redis as source of truth |

For rate limiting, fallback policy must be route-specific. Sensitive endpoints may fail closed or use local emergency limits. Public catalog reads may continue with reduced protection if approved.

## 8. RabbitMQ Failure Modes

| Failure | Safe behavior | Recovery |
|---|---|---|
| Broker unavailable during outbox publication | retain unpublished outbox rows | publisher retries after broker recovery |
| Consumer unavailable | queue accumulates | alert on lag; scale or restore consumer |
| Poison message | bounded retry then DLQ | fix cause and replay with authorization |
| Duplicate delivery | idempotent consumer ignores duplicate | retain processing record |
| Out-of-order delivery | use aggregate version or state validation | delay, reject stale event, or reconcile |
| Queue overflow | backpressure and load shedding | scale consumers, reduce producers, archive optional events |
| Invalid schema | do not retry indefinitely | move to DLQ and alert contract owner |

Message acknowledgement occurs only after successful durable handling. A consumer crash before acknowledgement must result in safe redelivery.

## 9. Object Storage and CDN Failure Modes

| Failure | Safe behavior | Recovery |
|---|---|---|
| Upload URL generation fails | do not create usable asset state | retry generation or report temporary failure |
| Upload incomplete | keep asset in pending state | cleanup abandoned multipart upload |
| Storage unavailable | block upload/processing; existing CDN content may continue | restore provider connectivity |
| CDN unavailable | use origin fallback only if secure and capacity-safe | provider failover or recovery |
| Signed URL expired | request fresh authorization | re-evaluate entitlement and issue new URL |
| Checksum mismatch | reject or delete local copy | regenerate or re-download |
| Missing derivative | serve safe available variant where compatible | requeue processing |

Premium media must never become public as a fallback for signed-delivery failure.

## 10. App Store and Billing Provider Failure Modes

| Failure | Safe behavior |
|---|---|
| Provider timeout | return pending/retryable outcome; do not grant unverified premium |
| Invalid receipt/proof | reject and audit |
| Duplicate webhook | idempotently return success after existing processing |
| Out-of-order webhook | compare provider version/time and reconcile authoritative state |
| Provider outage | preserve last verified entitlement only within documented policy |
| Signature validation failure | reject without retry and alert on spikes |
| Reconciliation backlog | expose metrics and process oldest critical items first |

The client must never be the sole authority for purchase success.

## 11. Push and Email Provider Failure Modes

Notification delivery failures must not roll back the business transaction that caused the notification.

| Failure | Safe behavior |
|---|---|
| Provider timeout | retry asynchronously |
| Invalid device token | disable token and stop retrying |
| Permanent rejection | mark failed with provider code |
| Rate limit | honor retry-after and reduce send rate |
| Provider outage | queue within retention window |
| Template rendering failure | do not send partial or unsafe content; alert owner |

Critical account communication remains visible in the in-app inbox when external delivery is unavailable.

## 12. Authentication and Session Failure Modes

| Failure | Safe behavior |
|---|---|
| Identity persistence unavailable | deny login/refresh with controlled error |
| JWKS/key loading failure | use valid cached key only within approved window; otherwise deny |
| Refresh reuse detected | revoke token family and require login |
| Parent elevation store unavailable | deny protected Parent Zone operation |
| Email provider unavailable during registration | create pending verification state only if recoverable and resendable |
| Excessive login failures | apply cooldown and security telemetry |

Security-critical failures must fail closed.

## 13. Mobile Offline Failure Modes

| Failure | Safe behavior |
|---|---|
| Local operation queue corrupt | stop replay, preserve diagnostic metadata, rebuild safely |
| Sync cursor invalid | request controlled full reconciliation |
| Duplicate queued operation | server idempotency returns original outcome |
| Entitlement expired offline | deny content after grace policy |
| Download checksum failure | remove file and request download again |
| Local database migration failure | preserve recoverable data, block unsafe use, offer controlled reset |
| App terminated during sync | resume from durable queue and last committed cursor |

The mobile app must apply downloaded server changes transactionally before advancing its synchronization cursor.

## 14. Media Processing Failure Modes

| Failure | Safe behavior |
|---|---|
| Worker crash | unacknowledged job is retried |
| Unsupported codec | mark permanent validation failure |
| Resource exhaustion | terminate isolated job and retry only within limit |
| Malware scan unavailable | keep asset quarantined |
| Derivative generation partially succeeds | retain explicit partial state; do not publish incomplete required set |
| Repeated deterministic failure | DLQ/manual review |

Content publication must validate that all mandatory media assets are in a ready state.

## 15. Search, Recommendations, and Analytics

These capabilities are non-authoritative.

- Search failure may fall back to basic database-backed discovery only if performance is acceptable.
- Recommendation failure may return curated or recent content.
- Analytics failure must not block playback, account, billing, or publication flows.
- Event loss in analytics paths must be measured and replayable where business value justifies it.
- Stale projections must display known-safe content and exclude unpublished or revoked content.

## 16. Administrative Bulk Operations

Bulk jobs require:

- explicit job records;
- bounded batch size;
- progress checkpoints;
- idempotent item processing;
- pause/cancel behavior;
- per-item outcome reporting;
- retry limits;
- audit records.

A bulk failure must not leave the entire operation status ambiguous. Completed items remain completed, failed items remain identifiable, and safe replay is possible.

## 17. Deployment Failure Modes

| Failure | Safe behavior |
|---|---|
| New instance fails readiness | do not route traffic |
| Migration incompatible with old release | use expand-and-contract before rollout |
| Error rate rises after deployment | stop rollout and roll back application |
| Queue consumer regression | pause consumer and preserve messages |
| Feature causes incident | disable through approved operational flag |
| Configuration missing | fail startup for mandatory secrets/configuration |

Deployment automation must distinguish liveness from readiness. A process may be alive but not safe to receive traffic.

## 18. Recovery Time and Data Loss Expectations

Initial planning targets:

| Capability | Target recovery posture |
|---|---|
| Authentication and core API | restore as highest priority |
| PostgreSQL business data | minimal accepted data loss according to backup/replication design |
| Playback progress | idempotent replay from client queue where possible |
| Notifications | delayed delivery acceptable within category-specific window |
| Media derivatives | regenerable from immutable originals |
| Cache | disposable and reconstructable |
| Analytics projections | rebuildable from retained events/exports where supported |

Final RTO and RPO values must be approved before production launch and validated through recovery exercises.

## 19. Observability Requirements

Track at minimum:

- timeout rate by dependency;
- retry count and retry exhaustion;
- circuit-breaker state;
- thread and connection pool saturation;
- queue depth and message age;
- DLQ depth;
- outbox backlog and oldest row age;
- database lock/deadlock rate;
- cache hit/miss/failure rate;
- provider latency and failure classification;
- offline sync queue depth and rejected operations;
- media-processing duration and failure reason;
- deployment error-rate change.

Every alert must identify an owner, user impact, first diagnostic steps, and a runbook.

## 20. Testing Requirements

Resilience tests should include:

- dependency timeouts;
- connection refusal;
- delayed responses;
- duplicate and out-of-order messages;
- partial provider success;
- process restart during background work;
- Redis unavailability;
- RabbitMQ unavailability;
- database deadlocks and transaction retries;
- corrupted downloads;
- stale entitlement cache;
- deployment with mixed application versions;
- DLQ replay.

Testcontainers, WireMock, fault injection, controlled provider stubs, and mobile integration tests should be used where appropriate.

## 21. Incident Response Expectations

For each critical dependency, a runbook must define:

1. symptoms and alert names;
2. affected user journeys;
3. safe degraded mode;
4. immediate containment;
5. recovery procedure;
6. data reconciliation;
7. replay or cleanup steps;
8. exit criteria;
9. follow-up owner.

Manual data correction requires an auditable procedure and should prefer application-level repair commands or forward migrations over direct ad-hoc SQL.

## 22. Review Checklist

- Is the dependency criticality known?
- Is there an explicit timeout?
- Is retry safe and bounded?
- Is the operation idempotent?
- Is circuit breaking needed?
- Can one workload exhaust another?
- What happens when the dependency is unavailable?
- Does the fallback preserve security and data integrity?
- Are backlog and recovery observable?
- Has restart/replay behavior been tested?

## 23. Related Documents

- `Backend_Architecture.md`
- `Mobile_Architecture.md`
- `System_Flows.md`
- `Event_Catalog.md`
- `Error_Catalog.md`
- `Logging_Monitoring.md`
- `Performance_Guidelines.md`
- `C4_Model/05_Deployment_Diagram.md`
- `C4_Model/06_Runtime_Views.md`
- `C4_Model/12_Security_Control_Matrix.md`

## 24. Ownership and Maintenance

Architecture owns the resilience model. Each bounded context owns its dependency policies and recovery behavior. DevOps owns shared infrastructure recovery and production runbooks. This catalog must be updated whenever a new provider, data store, queue, worker class, deployment topology, or critical user journey is introduced.