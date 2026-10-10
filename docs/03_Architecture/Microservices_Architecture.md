# Microservices Architecture — Canonical Runtime Blueprint

Version: 1.0  
Status: **Accepted architecture, implementation pending**  
Owner: Backend Architecture / DevOps  
Decision: [ADR-0015](../00_Project/ADR/ADR-0015-microservices-from-first-release.md)

## 1. What microservices-first means here

KidsAudioBookPlatform will have **separate Java 21/Spring Boot applications from the beginning**, with separately deployable container artifacts, independent database ownership, REST interfaces and RabbitMQ integration events. A monorepo is acceptable because deployables, not Git repository count, determine architecture.

The public edge gateway handles routing, request limits and observability; each business capability remains in its own independently deployed service. Service-to-service traffic stays private, authenticated, timed and contract-tested.

## 2. System landscape

~~~mermaid
flowchart TB
  Mobile[Flutter Child + Parent]
  AdminUI[React Admin Dashboard]
  CDN[CDN / Object Storage]
  G[HTTPS API Gateway / WAF]

  subgraph Services[Private Spring Boot microservices]
    ID[identity-service]
    P[profiles-service]
    C[catalog-service]
    M[media-service]
    PL[playback-service]
    B[billing-service]
    N[notifications-service]
    A[admin-service]
    Ads[advertising-policy-service - gated]
  end

  subgraph Infrastructure[Private shared infrastructure]
    MQ[(RabbitMQ)]
    Redis[(Redis - isolated keys)]
    DB[(PostgreSQL cluster - isolated service databases)]
    Store[(Private object storage)]
  end

  Mobile --> G
  AdminUI --> G
  G --> ID
  G --> P
  G --> C
  G --> PL
  G --> B
  G --> N
  G --> A
  G --> M
  G -. Feature flag + approval .-> Ads
  PL --> C
  PL --> P
  PL --> B
  PL --> M
  M --> Store
  Store --> CDN
  Mobile --> CDN
  C --> MQ
  B --> MQ
  PL --> MQ
  MQ --> N
  MQ --> PL
  ID --> DB
  P --> DB
  C --> DB
  M --> DB
  PL --> DB
  B --> DB
  N --> DB
  A --> DB
~~~

The single DB cylinder symbolizes **shared PostgreSQL infrastructure**, not a shared logical DB/schema or SQL access. Each service uses a different logical database and scoped credential.

## 3. Service ownership reference

| Service | Core data owner | Primary responsibility | Synchronous collaborators |
|---|---|---|---|
| identity-service | identity database | Adult auth, refresh sessions, Parent Zone proof, identity authority | None for login; exposes token validation/public claims |
| profiles-service | profiles database | Child ownership, preferences, parental restrictions | identity-service for security assertions where needed |
| catalog-service | catalog database | Publication state, stories, editorial catalogs and safe discovery | profiles/billing for policy decisions where needed |
| media-service | media database + object storage | Uploads, scan/transcode, media grants and manifests | catalog for publication state via versioned contract |
| playback-service | playback database | Session authorization, progress, completion, sync and downloads | profiles, catalog, billing, media |
| billing-service | billing database | Provider verification, subscriptions, entitlements and reconciliation | External Apple/Google billing APIs |
| notifications-service | notifications database | Preferences, inbox, provider dispatch | identity for recipient verification |
| admin-service | admin database | RBAC-admin orchestration, support/audit, moderation approval | catalog, identity, billing via authorized APIs |
| advertising-policy-service | advertising database | Audited ad-eligibility decisions (if approved) | billing/playback; not enabled by default |

Product API paths in [API Specification](API_Specification.md) are routed to these owners; public paths need not expose internal service naming or topology. Admin publishing writes occur through catalog-service rather than direct catalog DB writes.

## 4. Database per service

~~~text
postgres-instance-or-managed-cluster/
  identity_db        [identity_svc_user]
  profiles_db        [profiles_svc_user]
  catalog_db         [catalog_svc_user]
  media_db           [media_svc_user]
  playback_db        [playback_svc_user]
  billing_db         [billing_svc_user]
  notifications_db   [notifications_svc_user]
  admin_db           [admin_svc_user]
  advertising_db     [only when legally approved and deployed]
~~~

