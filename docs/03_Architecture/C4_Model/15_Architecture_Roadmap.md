# Architecture Roadmap — Microservices First

Version: 2.0
Status: Current target implementation plan; no production services are claimed
Owner: Architecture, Product and DevOps
Decision: [ADR-0015](../../00_Project/ADR/ADR-0015-microservices-from-first-release.md)

## 1. Purpose

KidsAudioBookPlatform will be built as **independently deployable Java 21/Spring Boot microservices from the beginning**. Every service owns its business capability, logical PostgreSQL database and credentials, Flyway migrations, API/event contracts, tracing, tests and release lifecycle. One PostgreSQL cluster may host distinct databases for cost efficiency; shared business tables, direct cross-service SQL and distributed transactions are forbidden.

There is **no initial monolith phase or later extraction milestone**. We may develop services sequentially, but each completed service remains a separate runnable artifact.

## 2. Phases and dependencies

~~~mermaid
flowchart LR
  F[Foundation: Gateway, CI, isolated DBs, RabbitMQ and tracing] --> I[identity + profiles services]
  I --> C[catalog + media services]
  C --> B[billing and entitlements service]
  B --> P[playback and offline service]
  P --> N[notifications + admin services]
  N --> R[Hardening and first production release]
  R --> E[Scale and safe product evolution]
~~~

## 3. Phase 0 — Platform foundation

Deliver:
- a repeatable Maven, Java 21 and container template for each service with independent builds and SBOMs;
- API Gateway routing, public TLS, downstream service security, correlation IDs and per-service liveness/readiness;
- PostgreSQL distinct logical databases, service users, migrations and restore procedures;
- RabbitMQ event contracts with producer outboxes and consumer inbox/idempotency;
- per-service observability, deadline and retry configuration;
- Docker Compose for multiple independently running services and dependencies;
- CI builds, contract checks, container scans and per-service staged rollout plans.

**Exit gate:** start, stop, deploy and roll back two independently built services. Prove cross-database access is denied, call across REST contracts, propagate a trace and safely replay an event.

## 4. Phase 1 — Identity and profiles

Deliver identity-service (registration, token rotation, account security and Parent Zone elevation) and profiles-service (child profiles, ownership, parental restrictions). Each has its own database.

**Exit gate:** expired proof, token replay, profile IDOR and service identity tests pass.

## 5. Phase 2 — Catalog and media

Deliver catalog-service (stories, publication, age/locale filters and editorial state) and media-service (controlled uploads, scanning, transcoding and signed CDN grants), with media-owned workers.

**Exit gate:** suspended/unreviewed content cannot be played, a scanned asset can publish and a service cannot access another service's DB.

## 6. Phase 3 — Billing

Deliver billing-service (store verification, subscription lifecycle, trials according to product approval and authoritative entitlements) with provider reconciliation workers.

**Exit gate:** forged, duplicate, expired, refunded or out-of-order provider updates do not grant false Premium rights.

## 7. Phase 4 — Playback and offline

Deliver playback-service (authorized playback sessions, progress/favorites/history, downloads and offline sync). It calls profiles, catalog, billing and media through versioned REST contracts and processes asynchronous events safely.

**Exit gate:** multi-service playback grant, offline conflicting progress, content takedown, expiry and remote timeout tests pass.

## 8. Phase 5 — Notifications, admin and privacy

Deliver notifications-service and admin-service, each with own database, plus durable account deletion saga with per-service acknowledgements, role-scoped support and protected parent communication.

**Exit gate:** notifications outage does not block playback, privileged writes are audited and deletion is not falsely marked complete before all required services finish.

## 9. Phase 6 — Release and evolution

Release requires per-service SLOs, tracing, error budgets, alarms, independently tested deploy/rollback, producer/consumer compatibility, service DB backup/restore, distributed security/IDOR tests, store and child privacy reviews, capacity costs, and product acceptance.

Optional advertising-policy-service stays disabled pending product/legal/security/store approval. Do not make it a critical playback dependency.

After release, add new services only for justified cohesive boundaries with an ADR; service splits/merges use versioned contracts and database migration with safe compatibility windows.

## 10. Risks and controls

| Risk | Control |
|---|---|
| Chatty REST calls / cascading failure | Bounded deadlines, circuit breakers, bulkheads and event-fed safe read models |
| Eventual consistency | Local ACID, outbox/inbox, idempotent sagas, reconciliation |
| Complex CI/operations | Service templates, independent pipelines, one tracing convention |
| Cost of many deployables | Measure per-service footprint; share only infrastructure, not business DB ownership |
| Child data / Premium leaks | Downstream ownership checks, fail-closed authority and audit |
| Database migration coupling | Expand/contract and consumer/provider compatibility across independent releases |

Related: [Microservices Architecture](../Microservices_Architecture.md), [Contracts](../Microservices_Contracts_and_Flows.md), [Implementation Roadmap](../Implementation_Roadmap.md), [CI/CD](../../05_DevOps/CI_CD.md).
