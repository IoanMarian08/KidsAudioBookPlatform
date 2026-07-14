# Backend Architecture

Version: 1.0.0  
Status: Draft for implementation  
Owner: Architecture  
Last updated: 2026-07-14

## 1. Purpose

This document defines the backend architecture for KidsAudioBookPlatform. It translates the product vision and high-level software architecture into implementation rules for the Java and Spring Boot backend.

The intended audience is backend developers, reviewers, DevOps engineers, QA engineers and AI coding agents working in the repository. The document is prescriptive: where it uses **must**, the rule is mandatory unless an Architecture Decision Record explicitly replaces it.

The backend must support a child-first mobile experience, a protected parent experience, content administration, subscriptions, offline listening, persisted notifications, analytics and future expansion toward author tooling without exposing unnecessary complexity in the first release.

## 2. Architectural goals

The backend is designed to achieve the following goals:

1. Clear domain ownership and low coupling between business capabilities.
2. Secure handling of parent accounts, child profiles and administrative operations.
3. Reliable playback and content delivery even under unstable mobile connectivity.
4. Independent evolution of content, identity, subscription and notification capabilities.
5. Strong observability through structured logs, metrics, traces and audit records.
6. Predictable APIs suitable for Flutter, the admin dashboard and future clients.
7. Safe incremental delivery without requiring a distributed system from day one.
8. A migration path from a modular monolith to separately deployable services where justified.
9. High testability and explicit business rules.
10. Operational simplicity for the MVP.

## 3. Recommended implementation strategy

The target architecture is service-oriented, but the initial implementation should be a **modular monolith with strict bounded contexts**, packaged so that selected modules can later become independent microservices.

This is an intentional decision. Starting with many independently deployed services would introduce network failures, distributed transactions, service discovery, duplicated infrastructure and operational overhead before the product has validated its usage patterns.

The modular monolith must not become an unstructured monolith. Each domain module owns its application services, domain model, persistence adapters and public contracts. Direct access to another module's repositories or internal entities is forbidden.

The recommended evolution is:

| Stage | Deployment model | Main objective |
|---|---|---|
| MVP | One Spring Boot deployment, one PostgreSQL cluster, Redis, object storage | Deliver product safely and quickly |
| Growth | Extract media/content delivery and notifications where load requires it | Isolate scaling and operational concerns |
| Scale | Extract identity, subscription and analytics only when organizational or scaling evidence exists | Independent ownership and release cycles |

## 4. Technology baseline

The backend baseline is:

- Java 21
- Spring Boot 3.x
- Maven
- Spring Web MVC for synchronous HTTP APIs
- Spring Security
- Spring Data JPA
- PostgreSQL
- Flyway for database migrations
- Redis for caching, rate-limit coordination and short-lived state
- RabbitMQ for asynchronous domain and integration events
- S3-compatible object storage for audio, images and downloadable packages
- OpenAPI 3 for API documentation
- Micrometer for metrics
- OpenTelemetry-compatible tracing
- Testcontainers for integration tests
- JUnit 5, AssertJ and Mockito

New infrastructure dependencies require an ADR and a measurable use case.

## 5. Backend bounded contexts

### 5.1 Identity and Access

Responsibilities:

- Parent account registration and authentication
- Email verification and password recovery
- Access and refresh token lifecycle
- Role and permission evaluation
- Parent-zone PIN metadata and verification flow
- Device and session management
- Administrative identity and authorization
- Security events such as suspicious login attempts

This context does not own child preferences, story progress or subscription billing records.

### 5.2 Family and Profiles

Responsibilities:

- Parent household representation
- Child profile creation and lifecycle
- Profile avatar, display name and age range
- Language and accessibility preferences
- Parental controls
- Profile limits based on subscription entitlement
- Child-specific listening preferences

A child profile is never an authentication principal. The authenticated principal is the parent account or an administrator. Child actions are performed in the context of a selected profile.

### 5.3 Content Catalog

Responsibilities:

- Stories, series and episodes
- Categories, collections and age recommendations
- Localized metadata
- Publication workflow
- Content visibility and entitlement classification
- Audio tracks, synchronized text and illustrations
- Ambient sound metadata
- Search and discovery metadata

Draft and editorial records are isolated from published read models.

### 5.4 Media

Responsibilities:

- Upload orchestration
- File validation and malware-scanning status
- Media metadata
- Transcoding status
- Signed upload and download URLs
- Audio variants and image variants
- Offline package manifests
- CDN-facing asset references

Binary media must not be stored in PostgreSQL. PostgreSQL stores metadata and references only.

### 5.5 Listening and Progress

Responsibilities:

- Playback sessions
- Resume position
- Episode completion
- Continue-listening feed
- Listening history
- Favorites
- Lightweight engagement events required by product behavior

Progress updates must be idempotent and tolerant of delayed synchronization from offline devices.

### 5.6 Subscription and Entitlements

Responsibilities:

- Free, trial and premium entitlement state
- Monthly and annual plan representation
- App-store purchase verification
- Subscription lifecycle events
- Trial eligibility
- Feature entitlement evaluation
- Grace periods and expiry

The backend stores the authoritative entitlement state used by APIs. It must not trust a premium flag supplied by a mobile client.

### 5.7 Advertising Policy

Responsibilities:

- Decide whether the free experience is eligible for an advertisement
- Track completed listening sessions relevant to the two-session rule
- Ensure advertisements are never inserted during a story
- Persist ad decision tokens where needed
- Support suppression after premium activation

The backend returns policy decisions; the mobile client remains responsible for rendering the supported ad provider experience.

### 5.8 Notifications

Responsibilities:

- Persist notifications per user
- Notification templates
- Delivery status
- Push provider integration
- In-app inbox
- User preferences
- Administrative announcements, offers and discounts

Business modules request notifications through events or an application contract. They must not integrate directly with push providers.

### 5.9 Administration

Responsibilities:

- Administrative workflows that span domain contexts
- Dashboard-specific read models
- Content moderation and publishing actions
- User support actions
- Subscription inspection
- Announcement management
- Audit search

The administration context does not bypass domain rules. It invokes application use cases exposed by the owning module.

### 5.10 Analytics

Responsibilities:

- Accept privacy-conscious product events
- Aggregate operational product indicators
- Build anonymized or pseudonymized reporting views
- Enforce event retention policies

Analytics must not become part of synchronous critical paths for login, playback or content browsing.

## 6. Module structure

The repository should use a structure similar to:

```text
backend/
  pom.xml
  application/
  modules/
    identity/
    family/
    catalog/
    media/
    listening/
    subscription/
    advertising/
    notification/
    administration/
    analytics/
  shared/
    kernel/
    web/
    security/
    observability/
    testing/
```

Each domain module follows this internal structure:

```text
<module>/
  api/
    rest/
    dto/
    mapper/
  application/
    command/
    query/
    service/
    port/
  domain/
    model/
    event/
    policy/
    exception/
  infrastructure/
    persistence/
    messaging/
    integration/
    configuration/
```

### 6.1 Dependency direction

Dependencies point inward:

```text
API -> Application -> Domain
Infrastructure -> Application/Domain contracts
```

The domain layer must not import Spring, JPA, web, messaging or provider SDK types.

Application services coordinate use cases and transactions. They do not contain HTTP concerns.

Infrastructure adapters implement ports owned by the application or domain layer.

## 7. Domain modeling rules

### 7.1 Aggregates

An aggregate defines a consistency boundary. All changes to an aggregate must pass through its root.

Examples:

- ParentAccount
- Household
- ChildProfile
- Story
- Series
- PlaybackProgress
- Subscription
- Notification

Aggregates should remain small. A Story aggregate should not load all audio binary metadata, listening history and every localized asset into one object graph.

### 7.2 Entities and value objects

Value objects should be preferred for validated domain concepts, for example:

- EmailAddress
- ChildProfileId
- StoryId
- AgeRange
- LocaleCode
- PlaybackPosition
- SubscriptionPeriod
- MediaAssetId