Separate Flyway history, backups/restore targets, migrations and least-privilege connections for each. No cross-database FK, JOIN, JPA relationship, shared read/write transaction or use of another service's database user. Cross-service IDs are opaque strings/UUIDs; enforce existence and ownership via APIs/events. Redis keys and broker routing namespaces must identify the producing/consuming service.

## 5. RPC and event policy

### REST for user-request decisions

Use short synchronous chains for actions requiring an immediate authoritative answer (login, Parent Zone, playback grant, entitlement check). Route queries to the owner using stable internal contracts. Define a request deadline and propagation budget. Never retry non-idempotent writes unless an idempotency key/contract makes it safe.

### RabbitMQ for state propagation and jobs

Use an outbox per producer service, inbox/dedup per consumer and versioned event contracts. Enforce at-least-once semantics; consumers must safely process duplicates/reordered events. Examples:

| Owner event | Consumers | Policy |
|---|---|---|
| AccountDeletionRequested | profiles, playback, billing, notifications, media | Durable deletion saga; auditable completion per owner |
| StoryPublished / StoryUnpublished | playback, notifications, search/projections | Update read models; **new playback grants must authoritatively re-check suspension** |
| SubscriptionActivated / EntitlementsRecalculated | playback, profiles, advertising, notifications | Invalidate caches/projections; fail closed on uncertain paid access |
| StoryCompleted | notifications and advertising if enabled | No ad decisions while feature disabled |
| MediaProcessingCompleted | catalog | Publication precondition using authoritative media status |

Event Catalog remains the canonical event naming/schema document. Cross-service data replication is minimized to rights-scoped projections.

## 6. Distributed privacy and safety

Every service authenticates caller or trusted internal identity and checks object-level authorization. Gateway filtering is not sufficient. Parent Zone verification proof must be accepted only by the appropriate downstream resource owner and bound to parent account/session/expiry. Service-to-service caller identity is separate from the end-user JWT and must be protected (e.g. workload identity/mTLS or signed service JWT based on an infrastructure choice). Avoid forwarding privileged service keys into clients.

Critical content status and entitlement revocation cannot rely indefinitely on stale event projections. Use short-lived caches and an authoritative lookup/fail-closed policy to protect children and licensed media. Exact grace/degraded-read behavior requires contract and threat-model tests.

## 7. Developer workflow

- Every service: separate Maven module/build, Dockerfile, environment config, Flyway scripts, API spec, tests and CI target.
- A shared **technical** library is allowed for transport/logging contracts, but must not own domain JPA entities or access service databases.
- Local Docker Compose runs gateway and each service plus one PostgreSQL instance with separate logical databases, RabbitMQ and Redis, plus object storage emulator.
- Integration tests use disposable databases/containers and WireMock/contract-tested peer stubs. Nightly/staging suites run representative multi-service scenarios with fault injection.
- Deploy services independently with compatibility windows for older producers/consumers and mobile clients; avoid simultaneous breaking migrations.

## 8. Failure budgets and operations

Measure p95/p99 end-to-end and per-service latencies, saturation, timeout count, dependency health, consumer lag/DLQ, entitlement reconciliation delays and signed URL failures. Prefer timeouts, circuit breakers/bulkheads and monitored fallbacks over a long call chain. Nonessential notification/ad outages must not block core playback; uncertain publication/authorization must not fail open.

## 9. Phased implementation order

1. Infrastructure, edge routing, identity-service, CI template, tracing, per-service databases.
2. profiles-service + catalog-service, safe account-scoped discovery.
3. media-service and secure asset publish workflow.
4. billing-service authoritative entitlement policy and store sandbox adapters.
5. playback-service with short synchronous grants and offline progress.
6. notifications-service, privacy deletion orchestration; optional advertising only after approval.
7. Production hardening: distributed fault tests, contract compatibility, per-service backup/restore, on-call and cost baselines.

**Not yet decided:** Kubernetes vs managed containers, cloud vendor/region, service auth mechanism and detailed per-service SLOs. These require infrastructure decisions; do not silently hardcode them.

Related: [Service Contracts and Flows](Microservices_Contracts_and_Flows.md), [Database Design](Database_Design.md), [API Specification](API_Specification.md), [ADR index](../00_Project/ADR/README.md).
