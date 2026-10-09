# C4 Runtime Views

Version: 1.0.0  
Status: Active Draft  
Owners: Architecture, Backend Engineering, Mobile Engineering  
Last reviewed: 2026-07-14

## 1. Purpose

This document complements the static C4 diagrams with runtime views for the most important user and administrative flows in KidsAudioBookPlatform.

The runtime views show how containers and components collaborate during real requests, where trust boundaries are crossed, which operations are synchronous or asynchronous, and where failure handling is required.

## 2. Scope

The document covers:

- authentication and session refresh;
- child profile selection;
- catalog browsing;
- story playback authorization;
- playback progress synchronization;
- offline playback reconciliation;
- subscription entitlement validation;
- content publication;
- media upload and processing;
- notification dispatch;
- audit and observability propagation.

## 3. Runtime modeling rules

Every runtime flow must make the following explicit:

1. initiating actor;
2. entry container;
3. trust-boundary transitions;
4. synchronous dependencies;
5. asynchronous messages;
6. transaction boundary;
7. retry behavior;
8. idempotency strategy;
9. timeout behavior;
10. observability context.

A runtime diagram is not complete if it only shows the happy path.

## 4. Authentication and session creation

```mermaid
sequenceDiagram
    autonumber
    actor Parent
    participant Mobile as Flutter Mobile App
    participant API as Spring Boot API
    participant Identity as Identity Component
    participant DB as PostgreSQL
    participant Redis as Redis
    participant Audit as Audit Component

    Parent->>Mobile: Submit email and password
    Mobile->>API: POST /v1/auth/login
    API->>Identity: Authenticate credentials
    Identity->>DB: Load account and password hash
    DB-->>Identity: Account data
    Identity->>Identity: Verify password and account state
    Identity->>Redis: Create device session metadata
    Identity->>DB: Persist refresh-token family and login event
    Identity->>Audit: Record successful login
    Identity-->>API: Access token, refresh token, account summary
    API-->>Mobile: 200 OK
```

### Runtime rules

- Password verification must use an approved adaptive hash.
- Account-state validation happens before token issuance.
- Refresh tokens are rotated and bound to a token family.
- Device session metadata may be cached in Redis, but authoritative revocation data remains durable.
- Login events must include correlation ID, device ID, IP classification, and outcome.
- Authentication errors must not reveal whether an account exists.

### Failure paths

| Failure | Required behavior |
|---|---|
| Invalid credentials | Return generic authentication failure |
| Locked account | Deny login and emit audit event |
| Redis unavailable | Continue with durable session storage where safe |
| Database unavailable | Fail closed |
| Audit sink delayed | Buffer or persist audit event without blocking indefinitely |

## 5. Access-token refresh

```mermaid
sequenceDiagram
    autonumber
    participant Mobile as Flutter Mobile App
    participant API as Spring Boot API
    participant Identity as Identity Component
    participant DB as PostgreSQL
    participant Redis as Redis

    Mobile->>API: POST /v1/auth/refresh
    API->>Identity: Refresh token request
    Identity->>DB: Load token family and session state
    DB-->>Identity: Session state
    Identity->>Identity: Validate expiry, rotation, reuse, revocation
    alt Valid refresh token
        Identity->>DB: Revoke old token and persist rotated token
        Identity->>Redis: Refresh session cache
        Identity-->>API: New token pair
        API-->>Mobile: 200 OK
    else Reuse detected
        Identity->>DB: Revoke complete token family
        Identity->>Redis: Remove session cache
        Identity-->>API: Refresh rejected
        API-->>Mobile: 401 Unauthorized
    end
```

Refresh-token reuse detection must revoke the full token family and force re-authentication.

## 6. Child profile selection

```mermaid
sequenceDiagram
    autonumber
    actor Parent
    participant Mobile as Flutter Mobile App
    participant API as Spring Boot API
    participant Profiles as Profile Component
    participant DB as PostgreSQL
    participant Redis as Redis

    Parent->>Mobile: Select child profile
    Mobile->>API: POST /v1/session/active-profile
    API->>Profiles: Validate profile ownership and status
    Profiles->>DB: Load profile and account relation
    DB-->>Profiles: Profile data
    Profiles->>Redis: Store short-lived active-profile context
    Profiles-->>API: Active profile summary
    API-->>Mobile: 200 OK
```