Identifiers must use immutable, non-sequential externally visible values such as UUIDs. Database-generated numeric identifiers may exist internally only when they are not exposed.

### 7.3 Domain services and policies

Use domain services only when a business rule does not naturally belong to one aggregate. Use policy objects for decisions such as:

- CanCreateChildProfile
- IsStoryAvailableForProfile
- CanStartPremiumTrial
- ShouldDisplayAdvertisement
- CanDownloadOffline

Policies must be unit-testable without Spring.

### 7.4 Domain events

Domain events describe facts that have already occurred:

- ParentRegistered
- ChildProfileCreated
- StoryPublished
- PlaybackSessionCompleted
- SubscriptionActivated
- SubscriptionExpired
- NotificationRequested

Event names use past tense. Events must be immutable and versioned when published outside the owning module.

## 8. Application layer

Each application use case is represented by a command or query handler.

Commands change state. Queries return data without changing business state.

Example command:

```java
public record CreateChildProfileCommand(
        UUID parentAccountId,
        String displayName,
        LocalDate birthDate,
        String avatarKey,
        String locale
) {}
```

Example use case contract:

```java
public interface CreateChildProfileUseCase {
    ChildProfileResult execute(CreateChildProfileCommand command);
}
```

Application services are responsible for:

- Loading aggregates through repository ports
- Performing authorization checks that require domain context
- Invoking domain behavior
- Persisting the result
- Registering integration events
- Returning application results

Controllers must not orchestrate repositories directly.

## 9. API layer

### 9.1 API style

Public APIs are RESTful JSON APIs under:

```text
/api/v1
```

Administrative APIs are separated:

```text
/api/v1/admin
```

Internal service callbacks use:

```text
/internal/v1
```

Internal endpoints must be protected with service credentials or network-level controls and must never rely only on obscurity.

### 9.2 Controller rules

Controllers must:

- Validate transport-level input
- Resolve the authenticated principal
- Convert DTOs into commands or queries
- Invoke exactly one application use case where practical
- Convert results into response DTOs
- Avoid business logic
- Avoid direct repository access

### 9.3 DTO rules

API DTOs are separate from domain entities and persistence entities.

Request DTOs use Bean Validation for structural rules. Domain validation remains in the domain model.

Example:

```java
public record CreateChildProfileRequest(
        @NotBlank @Size(max = 40) String displayName,
        @Past LocalDate birthDate,
        @NotBlank String avatarKey,
        @NotBlank String locale
) {}
```

### 9.4 Response envelope

Successful resource responses may return the resource directly. Collection responses must include pagination metadata.

```json
{
  "items": [],
  "page": {
    "number": 0,
    "size": 20,
    "totalElements": 0,
    "totalPages": 0
  }
}
```

Errors use one consistent problem format based on RFC 9457 concepts:

```json
{
  "type": "https://kidsaudiobook.app/problems/profile-limit-reached",
  "title": "Profile limit reached",
  "status": 409,
  "code": "FAMILY_PROFILE_LIMIT_REACHED",
  "detail": "The current subscription allows one child profile.",
  "instance": "/api/v1/child-profiles",
  "correlationId": "4eb2e274-4d34-4cd6-9737-a83a3161e70f",
  "violations": []
}
```

Internal stack traces must never be returned to clients.

### 9.5 Pagination and sorting

All potentially unbounded collections must be paginated. API page size defaults to 20 and should have a maximum of 100 unless a documented endpoint requires otherwise.

Stable sorting must include a unique tie-breaker.

Cursor pagination is preferred for high-volume chronological feeds such as listening history and notifications. Offset pagination is acceptable for small administrative tables.

### 9.6 Idempotency

Endpoints that may be retried by mobile clients must support idempotency where duplicate processing would be harmful.

Examples:

- Playback session completion
- Purchase verification
- Notification acknowledgement
- Administrative publish actions

Clients supply an `Idempotency-Key`. The backend stores the key, request fingerprint and result for a bounded retention period.

