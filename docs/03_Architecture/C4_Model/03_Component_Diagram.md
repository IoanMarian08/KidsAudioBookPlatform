# C4 Model — Backend Component Diagram

Version: 1.0.0  
Status: Active  
Owners: Architecture and Backend Engineering  
Last reviewed: 2026-07-14

## 1. Purpose

This document describes the internal component structure of the KidsAudioBookPlatform backend container. It defines the major backend components, their responsibilities, dependency rules, runtime interactions, and extension points.

The backend consists of **independently deployable Spring Boot microservices from the first release**. Each business context lives in an owning service with an isolated logical database and stable REST/RabbitMQ contracts; internal components remain layered using Clean Architecture. See [ADR-0015](../../00_Project/ADR/ADR-0015-microservices-from-first-release.md).

## 2. Scope

This component view covers:

- inbound API handling;
- authentication and authorization;
- application orchestration;
- domain logic;
- persistence;
- caching;
- asynchronous messaging;
- media access;
- notifications;
- observability;
- integration with external systems.

It does not define implementation-level classes. Those belong to the code-level design document.

## 3. Architectural style

Each microservice has its own API/application/domain/infrastructure components, database adapters, outbox and consumer inbox. Services communicate over authenticated internal REST/OpenAPI interfaces or RabbitMQ integration events, **not in-process module references or shared JPA repositories**. The gateway only routes/validates at the edge; downstream services independently authorize calls.

## 4. High-level component diagram

~~~mermaid
flowchart TB
  Mobile[Flutter Mobile] --> GW[HTTPS API Gateway]
  AdminUI[Admin Dashboard] --> GW
  subgraph S[Independent services and their internal components]
    ID[identity-service: API + auth policies + session persistence]
    P[profiles-service: API + ownership/controls + profile persistence]
    C[catalog-service: API + publication policies + catalog persistence + outbox]
    PL[playback-service: API + access/use cases + progress persistence + outbox]
    M[media-service: API + processing use cases + asset persistence]
    B[billing-service: API + verification + entitlements + outbox]
    N[notifications-service: API + inbox + workers]
    A[admin-service: API + admin orchestration + audit]
  end
  GW --> ID
  GW --> P
  GW --> C
  GW --> PL
  GW --> M
  GW --> B
  GW --> N
  GW --> A
  PL --> C
  PL --> P
  PL --> B
  PL --> M
  B --> Rabbit[(RabbitMQ)]
  C --> Rabbit
  Rabbit --> N
  C --> DB[(Service-owned PostgreSQL databases)]
  ID --> DB
  P --> DB
  PL --> DB
  M --> DB
  B --> DB
  N --> DB
  A --> DB
~~~

The database node represents **multiple isolated logical databases**, not one common service database. Each service's detailed API, application, domain, and infrastructure diagram is an **internal component view of that service**. Business rule classes may be reused as technical patterns but never as a shared mutable domain layer.


## 5. API layer

### Responsibilities

- expose REST endpoints;
- deserialize and validate transport payloads;
- resolve authenticated principal and profile context;
- invoke application use cases;
- map domain and application errors to API errors;
- apply pagination, idempotency, and correlation metadata;
- return stable DTOs.

### Prohibited responsibilities

The API layer must not:

- contain business rules;
- access repositories directly;
- publish messages directly;
- construct persistence entities;
- call external providers directly;
- manage transactions.

## 6. Security component

### Responsibilities

- access-token validation;
- refresh-token lifecycle;
- device-session validation;
- role and permission checks;
- Parent Zone PIN and re-authentication checks;
- ownership validation support;
- rate-limit identity resolution;
- security audit event generation.

### Primary collaborators

- Identity & Access Context;
- Redis for short-lived security state;
- PostgreSQL for durable session and account state;
- audit logging component.

## 7. Identity & Access context

### Responsibilities

- account registration and lifecycle;
- authentication;
- password management;
- account verification;
- session and device management;
- consent state;
- parental account ownership;
- roles and permissions.

### Core application services

- `RegisterAccountUseCase`
- `AuthenticateAccountUseCase`
- `RefreshSessionUseCase`
- `RevokeSessionUseCase`
- `ChangePasswordUseCase`
- `VerifyAccountUseCase`
- `UpdateConsentUseCase`