The active profile is a convenience context, not an authorization shortcut. Every profile-scoped request must still validate ownership.

## 7. Browse child home screen

```mermaid
sequenceDiagram
    autonumber
    actor Child
    participant Mobile as Flutter Mobile App
    participant API as Spring Boot API
    participant Home as Home Aggregation Component
    participant Redis as Redis
    participant Catalog as Catalog Component
    participant Progress as Playback Component
    participant DB as PostgreSQL
    participant CDN as CDN / Object Storage

    Child->>Mobile: Open home screen
    Mobile->>API: GET /v1/profiles/{id}/home
    API->>Home: Build child home view
    Home->>Redis: Load cached home sections
    alt Cache hit
        Redis-->>Home: Cached view
    else Cache miss
        Home->>Catalog: Load curated and age-appropriate content
        Catalog->>DB: Query published story projections
        DB-->>Catalog: Story summaries
        Home->>Progress: Load continue-listening items
        Progress->>DB: Query recent progress
        DB-->>Progress: Progress summaries
        Home->>Redis: Store assembled view with TTL and jitter
    end
    Home-->>API: Home response
    API-->>Mobile: Story summaries and signed artwork URLs
    Mobile->>CDN: Load artwork
```

### Performance constraints

- No more than two synchronous internal component calls after cache miss.
- The response must use summary projections, not full aggregates.
- Artwork bytes must not pass through the API.
- A recommendation failure must degrade to curated content.

## 8. Story details and playback authorization

```mermaid
sequenceDiagram
    autonumber
    actor Child
    participant Mobile as Flutter Mobile App
    participant API as Spring Boot API
    participant Catalog as Catalog Component
    participant Entitlements as Subscription Component
    participant Playback as Playback Component
    participant DB as PostgreSQL
    participant Storage as Object Storage
    participant CDN as CDN

    Child->>Mobile: Tap story
    Mobile->>API: GET /v1/stories/{storyId}
    API->>Catalog: Load published story details
    Catalog->>DB: Load story projection
    DB-->>Catalog: Story metadata
    Catalog-->>API: Story details
    API-->>Mobile: Metadata and access classification

    Child->>Mobile: Start playback
    Mobile->>API: POST /v1/playback/sessions
    API->>Entitlements: Validate account entitlement
    Entitlements->>DB: Load subscription and access rules
    DB-->>Entitlements: Entitlement state
    Entitlements-->>API: Access granted
    API->>Playback: Create playback session
    Playback->>DB: Persist session start
    Playback->>Storage: Generate short-lived signed media URL
    Storage-->>Playback: Signed URL
    Playback-->>API: Playback session and URL
    API-->>Mobile: 201 Created
    Mobile->>CDN: GET audio with range request
    CDN-->>Mobile: Audio bytes
```

### Security rules

- The story must be published and allowed for the selected profile.
- Premium access must be checked before signed URL generation.
- Signed media URLs must be short-lived and scoped to the requested object.
- The URL response must not expose storage credentials or internal bucket details.

## 9. Playback progress synchronization

```mermaid
sequenceDiagram
    autonumber
    participant Mobile as Flutter Mobile App
    participant API as Spring Boot API
    participant Playback as Playback Component
    participant DB as PostgreSQL
    participant Outbox as Outbox Table
    participant Publisher as Outbox Publisher
    participant MQ as RabbitMQ
    participant Analytics as Analytics Consumer

    Mobile->>API: PUT /v1/profiles/{profileId}/progress/{storyId}
    API->>Playback: Update progress command
    Playback->>DB: Lock or load current progress record
    Playback->>Playback: Resolve monotonic progress and completion rules
    Playback->>DB: Persist progress
    Playback->>Outbox: Persist ProgressUpdated event
    Playback-->>API: Updated progress
    API-->>Mobile: 200 OK

    Publisher->>Outbox: Poll unpublished events
    Outbox-->>Publisher: ProgressUpdated
    Publisher->>MQ: Publish event
    Publisher->>Outbox: Mark published
    MQ-->>Analytics: Deliver event
    Analytics->>Analytics: Update analytics projection
```

