# Implementation Blueprints

Version: 1.0  
Status: Design blueprints — implementation pending  
Owner: Backend, Mobile, Architecture and QA

## Purpose

These documents bridge **product intentions** and **implementable module tasks**. They do not replace approved ADRs, API Specification, Event Catalog, Database Design or Security Architecture. Where a blueprint is more specific than a normative contract, the contract takes precedence until an approved decision updates it.

## Build order

| Order | Blueprint | Depends on | Evidence to close |
|---|---|---|---|
| 1 | [Identity and Parent Zone](01_Identity_Parent_Zone.md) | Platform auth, PostgreSQL | Registration, session rotation, IDOR and parent-elevation tests |
| 2 | [Catalog and Media](02_Catalog_Media.md) | Identity, content/admin roles, object storage | Review/publish, signed upload and takedown tests |
| 3 | [Playback and Offline](03_Playback_Offline.md) | Profiles, Catalog, Media, Entitlements | Stream authorization, progress conflict and offline grant tests |
| 4 | [Subscriptions and Entitlements](04_Subscriptions_Entitlements.md) | Identity, store sandbox adapters | Verified purchase, refund/replay, restore and reconciliation tests |
| 5 | [Notifications](05_Notifications.md) | Identity and domain events | Inbox, consent, device registration, retry/DLQ tests |
| 6 | [Privacy and Deletion](06_Privacy_Deletion.md) | Identity, all data owners | Cross-domain erasure/retention and offline device tests |
| 7 | [Advertising Eligibility (gated)](07_Advertising_Eligibility.md) | Playback + entitlements + legal approval | Ad disabled by default; policy and safety tests before activation |

**Parallel work:** identity scaffolding, catalog editorial model and provider adapter interfaces can develop in parallel once contracts are agreed. Playback monetization authorization needs the entitlement policy contract even before store integrations are live.

## Shared implementation rules

- Build **independently deployable microservices from the first release**, each with its own logical database, REST/OpenAPI and RabbitMQ event contracts; follow [ADR-0015](../00_Project/ADR/ADR-0015-microservices-from-first-release.md) and [Microservices Architecture](../03_Architecture/Microservices_Architecture.md).
- Java 21/Spring Boot, feature-first organization; keep domain and application code independent of framework internals.
- Use PostgreSQL as the authoritative store, Redis only for reconstructible short-lived state and RabbitMQ with transactional outbox for reliable asynchronous work.
- Require adult authorization for privileged actions, server-side ownership for every child-profile resource and verified provider entitlement for paid access.
- Record scope changes and pending policies in the [Decision Register](../00_Project/DECISION_REGISTER.md).
- Use current [API Specification](../03_Architecture/API_Specification.md) and [Error Catalog](../03_Architecture/Error_Catalog.md); do not invent a second public endpoint convention.
- A blueprint is **not Done** until domain tests, integration contracts, negative authorization cases, migrations, observability and failure handling are verified.

## Acceptance and review

For any blueprint, reviewers should answer:
1. What is the owning bounded context?
2. Which invariants and roles apply?
3. Which existing endpoints/event types and database tables are involved?
4. Which state changes must be atomic, idempotent, audited or retried?
5. What happens offline, during timeouts and when provider events arrive out of order?
6. Which exact Given/When/Then cases prove the business outcome?
7. Which configuration/product/legal decisions remain blocked?

These are **implementation drafts** that require cross-check against actual code once code exists. Track deviations in linked PRs and ADRs.