### Domain components

- Account aggregate;
- DeviceSession aggregate;
- Credential policy;
- Consent policy;
- Session risk policy.

### Published events

- `AccountRegistered`
- `AccountVerified`
- `PasswordChanged`
- `SessionCreated`
- `SessionRevoked`
- `ConsentUpdated`

## 8. Profiles context

### Responsibilities

- child-profile creation and management;
- profile preferences;
- age-band and content-suitability settings;
- avatar and room configuration;
- active-profile selection;
- premium-only multi-profile rules.

### Domain components

- ChildProfile aggregate;
- ProfileLimitPolicy;
- AgeSuitabilityPolicy;
- ProfilePreference value objects.

### Published events

- `ChildProfileCreated`
- `ChildProfileUpdated`
- `ChildProfileDeleted`
- `ActiveProfileChanged`

## 9. Catalog context

### Responsibilities

- stories, series, and episodes;
- authors and narrators;
- categories and collections;
- language and age metadata;
- publication workflow;
- free/premium visibility;
- curated and searchable catalog views.

### Internal components

- Catalog Command Service;
- Catalog Query Service;
- Publication Workflow;
- Search Projection Builder;
- Catalog Repository Adapter;
- Catalog Cache Adapter.

### Domain components

- Story aggregate;
- Series aggregate;
- Episode entity;
- PublicationState value object;
- ContentSuitability policy;
- PremiumVisibility policy.

### Published events

- `StoryCreated`
- `StoryUpdated`
- `StoryPublished`
- `StoryUnpublished`
- `EpisodePublished`
- `CatalogMetadataChanged`

## 10. Playback context

### Responsibilities

- playback-session initiation;
- entitlement validation orchestration;
- resume position;
- progress persistence;
- completion tracking;
- listening history;
- offline-playback synchronization;
- continue-listening read model.

### Internal components

- Playback Session Service;
- Progress Service;
- History Service;
- Entitlement Gateway;
- Media URL Gateway;
- Playback Read Model;

### Domain components

- PlaybackSession aggregate;
- ListeningProgress aggregate;
- ProgressPosition value object;
- CompletionPolicy;
- ResumePolicy.

### Published events

- `PlaybackStarted`
- `ProgressUpdated`
- `StoryCompleted`
- `PlaybackStopped`

## 11. Subscription context

### Responsibilities

- subscription state;
- premium entitlements;
- trial lifecycle;
- billing-provider reconciliation;
- purchase receipt validation;
- grace periods;
- feature access decisions.

### Internal components

- Subscription Application Service;
- Entitlement Service;
- Billing Provider Adapter;
- Receipt Validation Adapter;
- Subscription Reconciliation Worker;

### Domain components

- Subscription aggregate;
- Entitlement policy;
- Trial policy;
- Grace-period policy;
- BillingState value object.

### Published events

- `SubscriptionActivated`
- `SubscriptionRenewed`
- `SubscriptionExpired`
- `SubscriptionCancelled`
- `TrialStarted`
- `EntitlementChanged`

## 12. Notification context

### Responsibilities

- in-app notifications;
- push notifications;
- email notifications where applicable;
- templates and localization;
- scheduling;
- retries and dead-letter handling;
- delivery tracking;
- read/unread state.

### Internal components

- Notification Command Service;
- Notification Query Service;
- Template Renderer;
- Localization Resolver;
- Push Provider Adapter;
- Delivery Worker;
- Retry Coordinator;

### Published events

- `NotificationCreated`
- `NotificationScheduled`
- `NotificationDelivered`
- `NotificationFailed`
- `NotificationRead`

## 13. Media context

### Responsibilities

- controlled upload sessions;
- file metadata;
- content-type and size validation;
- malware-scan coordination;
- audio processing and transcoding;
- artwork derivatives;
- signed download URLs;
- storage lifecycle management.

### Internal components

- Upload Session Service;
- Media Validation Service;
- Transcoding Coordinator;
- Derivative Generator;
- Signed URL Service;
- Object Storage Adapter;
- CDN Adapter.

