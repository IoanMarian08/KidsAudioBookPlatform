# ADR-0007: Redis Caching Strategy

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture, Backend, DevOps
- **Review cadence:** At least annually and after any cache-related availability or consistency incident

## Context

The platform must serve catalog pages, story metadata, profile summaries, entitlement checks, parent-elevation state, idempotency records, and short-lived operational data with low latency. PostgreSQL remains the system of record, but not every read should hit the database and some coordination use cases require fast shared state across application replicas.

Redis can reduce database pressure and support distributed counters, deduplication, short-lived session state, and operational coordination. At the same time, stale or incorrectly scoped cached data can expose premium content, leak account data, bypass security checks, or cause inconsistent user experience.

The strategy therefore needs explicit ownership, key design, TTL policy, invalidation rules, failure behavior, memory management, security constraints, and observability.

## Decision

Use Redis as a non-authoritative cache and short-lived coordination store.

PostgreSQL remains authoritative for durable business data. Redis data must be reconstructable, bounded in lifetime or size, and safe to lose unless a specific use case documents stronger guarantees.

Primary use cases:

- published catalog and category snapshots;
- story and episode metadata;
- account entitlement summaries;
- rate-limiting counters;
- idempotency keys and short-lived responses;
- parent-elevation state;
- notification deduplication;
- temporary delivery state;
- short-lived distributed coordination;
- cache-invalidation fan-out metadata;
- selected read models where staleness is explicitly acceptable.

Redis is not used as the primary store for accounts, child profiles, purchases, subscriptions, story publication state, playback progress, audit history, or other durable business records.

## Principles

1. PostgreSQL is authoritative.
2. Cached values must be reconstructable.
3. Every key has an owner.
4. Every key has an explicit TTL or bounded lifecycle.
5. Cache behavior must fail safely.
6. Security-sensitive state uses conservative defaults.
7. Cache invalidation occurs only after the authoritative transaction commits.
8. Key cardinality and payload size must be observable.
9. Redis outages must not silently change authorization semantics.
10. Cache use must reduce measurable load or latency rather than add complexity without evidence.

## Cache Patterns

### Cache-Aside

Cache-aside is the default pattern.

1. Read from Redis.
2. On hit, validate the cached envelope and return the value.
3. On miss, read from PostgreSQL or the authoritative provider.
4. Store the result with TTL and version metadata.
5. Return the authoritative result.

This pattern is used for catalog, story metadata, category snapshots, and similar read-heavy data.

### Write-Through

Write-through is not the default. It may be used only when the application can update PostgreSQL and Redis consistently without making Redis authoritative.

### Write-Behind

Write-behind is rejected for durable business writes because loss or delay could create data inconsistency.

### Read-Through Framework Abstraction

Framework-level caching may wrap cache-aside behavior, but key generation, TTL, serialization, error handling, and metrics must remain explicit and testable.

## Key Naming

Canonical format:

```text
<environment>:<bounded-context>:<purpose>:<identifier>:<schema-version>
```

Examples:

```text
prod:catalog:story:story-uuid:v2
prod:catalog:collection:bedtime:ro-RO:v3
prod:subscriptions:entitlement:account-uuid:v1
prod:security:parent-elevation:session-uuid:v1
prod:api:idempotency:account-uuid:key-hash:v1
```

Rules:

- use lowercase names;
- use stable bounded-context and purpose segments;
- include environment separation;
- include schema or payload version when format changes are possible;
- hash user-provided or excessively long key parts;
- do not include emails, names, raw tokens, PINs, purchase receipts, or other sensitive values;
- avoid unbounded timestamp or random suffixes unless the lifecycle is strictly controlled;
- document all high-cardinality key families.

## Value Envelope

Where useful, cached objects include metadata:

```json
{
  "schemaVersion": 2,
  "cachedAt": "2026-07-15T10:00:00Z",
  "sourceVersion": "story-version-uuid",
  "expiresAt": "2026-07-15T10:15:00Z",
  "payload": {}
}
```