### Consistency rules

- Progress writes must be idempotent.
- The client supplies an operation ID or a version where required.
- Replayed updates must not move progress backward unless the user explicitly restarts a story.
- Completion events must be emitted once per completion transition.
- Event publication uses the transactional outbox pattern.

## 10. Offline playback reconciliation

```mermaid
sequenceDiagram
    autonumber
    actor Child
    participant Mobile as Flutter Mobile App
    participant Local as Local Secure Storage
    participant API as Spring Boot API
    participant Playback as Playback Component
    participant Entitlements as Subscription Component
    participant DB as PostgreSQL

    Child->>Mobile: Listen while offline
    Mobile->>Local: Persist progress operations

    Note over Mobile,API: Network connectivity restored

    Mobile->>API: POST /v1/playback/progress/batch
    API->>Entitlements: Validate current or grace-period entitlement
    Entitlements->>DB: Load entitlement state
    DB-->>Entitlements: Entitlement result
    Entitlements-->>API: Access decision
    API->>Playback: Reconcile ordered progress operations
    Playback->>DB: Load current server versions
    DB-->>Playback: Current progress
    Playback->>Playback: Resolve conflicts deterministically
    Playback->>DB: Persist reconciled progress
    Playback-->>API: Per-operation results
    API-->>Mobile: 200 OK with accepted and rejected operations
    Mobile->>Local: Remove acknowledged operations
```

The batch endpoint must return a result for every operation. One invalid operation must not silently discard the full batch unless atomic behavior is explicitly requested.

## 11. Subscription purchase and entitlement activation

```mermaid
sequenceDiagram
    autonumber
    actor Parent
    participant Mobile as Flutter Mobile App
    participant Store as Apple / Google Store
    participant API as Spring Boot API
    participant Billing as Subscription Component
    participant DB as PostgreSQL
    participant MQ as RabbitMQ
    participant Notifications as Notification Consumer

    Parent->>Mobile: Purchase premium subscription
    Mobile->>Store: Complete native purchase
    Store-->>Mobile: Signed purchase token / receipt
    Mobile->>API: POST /v1/subscriptions/verify
    API->>Billing: Verify purchase command
    Billing->>Store: Validate receipt with provider
    Store-->>Billing: Verified transaction state
    Billing->>DB: Persist provider transaction and entitlement
    Billing->>DB: Persist outbox event
    Billing-->>API: Active entitlement
    API-->>Mobile: 200 OK
    DB-->>MQ: Outbox publisher emits EntitlementActivated
    MQ-->>Notifications: Deliver event
    Notifications->>Notifications: Schedule confirmation notification
```

### Idempotency

Provider transaction IDs are unique. Repeated verification of the same transaction must return the existing result and must not create duplicate entitlements.

## 12. Provider webhook processing

```mermaid
sequenceDiagram
    autonumber
    participant Store as Apple / Google Store
    participant Webhook as Webhook Endpoint
    participant Billing as Subscription Component
    participant DB as PostgreSQL
    participant MQ as RabbitMQ

    Store->>Webhook: Subscription lifecycle event
    Webhook->>Webhook: Verify signature and timestamp
    Webhook->>Billing: Process provider event
    Billing->>DB: Check provider event idempotency key
    alt New event
        Billing->>DB: Persist event and update entitlement
        Billing->>DB: Persist outbox event
        Billing-->>Webhook: Accepted
        Webhook-->>Store: 2xx
        DB-->>MQ: Publish entitlement lifecycle event
    else Duplicate event
        Billing-->>Webhook: Already processed
        Webhook-->>Store: 2xx
    end
```

Invalid signatures must be rejected before any business processing.

