# Microservices — Contracts, Ownership and Runtime Flows

Version: 1.0  
Status: Contract design guide; machine-readable specifications pending implementation  
Owner: Backend Engineering / Security / QA  
Decision: [ADR-0015](../00_Project/ADR/ADR-0015-microservices-from-first-release.md)

## 1. Contract rules

1. Every public endpoint in [API Specification](API_Specification.md) has **one** service owner; API Gateway only routes or authenticates at the edge, never implements business decisions.
2. Every inter-service REST endpoint has an OpenAPI contract, auth scope, request budget/timeout, idempotency definition, error semantics and compatibility policy.
3. RabbitMQ integration events are named and versioned in [Event Catalog](Event_Catalog.md). Producer-owned outbox and consumer-owned inbox use unique event IDs and local ACID. No global transaction across databases.
4. Never use direct SQL, shared JPA entities or distributed joins to exchange business data.
5. Distinguish local business error, remote timeout, transient dependency failure and permanent authorization denial; no arbitrary 200/empty fallback for child safety and premium decisions.
6. Use correlation ID, W3C trace context, sanitized structured logs and metrics across RPC and events.

## 2. Public API ownership map

| Existing route prefix/examples | Backend owner | Dependencies |
|---|---|---|
| /auth/**, /sessions/**, /me (account), /parent-zone/** | identity-service | Email verification, account database |
| /child-profiles/** | profiles-service | Parent authorization/identity claims |
| /stories/**, /series/**, /episodes/**, /categories/**, /collections/**, /search, /ambient-sounds | catalog-service | Profile eligibility and billing policy only when relevant |
| /playback/**, /sync/offline, /downloads/**, profile favorites/history/progress | playback-service | Profiles, Catalog, Billing, Media |
| /subscription-plans, /purchases/**, /me/subscription*, /me/entitlements | billing-service | Apple/Google store verification |
| /notifications/**, /notification-preferences, /devices/** | notifications-service | Account-owned recipient/device verification |
| /admin/** account-support/audit workflows | admin-service | Authoritative service contract for each action |
| /admin/stories/** and /admin/media/uploads/** | catalog-service and media-service behind admin orchestration | Catalog/Media own business mutations |
| /advertising/** | advertising-policy-service (gated) | Verified playback session and premium status |
| /support/requests | admin-service or support adapter | Access policy and privacy review |

Exact endpoints/status codes remain authoritative in API Specification; this table assigns ownership, **not** an additional API version.

## 3. Playback authorization sequence

~~~mermaid
sequenceDiagram
    actor Child
    participant App as Flutter
    participant GW as API Gateway
    participant Play as playback-service
    participant P as profiles-service
    participant C as catalog-service
    participant B as billing-service
    participant M as media-service
    Child->>App: Tap story
    App->>GW: POST /playback/sessions
    GW->>Play: Forward identity + trace
    Play->>P: Validate profile ownership/parent controls
    P-->>Play: Authorized + policy
    Play->>C: Verify published and age/locale
    C-->>Play: Eligible content version
    opt Premium
      Play->>B: Verify effective entitlement
      B-->>Play: Active or denied
    end
    Play->>M: Create short-lived media grant
    M-->>Play: Signed CDN URLs
    Play-->>App: Session + media + resume
~~~

Implement a bounded request budget; parallelize independent safe queries where appropriate. If identity, content publication or premium entitlement cannot be verified, **deny new authorization safely** instead of using stale permissive data.

## 4. Editorial publishing flow

~~~mermaid
sequenceDiagram
  actor Editor
  participant Admin as admin-service
  participant Catalog as catalog-service
  participant Media as media-service
  participant MQ as RabbitMQ
  Editor->>Admin: Approve/publish story
  Admin->>Catalog: Authorized publication command
  Catalog->>Media: Verify scan/asset readiness
  Media-->>Catalog: Ready + immutable asset version
  Catalog->>Catalog: Local DB transaction + outbox
  Catalog-->>Admin: Publication result
  Catalog-->>MQ: StoryPublished.v1
  MQ-->>Admin: Consume for audit/projections
~~~

Catalog is authoritative for story state; Admin cannot mutate Catalog DB directly. A media outage during publish prevents unsafe approval; media processing failures are retried via the media-owned queue/worker.

## 5. Purchase and entitlement flow

Provider callback → billing-service authenticated adapter → provider verification → billing DB subscription/entitlement update + outbox → RabbitMQ EntitlementsRecalculated → profile/playback/ad-policy projections. **Playback must validate current authority** (or an explicitly bounded, revocation-safe cache) before granting premium media. Duplicate provider events do not duplicate entitlement effects. Compensating reconciliation is required after store outage.

## 6. Parent account deletion saga

~~~mermaid
flowchart LR
  Req[Parent verified deletion request] --> ID[identity-service orchestrates durable saga]
  ID --> MQ[(RabbitMQ events / commands)]
  MQ --> Profiles[profiles-service purge]
  MQ --> Play[playback-service purge]
  MQ --> Media[media-service grants purge]
  MQ --> Notify[notifications-service revoke devices]
  MQ --> Billing[billing-service retain legally required records only]
  Profiles --> Confirm[Per-service completion receipts]
  Play --> Confirm
  Media --> Confirm
  Notify --> Confirm
  Billing --> Confirm
  Confirm --> Done[Audit and mark completed only after all required responses]
~~~

Do not declare deletion complete on send/ack alone. Retention exceptions are policy-driven; timed-out stages retry idempotently and appear in an operational dashboard. Use command contracts distinct from public event names where appropriate.

## 7. Contract and resilience test matrix

| Scenario | Required evidence |
|---|---|
| Gateway returns unauthorized/forbidden | Downstream repeats security/ownership validation |
| Caller times out after remote committed write | Retry is idempotent or reconciled by stable request key |
| RabbitMQ delivers duplicate event | Consumer inbox suppresses repeated mutation |
| Provider sends old event after new state | Billing preserves verified latest authoritative status |
| Catalog story suspended with stale playback projection | New grants rejected on authoritative publication state |
| Partial deletion saga stalls | Work remains durable/retriable and not marked complete |
| Any service database is inaccessible by another service principal | Privilege test in integration environment |
| Notification or ad service fails | Eligible story playback still works; ad stays disabled |

## 8. Open issues before coding

Service-internal endpoint names, API gateway technology, network service identity, exact retry budgets, cross-service security claims, per-service database names/secret stores, and deployment orchestrator require implementation-level reviews. Machine-readable OpenAPI/event schema artifacts must be added before integrating two services.

See [Microservices Architecture](Microservices_Architecture.md) and [ADR-0015](../00_Project/ADR/ADR-0015-microservices-from-first-release.md).