## 10. Authentication and authorization integration

### 10.1 Tokens

Access tokens must be short-lived. Refresh tokens must be rotated and revocable.

Refresh tokens should be represented server-side by a hashed token identifier. Raw refresh tokens must not be logged or persisted in plain text.

### 10.2 Roles

Initial platform roles:

- PARENT
- CONTENT_EDITOR
- CONTENT_REVIEWER
- SUPPORT_AGENT
- ADMIN
- SYSTEM

Roles are coarse-grained. Application permissions provide finer control, for example:

- story:create
- story:publish
- user:read
- user:suspend
- subscription:read
- announcement:manage

### 10.3 Resource authorization

Role checks alone are insufficient. Every household and profile operation must confirm resource ownership.

A parent may access only child profiles belonging to the authenticated household. An identifier supplied in a URL is never proof of authorization.

### 10.4 Parent-zone protection

The parent-zone PIN is an additional product protection, not a replacement for account authentication.

The backend should support a short-lived parent-zone authorization claim after successful PIN verification. PIN verification attempts must be rate-limited and audited. PIN values must be stored using a password-grade hashing algorithm.

Biometric verification occurs on the device. The backend trusts only a valid device-authenticated flow or short-lived token defined in the mobile security design; it does not receive biometric data.

## 11. Persistence architecture

### 11.1 Database ownership

In the modular monolith, modules may share one PostgreSQL cluster but must own separate schemas or clearly isolated table namespaces.

One module must not query another module's tables directly. Cross-module data access occurs through application contracts or replicated read models.

### 11.2 JPA entity rules

Persistence entities are infrastructure concerns and must not leak into API responses.

Rules:

- Avoid eager relationships by default
- Avoid large bidirectional object graphs
- Use explicit fetch plans
- Detect and prevent N+1 queries
- Use optimistic locking for concurrently edited aggregates
- Store timestamps in UTC
- Use database constraints in addition to application validation
- Never use schema auto-generation in production

### 11.3 Transactions

Each command use case normally executes within one local database transaction.

Transactions should be short and must not contain remote network calls.

For workflows requiring a database change and event publication, use the transactional outbox pattern.

```text
Business transaction:
1. Update aggregate state
2. Insert outbox record
3. Commit

Publisher:
4. Read pending outbox records
5. Publish to RabbitMQ
6. Mark as published
```

### 11.4 Migrations

Flyway migrations are immutable after they have been applied to a shared environment.

Migration rules:

- One logical change per migration where practical
- Backward-compatible changes before code that depends on them
- Separate destructive cleanup into later releases
- Index creation assessed for production locking impact
- Data migrations written to be restartable or safely repeatable

## 12. Caching

Caching is an optimization, never the source of truth.

Recommended cache candidates:

- Published story metadata
- Category and collection lists
- Feature entitlement snapshots with short TTL
- Public configuration
- Rate-limit counters
- Short-lived signed media URL metadata

Do not cache highly sensitive account data without an explicit security review.

Cache keys must be namespaced and versioned:

```text
catalog:v1:story:{storyId}:{locale}
family:v1:profile-summary:{profileId}
subscription:v1:entitlements:{accountId}
```

Cache invalidation should occur after a successful transaction, generally through events. TTL is still required as a safety mechanism.

Cache stampede protection should be used for high-traffic catalog entries.

## 13. Messaging and asynchronous processing

RabbitMQ is used for asynchronous work and cross-module integration events where eventual consistency is acceptable.

Suitable use cases:

- Notification requests
- Media processing status
- Analytics ingestion
- Search index updates
- Subscription lifecycle propagation
- Cache invalidation
- Administrative audit enrichment

Unsuitable use cases:

- Immediate authorization decisions
- Reading playback progress during resume
- Operations requiring the caller to know success immediately

### 13.1 Event envelope

