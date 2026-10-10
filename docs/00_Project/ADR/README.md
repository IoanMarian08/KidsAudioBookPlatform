# Architecture Decision Records

Version: 2.0
Status: Active
Owner: Platform Architecture
Last updated: 2026-10-10

## Purpose

This directory contains the **current architectural decisions** for KidsAudioBookPlatform. The backend is composed of independently deployable Java 21/Spring Boot microservices **from the first release**. Each service owns its logical database, migrations, credentials, APIs, event contracts, security and lifecycle.

**Start with [ADR-0015: Microservices from the First Release](ADR-0015-microservices-from-first-release.md).** It establishes the runtime and data ownership baseline. Use [Microservices Architecture](../../03_Architecture/Microservices_Architecture.md) and [Service Contracts](../../03_Architecture/Microservices_Contracts_and_Flows.md) when implementing services.

## Active ADRs

| ADR | Accepted decision |
|---|---|
| [ADR-0015](ADR-0015-microservices-from-first-release.md) | Independent microservices from the first release, with per-service database ownership |
| [ADR-0002](ADR-0002-postgresql-primary-system-of-record.md) | PostgreSQL as the durable system of record, isolated logical databases per service |
| [ADR-0003](ADR-0003-rest-and-rabbitmq-communication.md) | REST/OpenAPI for synchronous contracts, RabbitMQ for asynchronous events |
| [ADR-0004](ADR-0004-flutter-mobile-platform.md) | Flutter for mobile clients |
| [ADR-0005](ADR-0005-jwt-refresh-token-strategy.md) | JWT access tokens and rotating refresh credentials |
| [ADR-0006](ADR-0006-parent-zone-security.md) | Adult verification for the protected Parent Zone |
| [ADR-0007](ADR-0007-redis-caching-strategy.md) | Redis for reconstructible caching and coordination |
| [ADR-0008](ADR-0008-object-storage-and-cdn.md) | Private object storage and signed CDN media delivery |
| [ADR-0009](ADR-0009-observability-stack.md) | Distributed logging, metrics and tracing |
| [ADR-0010](ADR-0010-testing-strategy.md) | Layered automated and cross-service testing |
| [ADR-0011](ADR-0011-feature-flags.md) | Controlled, auditable feature flags |
| [ADR-0012](ADR-0012-flyway-database-migrations.md) | Service-owned Flyway migration history |
| [ADR-0013](ADR-0013-versioning-strategy.md) | Versioned APIs, events, content and releases |
| [ADR-0014](ADR-0014-offline-synchronization.md) | Idempotent offline synchronization with server authority |

## Mandatory microservice standards

Each independently deployed service has its own Spring Boot artifact, OCI image, CI checks, logical PostgreSQL database, credentials, migrations, recovery procedures, REST/events contracts, access control, observability and release lifecycle.

The API Gateway routes requests, while owning services enforce user identity, object ownership and elevated Parent Zone rights. RabbitMQ producers use transactional outbox and consumers use idempotent inbox/deduplication. A shared physical PostgreSQL cluster may contain multiple **isolated logical databases**; direct cross-service SQL, shared JPA entities, foreign keys and distributed transactions are prohibited.

## ADR workflow

Create a new ADR for a major change to service ownership, data authority, authentication, protocols, external providers, retention, scalability, reliability, cost or privacy. Use file names of the form ADR-XXXX-kebab-case-title.md and allocate the next available identifier.

Each proposal records context, constraints, options, approved choice, consequences, service ownership, data/contracts affected, rollout and rollback, failure modes, acceptance tests and review decision.

A proposal is Proposed until approved. Accepted decisions are reflected in C4 views, API/event contracts, database design, implementation roadmap and relevant automated tests. Significant decisions retain traceability in Git history; the active documentation contains the applicable architecture.

## Review checklist

- [ ] Child and parent safety controls remain enforced by the owning service.
- [ ] Business data and database ownership are explicit and isolated.
- [ ] Service-to-service identity and authorization are verified.
- [ ] REST/event schemas have compatibility tests.
- [ ] Remote failures, idempotency and reconciliation are defined.
- [ ] Each deployable has metrics, traces, recovery and rollback plans.
- [ ] Related docs and local links are updated.

Related: [Architecture Principles](../../03_Architecture/Architecture_Principles.md), [Database Design](../../03_Architecture/Database_Design.md), [Testing Strategy](../../06_Testing/Testing_Strategy.md), [CI/CD](../../05_DevOps/CI_CD.md).
