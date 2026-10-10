# ADR-0015: Adopt Microservices from the First Release

- **Status:** Accepted
- **Decision date:** 2026-10-10
- **Decision owner:** Product owner (explicit architectural direction)
- **Architecture impact:** Supersedes [ADR-0001: Start with a Modular Monolith](ADR-0001-modular-monolith-first.md).
- **Historical context:** [ADR-002](ADR-002.md) proposed microservices in an early draft but was later superseded. This new ADR is the canonical decision, not a reactivation of the legacy document.

## 1. Context

The previous baseline optimized for an initial modular monolith and deferred service extraction. The product owner has now explicitly decided that **KidsAudioBookPlatform must be based on microservices from the beginning**, not on a monolith. We must change the runtime architecture and delivery plan consistently while retaining the existing product contracts, security constraints and technology choices.

This is an intentional trade-off: independent deployment and data ownership are preferred even though they increase infrastructure, testing, observability, failure-handling and local development complexity.

## 2. Decision

**The first implemented backend release will consist of independently buildable, deployable and observable Java 21/Spring Boot services aligned with bounded contexts.** No deployable application may contain the entire platform's unrelated business capabilities. An API gateway is the public entry point; it is not a single backend implementation of all domain logic.

A service must:
1. Have its own executable artifact, runtime configuration, CI/deployment unit, version, health checks and resource limits.
2. Own its domain and persistence. **No cross-service repository/JPA access and no direct SQL access to another service's database.**
3. Expose documented REST/OpenAPI contracts for synchronous queries/commands and versioned RabbitMQ events for asynchronous integration.
4. Manage its own transactional outbox and consumer idempotency/inbox state when producing or consuming integration events.
5. Handle remote failure explicitly through timeouts, bounded retries, circuit breakers/bulkheads where appropriate, and safe degraded paths.
6. Emit structured logs, correlation/trace IDs, metrics and security audit signals.
7. Enforce authentication, authorization and ownership at its own server-side boundary, not solely at the gateway.

**Data ownership:** one logical PostgreSQL database per service with distinct credentials and migrations. Multiple databases **may share a PostgreSQL server/managed cluster for MVP cost efficiency**, but privileges and ownership remain isolated. A shared cluster does not permit SQL joins, foreign keys or transactions across services. Redis, RabbitMQ, object storage and observability are shared infrastructure with isolated namespaces/permissions as needed; none is a shared business database.

## 3. Initial deployable services

| Runtime | Owner / responsibilities | Data and API/event contracts |
|---|---|---|
| api-gateway | TLS routing, edge rate limiting, request correlation and security policy at the edge | No business database; routes to services. Token checks are repeated by downstream services. |
| identity-service | Adult authentication, refresh/session rotation, authorization primitives, Parent Zone challenge and scoped proof | Identity database. Owns account/session credentials and parent security. |
| profiles-service | Child profiles, age band, family preferences and parental content settings | Profiles database. Validates owner/elevated scope independently. |
| catalog-service | Stories, episodes, series, categories, localizations, publication and editorial metadata | Catalog database. Owns published content state and search/filter. |
| media-service | Private uploads, media scanning/transcoding coordination, renditions, manifests and signed delivery grants | Media database + private object storage. Workers may be **separate deployments** of this service. |
| playback-service | Streaming authorization orchestration, listening sessions, progress, favorites, history and offline sync/download registrations | Playback database. Consults catalog, profiles, media and entitlements through explicit contracts. |
| billing-service | Store purchase verification, plan configuration, trials, subscription lifecycle and authoritative entitlements | Billing database. Emits entitlement changes, owns provider reconciliation workers. |
| notifications-service | Parent notification inbox, preferences, device registration, approved templates and provider delivery | Notifications database. Consumes versioned events; provider delivery workers may deploy separately. |
| admin-service | Restricted support/admin-facing orchestration, approval audit and moderation permissions | Admin/audit database. **Catalog remains owner of publication records**; admin-service invokes catalog contracts rather than modifying catalog tables. |
| advertising-policy-service | Server-side free-tier ad eligibility/counters and audit | **Optional and feature-gated**, deployed only after child-safety/legal/store sign-off; never required for core playback. |

This is the **logical MVP boundary map**. Related bounded contexts can be composed *within their owning service* (e.g., Parent Zone inside identity-service, entitlements inside billing-service). Do not split into one deployment per entity, table or endpoint. If service consolidation/splitting is proposed later, an ADR must approve the change.

## 4. Communication and consistency

