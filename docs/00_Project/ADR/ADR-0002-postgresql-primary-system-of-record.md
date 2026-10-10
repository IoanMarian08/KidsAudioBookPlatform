# ADR-0002: Use PostgreSQL as the Primary System of Record

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture, Backend Engineering, DevOps

## Context

The platform contains strongly related data: parent accounts, child profiles, content metadata, publishing states, playback progress, subscriptions, entitlements, notification records, audit events, and administrative workflows. These capabilities require transactions, constraints, indexing, migration discipline, reliable recovery, and a clear source of truth.

The system also uses Redis for caching and short-lived coordination, RabbitMQ for asynchronous communication, and object storage for media. Without an explicit persistence authority, duplicated state could drift and security-sensitive decisions such as entitlement or profile ownership could become inconsistent.

## Decision

PostgreSQL is the authoritative persistent store for transactional and business data.

Redis may be used for cache, rate limiting, idempotency windows, short-lived coordination, and ephemeral session support. Object storage holds audio, illustrations, transcripts, and generated media assets. RabbitMQ transports events and commands. None of these systems is authoritative for durable business state.

When a state conflict exists, PostgreSQL wins unless another ADR explicitly defines a different authority for a narrowly scoped capability.

## Scope of Authority

PostgreSQL owns the durable truth for:

- accounts, credentials metadata, device sessions, and consent state;
- child profiles and parental settings;
- story, episode, version, publication, and moderation state;
- playback progress and completion state;
- subscriptions, provider purchase records, entitlements, and reconciliation history;
- notifications and delivery outcome records;
- upload intents and media metadata;
- feature-flag configuration and audit history;
- idempotency records where durable replay protection is required;
- transactional outbox and consumer inbox records;
- audit events and privacy-operation state.

Binary media remains in object storage. PostgreSQL stores only the object key, version, checksum, lifecycle status, ownership, and related metadata.

## Data Ownership

Each bounded context owns its tables, schema objects, migrations, and write paths.

Rules:

1. A microservice may read data owned by another service only through a versioned REST contract or an event-fed projection owned by the consumer.
2. Direct cross-service SQL reads and writes are forbidden.
3. Cross-service foreign keys, shared JPA entities and transactions are forbidden even when logical databases share one PostgreSQL cluster.
4. Shared reference data must have one explicit owner.
5. Reporting queries must not become hidden write-time dependencies.
6. A future service split/merge must preserve the authoritative writer until a controlled data migration completes.

## Identifier Strategy

- Externally exposed entities use UUIDs.
- Internal surrogate identifiers may be used only when they provide measurable operational value.
- Natural keys receive explicit unique constraints where business uniqueness matters.
- Identifiers are never reused after deletion.
- Public identifiers must not encode personal or sequential information.

## Integrity Rules

Database design must use:

- foreign keys where they protect authoritative relationships;
- check constraints for simple invariant enforcement;
- explicit unique constraints for natural uniqueness and idempotency;
- `NOT NULL` where absence is not a valid state;
- optimistic locking for concurrently editable aggregates;
- append-only records for purchase events, audit events, and other historical facts;
- UTC timestamps stored with unambiguous timezone semantics;
- monetary values represented with precise decimal or provider-minor-unit types;
- enumerations represented in a migration-safe form.

Application validation complements database constraints but does not replace integrity enforcement for critical invariants.

## Transaction Boundaries

A transaction must align with one business operation and one aggregate boundary whenever possible.

Rules:

- keep transactions short;
- never hold a database transaction open while calling an external provider;
- publish consistency-sensitive events through the transactional outbox;
- use idempotency keys for retry-prone writes;
- lock rows only when optimistic concurrency is insufficient;
- define deterministic lock ordering for multi-row updates;
- retry serialization or deadlock failures only when the operation is idempotent and bounded.

Distributed transactions across PostgreSQL, RabbitMQ, Redis, or object storage are not used. Cross-system consistency is achieved through outbox, reconciliation, and compensating workflows.

## Schema Organization

**Updated by [ADR-0015](ADR-0015-microservices-from-first-release.md):** initial deployment uses **a different logical PostgreSQL database, credential and migration history per microservice**. A PostgreSQL *cluster* can be shared to control cost, but business tables, SQL joins, foreign keys and transactions cannot be shared across services.

Recommended logical areas include:

```text
identity
profiles
catalog
playback
subscriptions
notifications
administration
media
platform
```

Schema boundaries must match documented bounded contexts and must not create a generic shared-data schema that bypasses ownership.

## Query and Indexing Policy

Indexes are created from documented access patterns, not speculation.

Required practices:

- inspect query plans for high-volume or latency-sensitive operations;
- index foreign keys used in joins and deletes;
- use composite indexes in the same order as dominant filters and sort patterns;
- use partial indexes for narrow lifecycle states where beneficial;
- avoid redundant indexes;
- monitor index size, write amplification, and unused indexes;
- paginate large result sets;
- prefer keyset pagination for large, ordered collections;
- prevent unbounded queries and accidental full-table scans in APIs.

PostgreSQL full-text search may support early product stages. A dedicated search platform is introduced only when relevance, scale, language analysis, or operational evidence justifies it.

## JSONB Policy

JSONB is allowed for flexible, peripheral metadata whose structure is not central to domain integrity.

JSONB must not be used to avoid modelling:

- account relationships;
- entitlements;
- publication state;
- ownership;
- security policy;
- payment or purchase records;
- query-critical fields.

Frequently queried JSONB attributes require explicit indexing and ownership. Stable fields should be promoted to typed columns.

## Migrations

Flyway manages all schema changes according to ADR-0012.