## 13. Content and media publication

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant AdminUI as Admin Dashboard
    participant API as Spring Boot API
    participant AdminComp as Administration Component
    participant Media as Media Component
    participant Storage as Object Storage
    participant DB as PostgreSQL
    participant MQ as RabbitMQ
    participant Worker as Media Worker
    participant Catalog as Catalog Component

    Admin->>AdminUI: Create or edit story
    AdminUI->>API: POST /v1/admin/stories
    API->>AdminComp: Validate permissions and command
    AdminComp->>DB: Persist draft metadata
    AdminComp-->>API: Draft story
    API-->>AdminUI: 201 Created

    AdminUI->>API: POST /v1/admin/media/upload-sessions
    API->>Media: Create controlled upload session
    Media->>Storage: Generate presigned upload request
    Storage-->>Media: Upload URL
    Media-->>API: Upload session
    API-->>AdminUI: Upload details
    AdminUI->>Storage: Upload audio or image directly
    AdminUI->>API: POST /v1/admin/media/{id}/complete
    API->>Media: Confirm upload
    Media->>DB: Persist processing state and outbox event
    DB-->>MQ: Publish MediaUploaded
    MQ-->>Worker: Deliver media-processing job
    Worker->>Storage: Read uploaded object
    Worker->>Worker: Malware scan, validate, transcode, derive metadata
    Worker->>Storage: Store immutable derivatives
    Worker->>DB: Persist processed media state

    Admin->>AdminUI: Publish story
    AdminUI->>API: POST /v1/admin/stories/{id}/publish
    API->>Catalog: Validate publication readiness
    Catalog->>DB: Persist published state and outbox event
    Catalog-->>API: Published story
    API-->>AdminUI: 200 OK
```

### Publication invariants

A story cannot become published unless:

- required metadata exists;
- age classification is valid;
- at least one playable media asset is in ready state;
- artwork is available;
- language information is complete;
- premium/free classification is explicit;
- moderation and approval rules are satisfied.

## 14. Notification dispatch

```mermaid
sequenceDiagram
    autonumber
    participant Producer as Domain Event Producer
    participant MQ as RabbitMQ
    participant Notify as Notification Component
    participant DB as PostgreSQL
    participant FCM as Firebase Cloud Messaging
    participant Email as Email Provider
    participant Mobile as Mobile App

    Producer->>MQ: Publish notification-relevant event
    MQ-->>Notify: Deliver event
    Notify->>DB: Load preferences, locale, quiet hours, devices
    Notify->>Notify: Resolve template and channels
    Notify->>DB: Persist notification and delivery attempts
    alt Push allowed
        Notify->>FCM: Send push message
        FCM-->>Mobile: Deliver push
        FCM-->>Notify: Delivery response
    end
    alt Email required
        Notify->>Email: Send transactional email
        Email-->>Notify: Provider response
    end
    Notify->>DB: Update delivery status
```

### Delivery rules

- Consumers must be idempotent.
- Notification preferences and quiet hours must be respected.
- Child-facing notifications must use approved safe templates.
- Provider failures use bounded retries and dead-letter handling.
- A notification failure must not roll back the originating business transaction.

## 15. Account deletion and privacy workflow

```mermaid
sequenceDiagram
    autonumber
    actor Parent
    participant Mobile as Flutter Mobile App
    participant API as Spring Boot API
    participant Identity as Identity Component
    participant Privacy as Privacy Orchestrator
    participant DB as PostgreSQL
    participant MQ as RabbitMQ
    participant Workers as Deletion Workers
    participant Storage as Object Storage

    Parent->>Mobile: Confirm account deletion
    Mobile->>API: DELETE /v1/account
    API->>Identity: Re-authenticate sensitive action
    Identity-->>API: Re-authentication valid
    API->>Privacy: Start deletion workflow
    Privacy->>DB: Mark account deletion pending
    Privacy->>DB: Revoke sessions and tokens
    Privacy->>DB: Persist deletion job and outbox event
    Privacy-->>API: Deletion accepted
    API-->>Mobile: 202 Accepted
    DB-->>MQ: Publish AccountDeletionRequested
    MQ-->>Workers: Deliver deletion tasks
    Workers->>DB: Delete or anonymize domain data by retention rule
    Workers->>Storage: Delete user-owned objects where applicable
    Workers->>DB: Persist workflow completion and audit evidence
