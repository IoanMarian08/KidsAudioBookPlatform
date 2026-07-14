# ADR-0002: Use PostgreSQL as the Primary System of Record

Status: Accepted
Date: 2026-07-14

## Context

The platform contains strongly related data: parent accounts, child profiles, content metadata, publishing states, playback progress, subscriptions, entitlements, notification records, audit events, and administrative workflows. These capabilities require transactions, constraints, indexing, migration discipline, and reliable recovery.

## Decision

PostgreSQL will be the authoritative persistent store for transactional and business data. Redis may be used for cache, rate limiting, short-lived coordination, and ephemeral session support. Object storage will hold audio, illustrations, transcripts, and generated media assets. Neither Redis nor object storage is authoritative for business state.

Database design must follow these rules:

- UUID identifiers for externally exposed entities;
- foreign keys and check constraints where they protect business integrity;
- explicit unique constraints for idempotency and natural uniqueness;
- Flyway-managed migrations;
- UTC timestamps;
- optimistic locking for concurrently editable aggregates;
- append-only records for purchase events, audit events, and other historical facts;
- indexes designed from real query patterns;
- JSONB used only for flexible peripheral metadata, not as a substitute for domain modelling.

## Consequences

### Positive

- Strong transactional guarantees.
- Mature tooling, indexing, backup, and recovery support.
- Good fit for relational catalog and subscription data.
- Reduced risk of duplicated or inconsistent entitlement state.
- Support for full-text search during early product stages.

### Negative

- Horizontal scaling requires deliberate design.
- Schema migrations must be carefully coordinated.
- Large analytical workloads should not run directly on the transactional database.

## Alternatives Considered

### MongoDB as the primary database

Rejected because most core data is relational and benefits from explicit constraints and transactions. Document storage could still be introduced for a future specialized use case.

### Database per module from day one

Rejected for the initial modular monolith because it increases local and operational complexity. Logical ownership will be expressed through schemas and access rules, preserving a later extraction path.

### Event store as the primary persistence model

Rejected because full event sourcing would add substantial complexity without a demonstrated requirement. Selected domains will retain immutable history where it provides clear value.

## Follow-up Actions

- Define schema ownership per bounded context.
- Add migration validation to CI.
- Test backup restoration before production launch.
- Establish slow-query monitoring and index review.
- Introduce read replicas only when production evidence supports them.