Clients of the cache reject unsupported schema versions and rebuild the value from the authoritative source.

## Serialization

- Use a stable, explicit serialization format.
- Avoid native Java object serialization.
- Include schema version for evolving payloads.
- Keep payloads small and purpose-specific.
- Compress only when measurement shows a benefit and CPU cost is acceptable.
- Serialization failure behaves as a cache miss.
- Deserialization errors are measured and the invalid key is removed or allowed to expire safely.

## TTL Policy

Suggested defaults:

| Data | Default TTL | Staleness tolerance |
|---|---:|---|
| Published story metadata | 15 minutes | Moderate |
| Category and collection pages | 5 minutes | Moderate |
| Search suggestions | 5 minutes | Moderate |
| Entitlement summary | 2 minutes | Low |
| Parent elevation state | 5 minutes maximum | Very low |
| Idempotency response | 24 hours | Exact within retention window |
| Notification deduplication | 24–72 hours | Exact within deduplication window |
| Rate-limit windows | Per policy | Exact within window |
| Negative catalog lookup | 30–60 seconds | Low |
| Feature-flag evaluation | 30–120 seconds | Depends on flag category |

Rules:

- TTLs are configuration with bounded approved ranges.
- Add randomized jitter to high-volume key families to reduce synchronized expiry.
- Security and entitlement data use shorter TTLs.
- Operational kill switches require explicit invalidation or very short TTLs.
- Negative caching must be short-lived to avoid hiding newly created resources.
- No durable business data uses an infinite TTL.

## Invalidation Strategy

### Transactional Rule

Never invalidate or populate a cache before the authoritative database transaction commits.

### Direct Invalidation

After commit, the owning bounded context invalidates or replaces affected keys.

### Event-Driven Invalidation

Domain events may trigger invalidation in other bounded contexts or projections. Consumers must be idempotent.

### Versioned Keys

For broad snapshots or schema changes, increment a logical version segment and allow old keys to expire naturally.

### Administrative Changes

Publishing, unpublishing, entitlement revocation, account disablement, and security-policy changes require immediate or near-immediate invalidation according to risk.

### Invalidation Failure

If invalidation fails:

- record a metric and structured event;
- retry with bounded backoff where appropriate;
- rely on short TTL for security-sensitive data;
- provide an operator-triggered purge path;
- never assume invalidation succeeded without confirmation for critical flows.

## Cache Stampede Protection

Use one or more of:

- TTL jitter;
- request coalescing;
- single-flight loading per key;
- short-lived rebuild locks;
- stale-while-revalidate for non-sensitive public catalog data;
- pre-warming for known high-traffic releases.

A distributed lock must have a short lease and safe timeout. Failure to acquire a rebuild lock should not block indefinitely.

## Distributed Locks

Distributed locks are allowed only when duplicate execution cannot be prevented more safely through database constraints, idempotency keys, queue partitioning, or transactional ownership.

Rules:

- define the protected resource;
- use a unique lock token;
- set a bounded lease;
- release only when the stored token matches;
- account for process pauses and lease expiry;
- avoid using locks as a substitute for correct database transactions;
- record contention, timeout, and lease-expiry metrics.

For high-risk operations, fencing tokens or database-level coordination are preferred over a simple Redis lock.

## Idempotency

Redis may store short-lived idempotency state for API requests.

Each record includes:

- account or caller scope;
- idempotency-key hash;
- request fingerprint;
- processing state;
- response status and body reference where safe;
- creation and expiry timestamps.

Rules:

- the same key with a different request fingerprint is rejected;
- an in-progress request returns a stable processing response;
- durable side effects still rely on database transactions and uniqueness constraints;
- critical idempotency requirements must survive Redis loss through database support where needed.

## Rate Limiting

Redis supports shared counters for authentication, API, upload, notification, and abuse-prevention limits.