### Published events

- `MediaUploaded`
- `MediaValidated`
- `MediaRejected`
- `TranscodingCompleted`
- `MediaReady`

## 14. Administration context

### Responsibilities

- content management;
- moderation;
- publication approval;
- account support operations;
- operational dashboards;
- audit search;
- administrative exports;
- feature configuration.

Administration commands must pass the same application and domain boundaries as public API commands. Admin controllers must never bypass domain rules by writing directly to persistence.

## 15. Shared technical components

Shared components are limited to technical capabilities that do not own business meaning.

Allowed examples:

- clock abstraction;
- identifier generation;
- correlation and trace support;
- transaction support;
- JSON serialization configuration;
- messaging infrastructure;
- outbox infrastructure;
- generic pagination primitives;
- standardized API error representation;
- metrics and structured logging adapters.

A shared module must not become a dumping ground for cross-context business logic.

## 16. Persistence components

Each bounded context owns its repository interfaces and persistence adapters.

```mermaid
flowchart LR
    App[Application Service] --> Port[Repository Port]
    Adapter[JPA Repository Adapter] --> Port
    Adapter --> Jpa[Spring Data Repository]
    Jpa --> DB[(PostgreSQL)]
```

Rules:

- repository interfaces belong to the owning context;
- JPA entities remain in infrastructure;
- domain objects are not required to be JPA entities;
- queries that serve read models may use dedicated projections;
- transactions begin at application-service boundaries;
- cross-context database writes are prohibited.

## 17. Caching components

Caching is implemented through ports owned by the consuming context.

Typical use:

- catalog projections;
- home-screen read models;
- short-lived entitlement snapshots;
- rate-limit counters;
- verification data;
- feature configuration.

Cache access must never leak Redis-specific types into domain or application code.

## 18. Messaging components

### Outbox publisher

The outbox publisher reads committed events from PostgreSQL and publishes them to RabbitMQ.

```mermaid
sequenceDiagram
    participant App as Application Service
    participant DB as PostgreSQL
    participant Outbox as Outbox Publisher
    participant MQ as RabbitMQ
    participant Consumer as Consumer

    App->>DB: Commit aggregate changes and outbox event
    DB-->>App: Transaction committed
    Outbox->>DB: Read unpublished events
    Outbox->>MQ: Publish event
    MQ-->>Outbox: Acknowledge
    Outbox->>DB: Mark event published
    MQ->>Consumer: Deliver event
    Consumer->>Consumer: Process idempotently
```

### Consumer rules

- consumers must be idempotent;
- duplicate delivery must be expected;
- retries must be bounded;
- poison messages move to a dead-letter queue;
- message handlers must emit metrics and structured logs;
- business state changes occur through application services.

## 19. External integration components

Every external provider is isolated behind a context-owned port and an infrastructure adapter.

Examples:

- Apple/Google purchase validation;
- push-notification provider;
- email provider;
- object storage;
- CDN;
- malware-scanning provider;
- analytics provider.

Provider-specific models must not enter the domain layer.

## 20. Critical runtime flow — start playback

```mermaid
sequenceDiagram
    participant Mobile
    participant API
    participant Playback
    participant Subscription
    participant Catalog
    participant Media
    participant DB
    participant Redis

    Mobile->>API: POST /playback/sessions
    API->>Playback: StartPlayback command
    Playback->>Catalog: Load playable story metadata
    Catalog->>Redis: Read cached projection
    alt cache miss
        Catalog->>DB: Load story projection
    end
    Playback->>Subscription: Check entitlement
    Subscription->>Redis: Read entitlement snapshot
    alt snapshot unavailable
        Subscription->>DB: Load subscription state
    end
    Playback->>Media: Generate signed media URL
    Media->>DB: Load media metadata
    Playback->>DB: Persist playback session
    Playback-->>API: Session and signed URL
    API-->>Mobile: 201 Created
```