Applied versioned migrations are immutable. Destructive changes use expand-and-contract. Large backfills are operational jobs when they could block deployment.

Every migration must be validated against:

- a clean database;
- the oldest supported upgrade baseline;
- representative production-scale data where lock duration matters;
- application versions expected during rolling deployment.

## Backup and Recovery

Production requires:

- automated encrypted backups;
- point-in-time recovery where supported;
- documented retention;
- restore testing in an isolated environment;
- measured recovery time and recovery point objectives;
- ownership and escalation procedures for restore operations.

A backup is not considered reliable until restoration has been tested.

Initial objectives:

| Objective | Initial target |
|---|---|
| Recovery point objective | 15 minutes or better |
| Recovery time objective | 4 hours or better |
| Restore test cadence | At least quarterly |

Targets may be tightened as usage and business impact grow.

## High Availability and Scaling

The initial deployment uses a managed or operationally supported PostgreSQL setup with automated failover appropriate to the environment.

Scaling order:

1. optimize queries and indexes;
2. tune connection pools and transaction scope;
3. introduce caching for safe reconstructable reads;
4. use read replicas for suitable stale-tolerant workloads;
5. archive or partition high-volume history tables;
6. scale vertically where cost-effective;
7. consider service-specific databases or partitioning only with production evidence.

Read replicas must never become the source for operations requiring read-your-write consistency unless the lag contract explicitly permits it.

## Connection Management

- Application instances use bounded connection pools.
- Pool size is derived from database capacity, replica count, workload, and transaction duration.
- Connection acquisition timeouts are mandatory.
- Pool saturation is monitored.
- Health checks must not create excessive database traffic.
- Background jobs must not starve interactive API traffic.

## Security

- TLS is required for database connections outside trusted local development.
- Credentials are stored in a secrets manager or protected deployment secret mechanism.
- Application roles follow least privilege.
- Migration credentials are separate from runtime credentials where feasible.
- Production access is audited and time-bounded.
- Sensitive columns are minimized and protected according to the security architecture.
- Raw passwords, PINs, refresh tokens, and payment credentials are never stored.
- Support and analytics access must not expose unnecessary child-related information.

## Data Retention and Privacy

Each table containing personal, child-related, audit, notification, or purchase data must have a documented retention policy.

Deletion workflows must distinguish:

- immediate access revocation;
- soft deletion during a recovery or legal window;
- anonymization;
- hard deletion;
- legally required retention.

Account deletion is an auditable workflow spanning PostgreSQL, object storage, notifications, analytics projections, and backups according to policy.

## Failure Behavior

If PostgreSQL is unavailable:

- writes fail safely and are not acknowledged as successful;
- security-sensitive reads do not fall back to stale client or cache state unless explicitly allowed;
- cache misses do not invent authoritative data;
- asynchronous consumers retry with bounded backoff;
- circuit breakers and admission control protect the database during recovery;
- operators receive alerts based on availability, saturation, replication, and error thresholds.

Redis or RabbitMQ failure must not change PostgreSQL's authority.

## Observability

Required telemetry includes:

- connection-pool usage and wait time;
- query latency percentiles;
- transaction duration;
- lock waits and deadlocks;
- slow queries;
- replication lag;
- storage growth;
- cache hit and fallback effects on database load;
- migration duration and failures;
- backup and restore outcomes.

Metrics and logs must not include raw sensitive values.

## Testing and Validation

CI and release validation must include:

- migration from a clean database;
- migration from supported previous versions;
- repository integration tests with real PostgreSQL via Testcontainers;
- constraint and concurrency tests for critical invariants;
- transaction rollback tests;
- outbox atomicity tests;
- restore rehearsal before production launch;
- representative performance tests for critical queries.

## Consequences

### Positive

- Strong transactional guarantees.
- Mature tooling, indexing, backup, and recovery support.
- Good fit for relational catalog, identity, subscription, and audit data.
- Reduced risk of duplicated or inconsistent entitlement state.
- Clear durable authority across platform components.
- Supports independent service database ownership and migration from the first release.

### Negative

- Horizontal scaling requires deliberate design.
- Schema migrations must be coordinated with rolling deployments.
- A shared cluster can create noisy-neighbor risks.
- Strong governance is needed to prevent cross-service coupling, shared-database access and incompatible migrations.
- Large analytical workloads require a separate path.

## Alternatives Considered

### MongoDB as the primary database

Rejected because most core data is relational and benefits from explicit constraints, transactions, and predictable joins. Document storage may still be introduced for a specialized use case with its own ADR.

### Database per service from day one — now required

Distinct logical databases and scoped users are mandatory for each independently deployed service under [ADR-0015](ADR-0015-microservices-from-first-release.md). Shared PostgreSQL infrastructure is allowed, while cross-service database access is prohibited. The operational overhead of independently owned databases is included in the architecture cost model.

### Event store as the primary persistence model

Rejected because full event sourcing would add substantial complexity without a demonstrated requirement. Selected domains retain immutable history where it provides clear value.

### Redis as a primary data store

Rejected because cache eviction, persistence semantics, and operational behavior do not match durable business records.

### Object storage for structured business data

Rejected because it lacks the transactional, relational, and query guarantees required by the domain.

## Follow-up Actions

- Maintain schema ownership per bounded context.
- Enforce migration validation in CI.
- Test backup restoration before production launch and quarterly thereafter.
- Establish slow-query monitoring and index review.
- Define table-level retention and privacy ownership.
- Document connection-pool budgets for each environment.
- Introduce read replicas only when production evidence supports them.
- Review this ADR before service data transfer, sharding, or a second authoritative database is introduced.