- algorithms may use fixed window, sliding window, token bucket, or leaky bucket;
- policies are scoped by account, IP, device, endpoint, or provider as appropriate;
- atomic Lua scripts or equivalent server-side operations are used where multiple commands must be consistent;
- rate-limit keys have explicit expiry;
- responses include stable error codes and `Retry-After` where appropriate;
- Redis outage behavior is defined per endpoint risk.

High-risk authentication and recovery endpoints fail conservatively if distributed rate-limit state is unavailable.

## Entitlement Caching

Entitlement summaries may be cached briefly, but subscription and content authorization remain server authoritative.

- cache keys are account-scoped;
- payloads include source version or last reconciliation time;
- revocation events trigger immediate invalidation;
- uncertain or missing state fails closed for premium-only authorization;
- cached entitlement must not extend beyond approved offline or grace policy;
- client-visible cache headers do not expose reusable entitlement proofs.

## Parent Elevation State

Parent-elevation state is short-lived and security-sensitive.

- TTL must not exceed the elevation credential lifetime;
- session revocation invalidates elevation;
- PIN reset and password recovery invalidate elevation;
- Redis outage causes parent-only operations to fail closed unless another authoritative session store is available;
- elevation keys contain identifiers, assurance metadata, and timestamps, never the PIN.

## Notification Deduplication

Redis may suppress duplicate notification delivery attempts within a bounded window.

- the deduplication key is derived from notification ID, recipient scope, and channel;
- TTL matches the maximum retry horizon;
- durable notification state remains in PostgreSQL;
- Redis loss may cause duplicate attempts, so downstream delivery and persistence must also be idempotent.

## Failure Behavior

### Cache Read Failure

For reconstructable low-risk data, bypass Redis and query PostgreSQL. Record the cache failure separately from the application result.

### Cache Write Failure

Return the authoritative result when safe. Do not fail the user request solely because optional cache population failed.

### Security State Failure

Rate limiting, parent elevation, idempotency, and entitlement authorization use conservative fallback behavior. The endpoint may fail closed rather than bypass security.

### Total Redis Outage

- public and authenticated catalog reads fall back to PostgreSQL with protective load shedding;
- optional cache population is disabled temporarily;
- security-sensitive shared state fails according to documented policy;
- background rebuild jobs pause or reduce concurrency;
- operators receive alerts;
- recovery avoids an immediate cache stampede.

### Partial Timeout or High Latency

Use strict timeouts, bounded connection pools, circuit breakers where appropriate, and fallback paths. Redis calls must not consume the full API latency budget.

## Memory and Eviction

- choose an eviction policy aligned with the workload;
- reserve memory headroom;
- set maximum payload sizes;
- monitor memory fragmentation;
- monitor key count and average payload size by family;
- prevent unbounded cardinality;
- separate critical security state from expendable cache data through logical or physical isolation when scale requires it;
- avoid relying on eviction for lifecycle management of critical coordination records.

If one Redis deployment hosts multiple use cases, key families and memory budgets must be explicitly allocated.

## Topology and Availability

Initial environments may use a single Redis instance for simplicity. Production must evaluate:

- managed Redis or equivalent service;
- replication and automatic failover;
- persistence settings for operational recovery;
- availability-zone placement;
- TLS support;
- maintenance and upgrade behavior;
- backup requirements for non-reconstructable short-lived state;
- separate clusters for cache and critical coordination as scale grows.

Redis persistence does not make Redis the system of record.

## Security

- require TLS in non-local environments;
- authenticate clients;
- use least-privilege ACLs where supported;
- isolate networks and deny public access;
- rotate credentials;
- do not run dangerous administrative commands from application identities;
- do not store passwords, PIN hashes, raw refresh tokens, payment credentials, personal child data, or full purchase receipts;
- avoid sensitive identifiers in key names;
- redact Redis connection strings and commands from logs;
- audit administrative access and purge operations.

## Observability

Track at minimum:

- hit and miss rate by key family;
- command latency percentiles;
- connection-pool saturation;
- timeout and error rate;
- memory usage and fragmentation;
- eviction count;
- expired key rate;
- key count and cardinality growth;
- average and maximum payload size;
- invalidation success and failure;
- cache rebuild duration;
- lock contention and lease expiry;
- idempotency conflicts;
- rate-limit decisions;
- fallback database load during Redis degradation.

Do not use unbounded labels such as raw key names or account IDs in metrics.

## Alerting

Alerts should include:

- sustained Redis unavailability;
- high command latency;
- connection-pool exhaustion;
- memory above approved threshold;
- unexpected eviction growth;
- replication or failover problems;
- abnormal key-cardinality growth;
- invalidation backlog;
- fallback database saturation;
- parent-elevation or rate-limit dependency failures.

Alerts must link to a runbook and describe user impact.

## Testing Requirements

Automated tests must cover:

- cache hit and miss behavior;
- TTL and jitter bounds;
- serialization compatibility;
- invalidation after successful commit;
- no invalidation before rollback;
- stale-value handling;
- Redis timeout and outage fallback;
- entitlement fail-closed behavior;
- parent-elevation expiry;
- idempotency conflict and replay;
- rate-limit atomicity;
- distributed-lock lease and token ownership;
- stampede protection;
- malformed or incompatible cached payloads;
- key-name privacy rules;
- metrics without high-cardinality labels.

Integration tests use a real Redis instance through Testcontainers or an equivalent environment rather than relying only on mocks.

## Operational Runbook Expectations

The Redis runbook must document:

- diagnosing latency and memory pressure;
- failover and recovery;
- disabling optional cache use;
- purging one key family safely;
- recovering from malformed values;
- preventing cache stampede after restart;
- handling invalidation backlog;
- rotating credentials;
- investigating unexpected cardinality growth;
- separating or migrating critical key families.

## Capacity Planning

For every major key family, estimate:

- expected object count;
- average and maximum payload size;
- TTL;
- write and read rate;
- peak concurrency;
- replication overhead;
- growth factor;
- acceptable miss rate;
- rebuild cost.

Capacity reviews are required before major catalog expansion, large marketing campaigns, or changes that introduce high-cardinality state.

## Consequences

### Positive

- Reduces PostgreSQL load and improves response latency.
- Supports scalable counters, deduplication, and shared short-lived state.
- Keeps durable authority in PostgreSQL.
- Explicit TTL and invalidation rules reduce accidental staleness.
- Conservative fallback protects security-sensitive flows.

### Negative

- Introduces invalidation complexity and eventual-consistency windows.
- Requires memory sizing, eviction policy, failover, and cardinality monitoring.
- Security-sensitive use cases need stricter outage behavior than ordinary caching.
- Additional serialization, testing, and operational tooling are required.

## Rejected Alternatives

- **Redis as the primary database:** inappropriate for durable business records.
- **Per-instance in-memory cache only:** inconsistent across replicas and lost on restart.
- **Caching every query:** difficult to reason about and likely to create stale or sensitive data exposure.
- **Infinite TTLs for business objects:** creates uncontrolled staleness and migration risk.
- **Write-behind for durable mutations:** risks data loss and ordering problems.
- **Distributed locks for all concurrency:** adds fragility where database constraints or idempotency are safer.
- **Silent fail-open for security state:** unacceptable for entitlement, elevation, and abuse-prevention controls.

## Follow-up Actions

- Define cache key families and ownership in backend documentation.
- Add Redis entities and data classification to `Database_Design.md` or the relevant storage section.
- Add cache, rate-limit, and idempotency flows to `System_Flows.md`.
- Add Redis metrics, alerts, and runbooks to `Logging_Monitoring.md`.
- Add failure-mode tests to the integration-test suite.
- Review whether cache and critical coordination require separate Redis deployments before production scale.

## Decision Compliance

A change is compliant with this ADR only when Redis remains non-authoritative, values are reconstructable or explicitly classified, TTL and ownership are defined, invalidation follows committed writes, sensitive data is excluded, outage behavior is documented, and operational metrics cover latency, memory, errors, evictions, and cardinality.