## 21. Critical runtime flow — publish story

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant Catalog
    participant DB
    participant Outbox
    participant MQ
    participant SearchWorker
    participant NotificationWorker

    Admin->>API: POST /admin/stories/{id}/publish
    API->>Catalog: PublishStory command
    Catalog->>Catalog: Validate publication rules
    Catalog->>DB: Update story and write outbox event
    DB-->>Catalog: Commit
    Catalog-->>API: Published story
    API-->>Admin: 200 OK
    Outbox->>DB: Read StoryPublished event
    Outbox->>MQ: Publish event
    MQ->>SearchWorker: Update search projection
    MQ->>NotificationWorker: Prepare relevant notifications
```

## 22. Dependency rules

Allowed dependency direction:

```text
API / Messaging Adapters
        ↓
Application Layer
        ↓
Domain Layer
        ↑
Infrastructure Adapters implement ports defined inward
```

Mandatory rules:

- domain depends on no framework;
- application may depend on domain;
- adapters may depend on application and domain contracts;
- one bounded context cannot import another context's persistence package;
- one context may call another only through an explicit application-facing interface or published event;
- shared technical code cannot depend on business contexts.

## 23. Transaction boundaries

A transaction normally covers one application use case and one bounded context.

Do not keep transactions open while:

- calling external providers;
- uploading or downloading media;
- waiting for RabbitMQ;
- performing long-running transformations;
- returning streamed content.

Cross-context workflows use orchestration, events, and compensating behavior rather than distributed transactions.

## 24. Failure handling

| Failure | Expected behavior |
|---|---|
| PostgreSQL unavailable | Reject state-changing operations; return controlled failure |
| Redis unavailable | Fall back to source of truth where safe |
| RabbitMQ unavailable | Persist outbox events and retry later |
| Object storage unavailable | Prevent new media access or upload completion; do not corrupt metadata |
| Billing provider unavailable | Apply documented entitlement grace policy |
| Push provider unavailable | Persist notification and retry asynchronously |
| Search projection stale | Fall back to simpler catalog queries where feasible |

## 25. Observability

Every component must expose or contribute to:

- request and use-case latency;
- success and failure counts;
- database timing;
- cache hit ratio;
- queue lag;
- retry and dead-letter counts;
- external-provider latency;
- business events;
- correlation and trace identifiers.

Metrics must be labeled by stable, low-cardinality values.

## 26. Testing strategy by component

| Component type | Required tests |
|---|---|
| Controller | API contract and authorization tests |
| Application service | Use-case tests with mocked ports or test adapters |
| Domain component | Fast unit tests for business invariants |
| Repository adapter | Integration tests with PostgreSQL |
| Cache adapter | Integration tests with Redis |
| Message publisher/consumer | Contract and integration tests with RabbitMQ |
| External adapter | Contract tests and failure simulations |
| End-to-end flow | Production-like happy-path and critical failure-path tests |

## 27. Microservice Component Readiness

All listed domains are microservices from the start. Before a service is called implementation-ready, verify its individually deployable image, endpoint/event contracts, unique logical PostgreSQL database and credential, per-service Flyway migrations, ownership controls, outbound deadline/retry policy, outbox/inbox idempotency, distributed tracing, tests, and operational alerts.

Changing the service boundary requires an ADR and a migration/compatibility plan, not a future extraction milestone. See [Microservices Contracts](../Microservices_Contracts_and_Flows.md).


## 28. Architecture review checklist

- [ ] Component belongs to exactly one bounded context.
- [ ] Business rules are in domain or application components.
- [ ] Controller contains no persistence logic.
- [ ] Repository access is context-owned.
- [ ] Transactions are bounded to one use case.
- [ ] External integrations are behind ports.
- [ ] Events are published through the outbox pattern.
- [ ] Consumers are idempotent.
- [ ] Cache behavior includes failure and invalidation rules.
- [ ] Authorization includes resource ownership.
- [ ] Metrics, logs, and traces are defined.
- [ ] Tests cover business rules and adapters.
- [ ] Cross-context dependencies are explicit.

## 29. Related documents

- `01_System_Context.md`
- `02_Container_Diagram.md`
- `04_Code_Diagram.md`
- `../Software_Architecture.md`
- `../Backend_Architecture.md`
- `../Database_Design.md`
- `../API_Specification.md`
- `../Security_Architecture.md`
- `../Logging_Monitoring.md`