```

Deletion is an orchestrated workflow, not a single cascading SQL statement. Legal retention requirements must be applied explicitly.

## 16. Correlation and trace propagation

Every synchronous request and asynchronous message must carry observability context.

```mermaid
flowchart LR
    Client[Client Request] -->|X-Correlation-Id / trace context| Gateway[API Entry]
    Gateway --> App[Application Component]
    App --> DB[(PostgreSQL)]
    App -->|trace context in headers| MQ[(RabbitMQ)]
    MQ --> Consumer[Async Consumer]
    Consumer --> Provider[External Provider]
    Gateway --> Logs[Structured Logs]
    App --> Metrics[Metrics]
    Consumer --> Traces[Distributed Traces]
```

Required fields include:

- correlation ID;
- trace ID and span ID;
- actor type and actor ID where permitted;
- account ID or profile ID where relevant;
- operation name;
- event ID for messages;
- idempotency key for retriable writes;
- source container and component.

Sensitive values, tokens, passwords, PINs, and raw provider receipts must never be logged.

## 17. Timeout hierarchy

Timeouts must be layered so that callers stop waiting after callees.

Example request budget:

| Layer | Maximum budget |
|---|---:|
| Mobile request | 10 seconds |
| API handler | 8 seconds |
| Internal component orchestration | 6 seconds |
| External provider call | 3 seconds |
| Database query target | 500 ms for interactive paths |
| Redis operation target | 100 ms |

These are design defaults, not universal constants. Each integration must document its own measured limits.

## 18. Retry matrix

| Operation | Retry allowed | Notes |
|---|---|---|
| GET catalog projection | Yes | Small bounded retry for transient infrastructure failure |
| Password authentication | No automatic retry | User controls retry |
| Refresh-token rotation | No blind retry | Requires idempotent request handling |
| Progress upsert | Yes | Must use operation ID or version |
| Provider receipt verification | Yes | Bounded, only for transient errors |
| Push notification delivery | Yes | Exponential backoff and dead-letter queue |
| Media processing | Yes | Job must be idempotent |
| Account deletion task | Yes | Step-level checkpointing required |
| Validation failure | No | Deterministic failure |
| Authorization failure | No | Fail immediately |

## 19. Runtime anti-patterns

The following are prohibited:

- calling external providers inside an open database transaction;
- publishing messages before the authoritative transaction commits;
- synchronous notification delivery in a user-facing request;
- streaming audio through the Spring Boot API under normal operation;
- loading complete entities for list screens;
- unbounded retries;
- retrying non-idempotent commands without a key;
- using Redis as the sole source of truth;
- relying on active-profile cache as authorization proof;
- logging tokens, passwords, PINs, receipts, or private child data.

## 20. Runtime review checklist

Before approving a new runtime flow, verify:

- [ ] The initiating actor and entry point are clear.
- [ ] Authorization occurs at the correct boundary.
- [ ] Profile and resource ownership are validated.
- [ ] The transaction boundary is explicit.
- [ ] External calls occur outside database transactions.
- [ ] Message publication uses the outbox pattern where required.
- [ ] Idempotency behavior is documented.
- [ ] Timeout and retry behavior are documented.
- [ ] Cache failure behavior is defined.
- [ ] Partial failure behavior is defined.
- [ ] Correlation and trace context are propagated.
- [ ] Sensitive information is excluded from logs.
- [ ] Metrics and alerting signals are identified.
- [ ] The mobile client can recover from network interruption.
- [ ] The flow remains valid if it is later split across microservices.

## 21. Related documents

- `../Software_Architecture.md`
- `../Backend_Architecture.md`
- `../Mobile_Architecture.md`
- `../API_Specification.md`
- `../Database_Design.md`
- `../Security_Architecture.md`
- `../Logging_Monitoring.md`
- `../Notifications.md`
- `01_System_Context.md`
- `02_Container_Diagram.md`
- `03_Component_Diagram.md`
- `04_Code_Diagram.md`
- `05_Deployment_Diagram.md`