```json
{
  "eventId": "0d24f240-f990-4dc6-bb46-f56f9bd85231",
  "eventType": "story.published.v1",
  "occurredAt": "2026-07-14T18:45:00Z",
  "correlationId": "8214e8b8-a643-42b3-ab1f-fb2fe55791ef",
  "causationId": "5c33d8f9-ed88-481c-a42b-980b53d19a19",
  "producer": "catalog",
  "payload": {}
}
```

Consumers must be idempotent. At-least-once delivery is assumed.

### 13.2 Retry and dead-letter policy

Transient failures use bounded retries with exponential backoff. Permanent failures are moved to a dead-letter queue with enough metadata for diagnosis and safe replay.

Poison messages must not block a queue indefinitely.

## 14. Media architecture

The backend coordinates media workflows but does not stream large files through application servers unless a specific security requirement demands it.

Recommended upload flow:

```text
Admin requests upload slot
-> backend validates metadata and permission
-> backend creates pending media record
-> backend returns signed object-storage upload URL
-> browser uploads directly
-> storage event or callback starts validation/transcoding
-> media status becomes READY
-> content editor may attach asset to draft content
```

Recommended playback flow:

```text
Mobile requests playable asset
-> backend validates story visibility and entitlement
-> backend returns CDN-backed signed URL or manifest
-> mobile streams directly from CDN/object storage
```

Uploads must validate content type, extension, signature, maximum size and scan status. The client-provided MIME type is not trusted.

## 15. Offline listening

Premium users may download eligible content for offline use.

The backend should issue an offline package manifest containing:

- Story or episode identifier
- Media asset references
- Content version
- Expiry or license-check policy
- Checksums
- Required locale assets
- Synchronized text version
- Illustration versions

The mobile application stores encrypted or platform-protected media where practical. The server does not promise absolute prevention of copying, but it must avoid publishing permanent unrestricted premium URLs.

Offline progress synchronization must use timestamps, sequence values or revision numbers to resolve delayed updates. The chosen conflict rule must favor preserving the furthest legitimate playback position while allowing explicit restart actions.

## 16. Subscription verification

App-store receipts or purchase tokens must be verified server-side with the relevant provider.

The mobile client must never directly set subscription status.

Purchase verification must be idempotent and auditable. Provider notifications should update subscription state asynchronously.

The entitlement service should expose a compact result:

```json
{
  "plan": "PREMIUM_ANNUAL",
  "status": "ACTIVE",
  "trial": false,
  "expiresAt": "2027-07-14T00:00:00Z",
  "features": [
    "MULTIPLE_PROFILES",
    "OFFLINE_DOWNLOADS",
    "NO_ADS"
  ]
}
```

Business modules should depend on feature entitlements rather than hard-coding plan names.

## 17. Validation strategy

Validation occurs at multiple layers:

| Layer | Responsibility |
|---|---|
| API | Required fields, formatting, size limits, syntactic validity |
| Application | Actor context, use-case preconditions, orchestration constraints |
| Domain | Business invariants |
| Database | Uniqueness, nullability, referential integrity, check constraints |
| Infrastructure | File signatures, provider responses, integration limits |

Validation messages exposed to clients must be safe, actionable and localized by the client when appropriate.

## 18. Exception handling

Exceptions are categorized:

- ValidationException
- ResourceNotFoundException
- ConflictException
- AuthorizationException
- AuthenticationException
- RateLimitException
- ExternalServiceException
- InfrastructureException

Domain exceptions must use stable error codes. Controllers rely on a global exception handler to map exceptions to API problems.

Catching `Exception` in business code is prohibited unless the code immediately converts it into a meaningful infrastructure boundary exception and preserves the cause.

## 19. Resilience

All outbound calls must define:

- Connection timeout
- Response timeout
- Retry policy
- Circuit-breaker policy when appropriate
- Maximum concurrency or bulkhead
- Observability tags

Retries are permitted only for operations known to be safe or idempotent.

Fallbacks must not silently grant access, premium entitlement or administrative permissions.

External-provider degradation should not unnecessarily block already-authorized playback when a cached valid entitlement remains within an approved grace period.

## 20. Rate limiting and abuse prevention

