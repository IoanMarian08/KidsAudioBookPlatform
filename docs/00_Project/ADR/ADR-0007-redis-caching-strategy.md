# ADR-0007: Redis Caching Strategy

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture and Backend

## Context

The platform must serve catalog pages, story metadata, profile summaries, entitlement checks, and short-lived operational state with low latency. PostgreSQL remains the system of record, but not every read should hit the database.

## Decision

Use Redis as a non-authoritative cache and short-lived coordination store.

Primary use cases:

- published catalog and category snapshots;
- story and episode metadata;
- account entitlement summaries;
- rate-limiting counters;
- idempotency keys;
- short-lived parent-elevation state;
- distributed locks only where duplicate execution cannot otherwise be prevented;
- notification deduplication and temporary delivery state.

## Cache Rules

- Cache-aside is the default pattern.
- PostgreSQL is always authoritative.
- Cached values must be reconstructable.
- Every key has an explicit TTL unless documented otherwise.
- Key format: `<environment>:<bounded-context>:<entity>:<identifier>:<version>`.
- Use randomized TTL jitter for high-volume keys to reduce synchronized expiry.
- Invalidate or version keys after successful transactions; never invalidate before commit.
- Do not cache passwords, PIN hashes, raw refresh tokens, payment credentials, or full child-sensitive records.

## Suggested TTLs

| Data | TTL |
|---|---:|
| Published story metadata | 15 minutes |
| Category/collection pages | 5 minutes |
| Entitlement summary | 2 minutes |
| Parent elevation state | 5 minutes |
| Idempotency response | 24 hours |
| Rate-limit windows | Per policy |

## Failure Behavior

Redis failure must not make core authenticated reads unavailable when PostgreSQL can safely serve them. Rate limiting and idempotency require conservative fallback behavior. Cache failures are logged as operational events and measured separately from application failures.

## Consequences

### Positive

- Reduces database load and improves response time.
- Supports scalable counters and short-lived shared state.
- Keeps authoritative data in PostgreSQL.

### Negative

- Introduces invalidation complexity and eventual consistency windows.
- Requires memory sizing, eviction policy, and key-cardinality monitoring.

## Rejected Alternatives

- Redis as primary database: inappropriate for durable business records.
- Per-instance in-memory cache only: inconsistent across replicas and lost on restart.
- Caching every query: difficult to reason about and likely to produce stale or sensitive data exposure.