- **Public traffic:** Flutter / React admin → HTTPS gateway → owning service. Use a BFF only for a proven client-specific aggregation need, as a separate deployable without business-data ownership.
- **Synchronous:** REST/JSON over protected service-to-service networking, with contract versioning, propagated authenticated identity where applicable, least-privilege service credentials, explicit timeout budgets and bounded resilience policies.
- **Asynchronous:** RabbitMQ domain/integration events with schema version, correlation/causation IDs, producer-owned outbox and consumer-owned inbox/deduplication. At-least-once delivery is assumed; event order is per aggregate, not global.
- **Consistency:** local ACID inside each service's database; **no cross-service ACID/2PC**. Use event-driven projections, a saga/process manager with compensations where multi-service workflows require coordination, and explicit reconciliation for provider/child-safety critical states.
- **High-risk authorization:** Profile ownership, account locks, entitlements, content takedowns and Parent Zone proof must fail closed when validation cannot be established. Redis cache alone must never become the source of truth.
- **Media delivery:** CDN/object storage serves bytes; API applications authorize and issue expiring grants rather than proxying whole audio files.
- **Privacy:** Cross-service data deletion/export is a durable orchestrated process with owned handlers, idempotent acknowledgements and auditable completion; partial completion is observable.

## 5. Databases, schema migration and backups

Each service manages an isolated database, migration history and least-privileged DB user. A deployment can share the infrastructure PostgreSQL instance but must preserve logical service boundaries. Cross-service references use opaque IDs and explicit checks, never cross-database foreign keys. Read models belong to the consuming service and are refreshed via events or versioned APIs.

Data migration and rollback are independently staged and contract-compatible. Backups, restoration and retention must specify **per-database** targets, coordinated recovery order and idempotent message replay.

## 6. Repository and deployment approach

The repository may remain a **monorepo**, but it must contain **separately built/deployed microservices**; monorepo does not mean monolith. CI tests only affected services plus cross-service contracts and global security gates. A container orchestration/deployment platform is required for staging/production; provider and Kubernetes-vs-managed-containers are **not yet decided**. Docker Compose can run local service containers.

Suggested code boundaries are documented in [Microservices Architecture](../../03_Architecture/Microservices_Architecture.md) and [Service Contracts](../../03_Architecture/Microservices_Contracts_and_Flows.md).

## 7. Consequences and accepted costs

Benefits: independent scaling/deployment, isolation, owner-aligned data, better deployability of media/billing/notification workloads. Costs: additional operational complexity, network partial failures, eventual consistency, independent schema contracts, more staging resource usage, complex debugging and data deletion.

Mitigations: small **cohesive** service set, shared deployment/CI templates (not shared business model), standard OpenAPI/event schemas, container-based integration tests, distributed tracing, local Compose, service-level SLOs, clear runbooks, minimum privilege and cost budgets.

## 8. Alternatives reconsidered

- **Modular monolith:** operationally simpler; rejected for the first release by explicit product-owner decision. Historical decision retained in ADR-0001 as superseded.
- **One service per table/domain noun:** rejected as excessive fragmentation.
- **Direct synchronous calls for everything:** rejected because failure amplification/coupling would be unacceptable; events are required for noninteractive propagation.
- **Shared transactional database across services:** rejected because it destroys independent ownership.
- **Microservices with public direct exposure:** rejected; edge gateway and private networking remain required.

## 9. Rollout and acceptance criteria

No claim of implementation is made by accepting this ADR. It becomes an engineering release gate:

1. Independently start/stop/deploy each core service and verify unaffected services degrade safely.
2. Prove DB user separation; cross-service SQL access is forbidden and testable.
3. Publish OpenAPI contracts and versioned event schemas for service boundaries, with compatibility tests.
4. Demonstrate request tracing across gateway and at least two services, and event trace correlation.
5. Test retries/duplicates, out-of-order events, deadline exhaustion, circuit breaking and DLQ/replay.
6. Exercise purchase verification/entitlement revocation and content suspension with safe consistency behavior.
7. Run per-service integration tests plus critical end-to-end parent/child journeys.
8. Validate operational on-call, secrets, backup/restore and independent deployment/rollback.

Related: [Software Architecture](../../03_Architecture/Software_Architecture.md), [Backend Architecture](../../03_Architecture/Backend_Architecture.md), [Database Design](../../03_Architecture/Database_Design.md), [Infrastructure](../../05_DevOps/Infrastructure.md), [Implementation Roadmap](../../03_Architecture/Implementation_Roadmap.md).