Rate limits should exist for:

- Login
- Registration
- Password reset
- Email verification resend
- Parent PIN verification
- Search
- Signed media URL generation
- Upload creation
- Purchase verification
- Administrative bulk actions

Limits may combine account, IP, device and endpoint keys. Responses use HTTP 429 and include a safe retry indication.

Bot protection may be added to public account flows. It must remain accessible and should not be imposed on every normal authenticated mobile request.

## 21. Logging

Logs must be structured JSON in deployed environments.

Every request should include:

- timestamp
- level
- service/module
- correlationId
- traceId
- requestId
- actor type and pseudonymous actor ID where allowed
- HTTP method
- route template
- status
- duration

Never log:

- Passwords or PINs
- Access or refresh tokens
- Raw app-store receipts
- Full payment data
- Private media URLs with credentials
- Sensitive child information
- Request bodies by default

Business events worth logging include publication, subscription state change, profile lifecycle changes and administrative actions. Detailed rules belong in `Logging_Monitoring.md`.

## 22. Audit logging

Security and administrative audit records are distinct from operational logs and require longer retention and controlled access.

Audit records include:

- Actor
- Action
- Target type and ID
- Timestamp
- Outcome
- Reason when supplied
- Correlation ID
- Before/after summary for approved fields

Administrative audit entries must be append-only from the application's perspective.

## 23. Metrics and tracing

Minimum backend metrics:

- HTTP request rate, duration and error ratio
- JVM and connection-pool metrics
- Database query and transaction indicators
- Cache hit ratio
- Queue depth and consumer failures
- Outbox backlog
- Media processing duration
- Login and verification failure counts
- Playback-progress update latency
- Purchase verification outcomes
- Notification delivery outcomes

Distributed traces must propagate correlation through HTTP and RabbitMQ message headers.

High-cardinality values such as raw user IDs must not be metric labels.

## 24. Configuration and secrets

Configuration follows environment-specific externalization.

Rules:

- No secrets in Git
- Secrets provided by environment or secret manager
- Typed configuration properties with validation
- Safe defaults for local development only
- Startup failure when mandatory production configuration is absent
- Feature flags used for controlled rollout, not permanent branching logic

Sensitive configuration changes must be auditable operationally.

## 25. API documentation

Every externally callable endpoint must appear in generated OpenAPI documentation.

OpenAPI descriptions must include:

- Purpose
- Authentication requirements
- Required permissions
- Request and response schema
- Validation constraints
- Error responses
- Pagination behavior
- Idempotency behavior where relevant

Every public Java class, public method, controller, DTO and non-obvious configuration component requires useful JavaDoc. JavaDoc must explain intent and contracts rather than repeat the method name.

## 26. Testing architecture

### 26.1 Unit tests

Unit tests cover:

- Domain invariants
- Policies
- Value objects
- Application orchestration with mocked ports
- Mapping and validation edge cases

### 26.2 Module integration tests

Use Spring Boot tests selectively for:

- Security rules
- Controller serialization
- Persistence mappings
- Transaction behavior
- Outbox publication
- Cache behavior

### 26.3 Infrastructure integration tests

Testcontainers should run PostgreSQL, Redis and RabbitMQ for meaningful integration tests. Do not replace all integration behavior with in-memory substitutes that differ from production.

### 26.4 Contract tests

API contracts and integration-event schemas must be validated. Breaking contract changes require a new API or event version and a migration plan.

### 26.5 Architecture tests

Use ArchUnit or equivalent checks to enforce:

- Module boundaries
- Dependency direction
- Controller restrictions
- Domain independence from Spring/JPA
- Naming conventions
- Prohibition of cross-module repository access

## 27. Code quality rules

- Constructor injection only
- Immutable DTOs and value objects where possible
- No field injection
- No static mutable state
- No generic utility dumping ground
- No direct use of `LocalDateTime.now()` in domain logic; inject a Clock
- No hidden database access from mappers or serializers
- No returning `null` collections
- Avoid boolean parameters that obscure intent
- Prefer explicit types over unstructured maps
- Avoid premature abstraction across unrelated domains
- Keep methods focused and readable

Shared code must represent a truly shared technical concern. Domain concepts are not moved into `shared` merely because two modules use similar words.

## 28. Deployment and runtime profile

The initial backend is packaged as one container image.

It may run multiple replicas behind a load balancer. Therefore:

- Application instances must be stateless
- Session state must not live in process memory
- Scheduled work requires distributed coordination
- Idempotency state must be shared
- Uploaded files must not depend on local disk
- Graceful shutdown must stop accepting work and complete in-flight requests within a bounded interval

Health endpoints:

- Liveness: process can continue running
- Readiness: instance can serve traffic
- Startup: initialization has completed

Readiness should account for mandatory dependencies but avoid cascading total outages due to optional integrations.

## 29. Future service extraction criteria

A module may be extracted into a separately deployed service when at least one of the following is true:

- It requires materially different scaling characteristics
- It has a distinct availability target
- It has a dedicated team and independent release cadence
- It creates deployment contention in the monolith
- Security or regulatory isolation requires it
- Its technology requirements cannot be satisfied reasonably in the current runtime

Extraction is not justified only because the target architecture mentions microservices.

Likely early extraction candidates:

1. Media processing
2. Notifications
3. Analytics ingestion

Identity and subscription extraction should occur only with strong operational justification because they participate in many critical flows.

## 30. Initial implementation milestones

### Milestone 1: Foundation

- Spring Boot application skeleton
- Module boundaries
- Shared error model
- Security baseline
- PostgreSQL and Flyway
- Structured logging and correlation IDs
- OpenAPI
- Testcontainers

### Milestone 2: Identity and family

- Parent registration and login
- Refresh token rotation
- Household and child profiles
- Parent-zone PIN
- Authorization tests

### Milestone 3: Catalog and media

- Draft/published content model
- Categories, stories, series and episodes
- Signed uploads
- Media validation state
- Public catalog APIs

### Milestone 4: Listening

- Playback authorization
- Resume progress
- Continue listening
- Favorites and history
- Offline manifest groundwork

### Milestone 5: Monetization

- Entitlements
- Trial lifecycle
- Store verification adapters
- Advertisement policy
- Offline premium authorization

### Milestone 6: Administration and communication

- Admin APIs
- Publish workflow
- Persisted notifications
- Announcements and offers
- Audit search

## 31. Definition of done for backend features

A backend feature is not complete until:

- Business rules are represented explicitly
- Authentication and resource authorization are implemented
- API and error contracts are documented
- Database migrations are included
- Unit and integration tests cover success and important failure paths
- Logs and metrics support production diagnosis
- Sensitive data handling has been reviewed
- Idempotency and retry behavior have been considered
- Module boundaries remain intact
- Relevant architecture documentation and changelog entries are updated

## 32. Open decisions

The following decisions should receive dedicated ADRs before implementation is finalized:

1. Exact identity provider strategy: first-party credentials only or external identity provider.
2. App-store verification library/provider selection.
3. Object storage and CDN providers.
4. Audio transcoding pipeline.
5. Search implementation: PostgreSQL search initially versus dedicated search engine.
6. Exact analytics event retention and child-privacy model.
7. Offline license expiry and refresh behavior.
8. Notification push provider abstraction.
9. Whether module schemas share one database user or use per-schema credentials.

Until an ADR replaces them, the defaults in this document apply.

## 33. Related documents

- `Architecture_Principles.md`
- `Software_Architecture.md`
- `Database_Design.md`
- `API_Specification.md`
- `Security_Architecture.md`
- `Performance_Guidelines.md`
- `Logging_Monitoring.md`
- `Notifications.md`
- `Mobile_Architecture.md`
- `Admin_Dashboard.md`

## 34. Final rule

The backend must optimize for correctness, safety and clarity before distribution complexity. A well-structured modular application is preferred over a network of poorly defined services. Service boundaries are earned through domain clarity and operational evidence.