# Architecture Principles

Version: 1.0.0  
Status: Active Draft  
Owner: Project Architecture  
Last updated: 2026-07-14

## 1. Purpose

This document defines the architectural constitution of KidsAudioBookPlatform. It establishes the rules that every backend service, mobile feature, administrative capability, data model, API, event, deployment, and operational process must follow.

The purpose is not to prescribe implementation details for every class. The purpose is to make important decisions explicit so that future implementation does not depend on guesswork, personal preference, or inconsistent assumptions.

These principles apply to:

- the Spring Boot backend;
- the Flutter mobile application;
- the administrative dashboard;
- databases, caches, queues, object storage, and delivery infrastructure;
- authentication, authorization, subscriptions, notifications, and content workflows;
- CI/CD, monitoring, support, and incident response;
- future services and integrations.

When a design decision conflicts with this document, one of two things must happen:

1. the design must change; or
2. the principle must be formally amended through an Architecture Decision Record.

Silent exceptions are not allowed.

## 2. Product Context

KidsAudioBookPlatform is a child-focused mobile storytelling platform with a parent-controlled account model. The system must support audio stories, synchronized text, illustrations, collections, series, episodes, child profiles, parental controls, subscriptions, free and premium access, offline use, ambient sounds, advertisements for eligible free users, and an administrative content workflow.

The platform serves two very different experience domains:

- **Child Experience** — simple, calm, safe, visual, low-friction, and intentionally limited;
- **Parent Zone** — protected, explicit, auditable, configurable, and information-rich.

The architecture must preserve this separation at the domain, API, authorization, telemetry, and user-experience levels.

The product principles are:

- **Child First**;
- **Parent in Control**;
- **Magic Without Complexity**.

The platform motto is:

> A safe world where every evening begins with a story.

Architecture exists to protect this promise.

## 3. Decision Hierarchy

When several valid technical choices exist, decisions must be evaluated in this order:

1. child safety and privacy;
2. data integrity and security;
3. availability of core listening functionality;
4. product correctness;
5. maintainability and operational clarity;
6. performance and scalability;
7. development speed;
8. infrastructure cost;
9. implementation convenience.

A faster implementation is not preferred when it weakens security, correctness, auditability, or long-term maintainability.

## 4. Architecture Style

The strategic target is a service-oriented architecture with independently understandable bounded contexts and clear ownership. The initial implementation may deploy some capabilities together where this reduces operational complexity, but the internal boundaries must remain explicit.

The project must avoid both extremes:

- a single unstructured monolith with tightly coupled modules;
- premature fragmentation into dozens of operationally expensive microservices.

The preferred evolution model is:

1. define bounded contexts;
2. implement strong module boundaries;
3. deploy together where appropriate;
4. extract independently deployable services only when there is a clear scaling, ownership, security, or release benefit.

Service extraction must be justified through an ADR.

## 5. Bounded Contexts

The initial domain decomposition is:

| Context | Responsibility |
|---|---|
| Identity and Access | Parent accounts, authentication, sessions, roles, account security |
| Profile Management | Child profiles, preferences, age range, avatars, parental settings |
| Content Catalog | Stories, series, episodes, categories, collections, metadata, availability |
| Media Delivery | Audio, illustrations, text synchronization assets, signed access, CDN integration |
| Playback and Progress | Listening sessions, progress, resume position, completion, history |
| Entitlements | Free access, premium access, trials, feature eligibility |
| Subscriptions and Billing | Plans, purchases, renewals, provider callbacks, subscription state |
| Advertising Eligibility | Ad policy, frequency control, session-based eligibility, safe placement |
| Downloads and Offline | Download manifests, device authorization, expiry, offline entitlement checks |
| Ambient Audio | White noise and soundscape catalog, playback configuration, mixing preferences |
| Notifications | In-app notifications, push orchestration, preferences, delivery state |
| Administration | Content operations, user support, subscriptions, campaigns, moderation, audit access |
| Audit and Compliance | Security-sensitive audit records, administrative activity, retention controls |
| Analytics | Privacy-safe product events, aggregated usage, content performance |

These contexts may initially exist as modules rather than separate deployments. Their contracts must remain independent of deployment topology.

## 6. Ownership and Data Boundaries

Each bounded context owns its business rules and authoritative data.

A service or module must not directly write another context's tables. Direct cross-context database access is prohibited.

Read access to another context's database is also prohibited unless explicitly approved in an ADR for a temporary migration or reporting use case.

Cross-context data must be obtained through:

- a synchronous API;
- an asynchronous event;
- a purpose-built read model;
- a controlled data export.

Ownership examples:

- Identity owns parent account status and credentials.
- Profile Management owns child profile settings.
- Content Catalog owns story publication state.
- Playback owns listening progress.
- Entitlements owns effective feature eligibility.
- Billing owns payment-provider transactions and subscription lifecycle.

No other context may redefine these truths.

## 7. API-First Design

All externally consumed backend capabilities must be designed contract-first.

Before implementation, the contract must define:

- endpoint purpose;
- authentication and authorization requirements;
- request and response models;
- validation rules;
- error codes;
- idempotency behavior;
- pagination behavior;
- versioning expectations;
- security-sensitive fields;
- observability requirements.

OpenAPI is the canonical synchronous API description. The Markdown API specification explains intent, rules, workflows, and examples that are not sufficiently expressive in OpenAPI alone.

API implementation and documentation must not drift. CI should eventually validate that generated OpenAPI is compatible with the reviewed contract.

## 8. REST Usage

REST is the default communication style for:

- mobile-to-backend requests;
- admin-dashboard-to-backend requests;
- queries requiring an immediate response;
- commands whose caller must know whether the operation was accepted;
- integration callbacks where the external provider supports HTTP.

REST endpoints must represent resources or explicit business actions. They must not expose internal class structure.

Good examples:

```text
GET  /v1/profiles/{profileId}/continue-listening
POST /v1/stories/{storyId}/playback-sessions
POST /v1/admin/stories/{storyId}/publish
```

Avoid vague RPC-style endpoints such as:

```text
POST /v1/doAction
POST /v1/processData
POST /v1/updateEverything
```

## 9. Asynchronous Messaging

Asynchronous events are preferred when:

- the producer does not require an immediate business response;
- several consumers may react independently;
- eventual consistency is acceptable;
- work is slow, retryable, or operationally isolated;
- the event represents a meaningful business fact.

Examples include:

- `StoryPublished`;
- `PlaybackSessionCompleted`;
- `SubscriptionActivated`;
- `SubscriptionExpired`;
- `ChildProfileDeleted`;
- `NotificationRequested`;
- `OfflineDownloadRevoked`.

RabbitMQ is the initial message broker unless an ADR selects another technology.

Events must describe facts that already happened. Commands and events must not be confused.

Bad event name:

```text
PublishStory
```

Preferred event name:

```text
StoryPublished
```

## 10. Event Contract Rules

Every event must include:

```json
{
  "eventId": "uuid",
  "eventType": "SubscriptionActivated",
  "eventVersion": 1,
  "occurredAt": "2026-07-14T18:30:00Z",
  "correlationId": "uuid",
  "causationId": "uuid-or-null",
  "producer": "subscription-service",
  "payload": {}
}
```

Required rules:

- event IDs are globally unique;
- timestamps are UTC;
- schemas are versioned;
- consumers must tolerate additional fields;
- personally identifiable data must be minimized;
- secrets and payment credentials must never appear in events;
- event consumers must be idempotent;
- failed delivery must support retry and dead-letter handling;
- event publication must not be lost after a successful database transaction.

The transactional outbox pattern is the preferred solution for reliable event publication.

## 11. Consistency Model

Strong consistency is required inside a single aggregate transaction.

Eventual consistency is acceptable across bounded contexts when:

- the temporary inconsistency is understood;
- the user experience remains safe;
- the system can recover automatically;
- operations are idempotent;
- monitoring detects stalled propagation.

Examples:

- A newly published story may appear in recommendations a few seconds after becoming available.
- An expired subscription must stop granting premium access within a clearly defined maximum delay.
- A deleted child profile must trigger downstream cleanup, but the initiating service remains authoritative immediately.

Security revocations require tighter propagation limits than analytical updates.

## 12. Aggregate Design

Aggregates protect business invariants. They must remain small enough to load and update efficiently.

An aggregate boundary should contain only data that must change atomically.

Examples:

- a subscription and its lifecycle transitions may be one aggregate;
- a complete story catalog with all categories and collections must not be one aggregate;
- playback progress for each profile-story pair may be independently updated;
- publication state changes must validate required content assets before transition.

Cross-aggregate workflows must use orchestration, events, or explicit process managers rather than oversized transactions.

## 13. Database Principles

PostgreSQL is the default relational database.

Each independently deployed service must own its schema or database. Shared tables across services are prohibited.

Database rules:

- use explicit primary keys;
- prefer UUIDs for externally visible identifiers;
- define foreign keys inside a service boundary where operationally practical;
- use unique constraints for business uniqueness;
- use check constraints for simple invariant enforcement;
- index real query patterns, not hypothetical ones;
- store timestamps in UTC;
- avoid unbounded text or JSON usage without a clear reason;
- use JSONB only for genuinely flexible structures, not to avoid modeling;
- use migrations for every schema change;
- never modify production schemas manually.

Flyway is the preferred migration tool.

## 14. Identifier Rules

Public resource identifiers must not expose sequential internal database IDs.

Preferred identifiers:

- UUIDv7 when supported and operationally validated;
- UUIDv4 otherwise;
- stable provider IDs only inside integration-specific records.

Identifiers must be immutable.

Human-readable slugs may be used for discovery and URLs but must not replace the stable canonical identifier.

## 15. Time and Date Rules

All persisted instants use UTC.

API timestamps use ISO 8601 with an explicit zone.

Business-local dates, such as a subscription billing date, may be stored as a date when no time-of-day meaning exists.

The mobile application may display content in the user's local time zone, but backend rules must never rely on an unspecified server-local timezone.

## 16. Caching

Redis is the default distributed cache where a distributed cache is justified.

Caching is not a substitute for correct database design.

Every cache entry must define:

- owner;
- key format;
- value schema;
- TTL;
- invalidation strategy;
- acceptable staleness;
- fallback behavior;
- metrics.

Suitable cache candidates include:

- public catalog metadata;
- category and collection definitions;
- short-lived entitlement decisions;
- rate-limiting counters;
- idempotency records;
- frequently requested configuration.

Sensitive data should not be cached unless required and explicitly protected.

Cache failures must degrade predictably. Core account and billing correctness must not depend solely on cache availability.

## 17. Media and Object Storage

Audio files, illustrations, and other large assets must not be stored directly in relational database rows.

Object storage is authoritative for binary assets. The database stores metadata, state, references, checksums, and ownership.

Media delivery should use a CDN and controlled URLs.

Rules:

- private or premium media uses signed, short-lived access URLs;
- upload flows validate type, size, checksum, and content safety;
- original files are immutable;
- derived versions have explicit lineage;
- asset lifecycle changes are auditable;
- deletion follows retention and legal rules;
- clients must not learn internal storage credentials or bucket structure.

## 18. Authentication

The parent account is the authenticated security principal.

Children do not receive independent unrestricted accounts in the initial product model.

Authentication must support:

- secure account registration and login;
- access-token and refresh-token rotation;
- session revocation;
- device visibility;
- password reset;
- brute-force protection;
- suspicious activity monitoring;
- future social identity providers without coupling domain rules to one provider.

Access tokens must be short-lived. Refresh tokens must be revocable and stored securely.

## 19. Authorization

Authorization must be enforced on the server for every protected operation.

The backend must never trust the client to enforce:

- profile ownership;
- premium entitlement;
- administrative role;
- parent-zone protection;
- publication permissions;
- support access;
- discount or campaign eligibility.

Authorization should combine:

- role-based access control for broad platform roles;
- ownership checks for parent and profile resources;
- entitlement checks for premium features;
- state checks for workflow actions;
- attribute-based rules where needed.

Administrative endpoints must use separate authorization policies from consumer endpoints.

## 20. Parent Zone Protection

Parent Zone protection is a product and security boundary.

The mobile application may use a parental PIN and device biometrics. Biometrics are a local convenience mechanism, not a replacement for server authentication.

Rules:

- the parental PIN must not be stored in plaintext;
- attempts must be rate-limited;
- sensitive changes may require recent parent verification;
- child-visible flows must not expose account, payment, or administrative data;
- entering Parent Zone must produce appropriate security telemetry without recording the PIN.

## 21. Child Safety by Design

Child safety is a system-wide requirement.

The architecture must ensure:

- no direct child-to-child communication in MVP;
- no public profiles;
- no open text input in child flows unless explicitly reviewed;
- no behavioral advertising based on child profiling;
- no unsafe external links in Child Experience;
- no accidental purchase path from child screens;
- no unreviewed user-generated content;
- minimal personal data collection;
- age-appropriate analytics;
- rapid content unpublishing and revocation.

A feature that creates a new child-safety surface requires explicit security and product review.

## 22. Privacy and Data Minimization

Collect only data that is necessary for the stated product purpose.

Every personal data field must have:

- a documented purpose;
- an owner;
- a retention policy;
- an access policy;
- a deletion or anonymization path.

Child profile names may be pseudonyms. Birth dates should not be collected when an age band is sufficient.

Logs, events, metrics, and analytics must minimize personal data. Email addresses, tokens, names, and payment identifiers must not appear in unrestricted logs.

## 23. Secret Management

Secrets must never be committed to source control.

Secrets include:

- database credentials;
- signing keys;
- provider API keys;
- payment secrets;
- push-notification credentials;
- object-storage credentials;
- encryption keys.

Secrets must be supplied through a managed secret mechanism appropriate to the environment.

Local development may use environment files that are excluded from Git.

Secrets must be rotatable without rebuilding application code.

## 24. Input Validation

All external input is untrusted.

Validation must occur at the system boundary and again where domain invariants are enforced.

Validation categories include:

- syntactic validation;
- size and range validation;
- enum and state validation;
- ownership validation;
- business-rule validation;
- file validation;
- rate and abuse validation.

Validation failures must return stable machine-readable error codes without exposing internal details.

## 25. File Upload Security

Administrative uploads are high-risk operations.

The upload pipeline must support:

- authentication and role checks;
- file size limits;
- extension and MIME-type validation;
- magic-byte inspection;
- checksum generation;
- malware scanning where available;
- image and audio processing in isolated workers;
- safe generated filenames;
- quarantine before publication;
- metadata stripping where appropriate;
- rejection of executable or unsupported content;
- audit records.

A file is not publishable merely because upload succeeded.

## 26. Error Model

All APIs must use a consistent error envelope.

Example:

```json
{
  "timestamp": "2026-07-14T18:30:00Z",
  "status": 409,
  "code": "STORY_NOT_READY_FOR_PUBLICATION",
  "message": "The story cannot be published because required assets are missing.",
  "correlationId": "8a4b5f84-2f19-4c80-a24d-6e71217d3adb",
  "fieldErrors": [
    {
      "field": "audioAssetId",
      "code": "REQUIRED"
    }
  ]
}
```

Rules:

- codes are stable and documented;
- messages are safe for clients;
- stack traces are never returned;
- validation errors identify fields when appropriate;
- unexpected failures receive a correlation ID;
- internal logs preserve diagnostic context.

## 27. Exception Handling

Exceptions must represent meaningful failure categories.

Do not use exceptions for normal branching.

Expected business failures should map to explicit domain or application errors.

Infrastructure exceptions must be translated at boundaries so that database, broker, storage, or provider implementation details do not leak into public APIs.

Catch exceptions only when the code can:

- recover;
- add meaningful context;
- translate the exception;
- perform required cleanup;
- record and rethrow correctly.

Empty catch blocks are prohibited.

## 28. Idempotency

Operations that may be retried must be idempotent.

Mandatory candidates include:

- payment-provider webhooks;
- subscription activation callbacks;
- purchase verification;
- notification requests;
- event consumers;
- administrative import jobs;
- selected POST commands initiated from unreliable mobile networks.

Idempotency keys must be scoped, stored for a defined duration, and associated with the resulting operation outcome.

## 29. Pagination and Query Design

List endpoints must be paginated unless the dataset is guaranteed to remain small and bounded.

Cursor pagination is preferred for large, frequently changing collections.

Offset pagination may be used for administrative tables where direct page navigation is valuable and query volume is controlled.

Every list endpoint must define:

- stable ordering;
- default and maximum page size;
- filter behavior;
- sort fields;
- empty-result behavior;
- authorization filtering.

Unbounded list endpoints are prohibited.

## 30. API Versioning

Public APIs use URI major versioning, beginning with `/v1`.

Backward-compatible additions do not require a major version change.

Breaking changes include:

- removing fields;
- changing field meaning;
- making optional fields mandatory;
- changing enum semantics;
- changing authorization expectations;
- changing error meaning;
- changing identifier format in an incompatible way.

Breaking changes require a new major version or a controlled migration plan.

## 31. DTO Rules

API DTOs are not persistence entities and are not domain entities.

Rules:

- do not expose JPA entities directly;
- use explicit request and response models;
- keep input and output models separate when their responsibilities differ;
- document nullable and optional fields;
- avoid generic maps for stable contracts;
- use enums for controlled values;
- validate at the boundary;
- avoid leaking internal audit fields;
- keep security-sensitive fields write-only where appropriate.

Mapping must be explicit and testable.

## 32. Java and Spring Boot Standards

The backend baseline is Java 21 and Spring Boot.

Preferred practices:

- constructor injection;
- immutable DTOs where practical;
- records for suitable transport models;
- explicit transactional boundaries;
- package-by-feature or bounded-context organization;
- no field injection;
- no business logic in controllers;
- no persistence logic in controllers;
- no generic `Utils` dumping grounds;
- avoid static mutable state;
- avoid framework annotations in pure domain objects when practical;
- document public APIs and non-obvious business rules.

Controllers coordinate HTTP concerns. Application services coordinate use cases. Domain components protect business rules. Repositories handle persistence abstractions.

## 33. Mobile Architecture Principles

The Flutter application must separate:

- presentation;
- state management;
- application/use-case logic;
- domain models;
- data access;
- platform integrations.

The child experience and parent zone must have explicit navigation and authorization boundaries.

Mobile rules:

- no secrets embedded in the application;
- secure storage for tokens;
- resilient behavior on unstable networks;
- explicit offline states;
- local data scoped by account and profile;
- cached data invalidated on logout or account switch;
- accessibility considered from the start;
- analytics routed through a controlled abstraction;
- business-critical entitlement decisions verified by the server when online.

## 34. Offline-First Boundaries

Offline support is a premium capability and must be designed intentionally.

Offline availability requires:

- a download manifest;
- asset integrity checks;
- local encryption or platform-protected storage where justified;
- expiry or revocation rules;
- account and device association;
- synchronization of playback progress;
- conflict resolution;
- storage quota handling;
- clear user-visible states.

Offline mode must never imply permanent ownership of media assets.

## 35. Administrative Architecture

Administrative capabilities are privileged and high impact.

The admin dashboard must use dedicated APIs or dedicated authorization policies.

Administrative actions must support:

- role enforcement;
- server-side validation;
- audit logging;
- safe preview before publication;
- controlled state transitions;
- protection from accidental destructive changes;
- pagination and filtering;
- bulk-operation limits;
- clear failure reporting.

High-risk actions such as user suspension, subscription overrides, content publication, and permanent deletion require stronger controls and complete audit records.

## 36. Subscription and Billing Principles

The platform must treat payment providers as external systems, not as the sole source of internal business state.

Billing architecture must:

- verify provider callbacks;
- persist raw provider references safely;
- process callbacks idempotently;
- maintain an internal subscription state machine;
- reconcile periodically with providers;
- distinguish billing state from effective entitlement;
- support grace periods and recovery;
- record all state transitions;
- never trust client-reported purchase success without server verification.

Entitlement decisions must remain understandable and testable.

## 37. Advertisement Principles

Advertisements are allowed only for eligible free users and only under the approved product policy.

Architecture must enforce:

- no mid-story interruption;
- no ad shown merely because a client requests one;
- server-supported session counting or tamper-resistant eligibility;
- age-appropriate provider configuration;
- no behavioral child profiling;
- premium users never receive ads;
- failures in ad delivery do not block core listening;
- ad events are auditable at an aggregate level without excessive child data.

The current policy target is a subtle advertisement after every two eligible listening sessions, followed by a premium upsell. Exact rules remain configurable.

## 38. Notifications

Notifications must be modeled as persistent user-facing records where product requirements call for inbox history.

Push notification delivery is an external delivery channel, not the authoritative notification record.

The notification domain must distinguish:

- notification creation;
- user targeting;
- persistence;
- push request;
- provider delivery result;
- read state;
- dismissal;
- expiration.

Users must be able to control optional notification categories. Mandatory security notifications may override marketing preferences where legally and product-appropriately required.

## 39. Logging

Logs must be structured, searchable, and safe.

Every request should support:

- correlation ID;
- service name;
- environment;
- log level;
- timestamp;
- route or operation;
- duration;
- outcome;
- safe actor or account reference where needed.

Never log:

- passwords;
- access or refresh tokens;
- parental PINs;
- full payment credentials;
- secret keys;
- unrestricted request bodies containing personal data;
- raw audio or binary content.

Business events worth auditing must not rely only on ordinary application logs.

## 40. Auditing

Audit records are immutable security and accountability records.

Audit candidates include:

- administrative login and role changes;
- story publication and unpublication;
- subscription override;
- account suspension;
- child profile deletion;
- privacy export and deletion requests;
- security-setting changes;
- high-risk configuration changes.

An audit record should include actor, action, target, timestamp, result, correlation ID, and safe before/after details where appropriate.

Audit retention differs from ordinary log retention and must be explicitly defined.

## 41. Metrics and Tracing

Every deployable backend component must expose health and operational metrics.

Minimum metrics include:

- request rate;
- error rate;
- latency percentiles;
- database pool usage;
- cache hit/miss ratio where applicable;
- queue depth and consumer lag;
- retry and dead-letter counts;
- external provider latency and failures;
- JVM health;
- business-critical workflow counters.

Distributed tracing should propagate correlation and trace context across HTTP and messaging boundaries.

Observability must support answering:

- What failed?
- For whom did it fail?
- Where did it fail?
- When did it begin?
- Is it still happening?
- What changed recently?

## 42. Health Checks

Health checks must distinguish:

- liveness — process can continue running;
- readiness — process can safely receive traffic;
- dependency status — diagnostic information for operators.

A transient optional dependency failure must not always make the entire service unavailable.

Health endpoints must not expose secrets or excessive infrastructure detail publicly.

## 43. Resilience

External and cross-service calls must use explicit resilience policies.

These may include:

- connection and request timeouts;
- bounded retries with backoff and jitter;
- circuit breakers;
- bulkheads;
- fallback behavior;
- dead-letter queues;
- replay tooling;
- reconciliation jobs.

Retries are allowed only for failures likely to be transient and only where the operation is safe to repeat.

Unlimited retries are prohibited.

## 44. Performance Budgets

Performance must be measured against user journeys, not isolated method execution.

Initial targets will be defined in the performance document, but each feature must consider:

- API latency;
- startup impact;
- media start time;
- memory usage;
- database query count;
- network payload size;
- battery and mobile data usage;
- cache behavior;
- concurrency expectations.

Performance regressions in core catalog and playback flows should block release when they exceed agreed budgets.

## 45. Scalability

The platform should scale stateless application nodes horizontally.

User session state must not depend on one application instance.

Scalability strategies include:

- CDN delivery for media;
- distributed cache;
- asynchronous processing;
- database indexing;
- read models;
- queue-based load leveling;
- horizontal application scaling;
- partitioning only when justified by measured need.

Premature sharding is discouraged. Clear data ownership and query discipline come first.

## 46. Deployment

Services and applications must be containerizable.

Docker is the standard packaging approach for backend components and supporting local infrastructure.

Deployment principles:

- immutable artifacts;
- environment-specific configuration externalized;
- automated migrations with controlled rollout;
- reproducible builds;
- health-based rollout;
- rollback capability;
- no manual code changes on servers;
- no environment-specific branches.

Production deployment architecture will be documented separately and may evolve through ADRs.

## 47. Configuration

Configuration must be:

- external to application binaries;
- validated at startup;
- typed where possible;
- documented;
- environment-specific without code forks;
- safe for logs;
- reloadable only when there is a controlled need.

Feature flags may be used for controlled rollout but must not become permanent hidden architecture.

Every flag requires an owner and removal condition.

## 48. CI/CD Quality Gates

The delivery pipeline should progressively enforce:

- compilation;
- formatting and static analysis;
- unit tests;
- integration tests;
- architecture tests;
- API compatibility checks;
- dependency vulnerability scanning;
- secret scanning;
- container scanning;
- migration validation;
- documentation checks;
- build reproducibility.

A failed quality gate must not be bypassed silently.

## 49. Testing Strategy

Testing follows a risk-based pyramid.

Required categories include:

- unit tests for domain rules;
- application-service tests for use cases;
- repository integration tests;
- API integration tests;
- messaging contract tests;
- security tests;
- migration tests;
- mobile widget and integration tests;
- end-to-end tests for critical journeys;
- load tests for important flows.

Critical journeys include:

- account login;
- profile selection;
- story discovery;
- playback start and resume;
- subscription purchase verification;
- entitlement change;
- offline download;
- admin publication workflow.

## 50. Architecture Testing

Architecture boundaries must be testable.

For Java modules, ArchUnit or equivalent checks should enforce rules such as:

- controllers do not access repositories directly;
- domain packages do not depend on delivery or persistence packages;
- one bounded context does not import another context's persistence implementation;
- administrative APIs remain isolated;
- forbidden dependency cycles fail the build.

Architectural rules that exist only in prose are likely to decay.

## 51. Documentation

Documentation is part of the product, not an optional afterthought.

Required documentation includes:

- architecture principles;
- software and backend architecture;
- mobile architecture;
- database design;
- API specification;
- security architecture;
- performance guidance;
- logging and monitoring;
- notification architecture;
- ADRs;
- operational runbooks;
- changelog.

Public classes, controllers, public methods, DTOs, and non-obvious rules should include useful JavaDoc or equivalent documentation. Comments must explain why, not repeat obvious code.

## 52. Dependency Management

Dependencies must be intentional.

Before adding a library, evaluate:

- necessity;
- maintenance activity;
- license;
- security history;
- transitive dependencies;
- runtime cost;
- replacement difficulty;
- compatibility with Java 21 and the selected Spring Boot version.

Do not add a library for functionality that is trivial and safer to implement directly.

Dependency versions must be centrally manageable where practical.

## 53. Third-Party Integrations

Every third-party integration must be isolated behind an internal interface.

The domain must not depend directly on provider-specific payloads.

An integration adapter must handle:

- authentication;
- request mapping;
- response mapping;
- timeouts;
- retries;
- provider error translation;
- observability;
- idempotency;
- webhook verification;
- testing through stubs or sandboxes.

Provider replacement should not require rewriting core business rules.

## 54. Backward Compatibility

Database, API, event, and mobile compatibility must be considered together.

Because mobile users do not upgrade immediately, backend releases must support a defined range of application versions.

Removal of old behavior requires:

- usage measurement;
- migration communication;
- minimum-version policy;
- controlled deprecation;
- fallback or upgrade path.

Event consumers and producers must be deployable independently where practical.

## 55. Data Deletion and Retention

Deletion is a workflow, not a single SQL statement.

The architecture must distinguish:

- soft deletion;
- immediate access revocation;
- delayed physical deletion;
- legal or financial retention;
- anonymization;
- cache invalidation;
- object-storage cleanup;
- event propagation;
- backup expiration.

User-facing deletion promises must match actual system behavior.

## 56. Accessibility

Accessibility is an architectural requirement for both child and parent experiences.

The system should support:

- scalable text;
- screen readers;
- meaningful semantics;
- sufficient contrast;
- reduced-motion preferences;
- audio-independent understanding where possible;
- clear focus order;
- large touch targets;
- captions or synchronized text where available.

Backend content models must provide the metadata needed to render accessible experiences.

## 57. Localization

Text presented to users must be localizable.

Do not hard-code user-facing language in backend business logic.

Content metadata should support multiple locales without duplicating the entire story identity unnecessarily.

APIs should carry stable codes; clients or localization services render language-specific text where appropriate.

The initial product may launch with a limited language set, but architecture must not block expansion.

## 58. Analytics

Analytics must be privacy-safe and purpose-driven.

Every tracked event must answer a product or operational question.

Avoid collecting raw data merely because it may be useful later.

Analytics event schemas must be versioned and documented.

Child-related analytics should prefer pseudonymous profile identifiers and aggregated insights.

Security audit events and product analytics are separate systems with different purposes and retention.

## 59. Feature Flags and Experiments

Experiments involving children require heightened review.

Feature flags must support:

- clear targeting rules;
- safe defaults;
- rollback;
- metrics;
- expiration;
- ownership.

Experiments must not weaken safety, parental control, privacy, or subscription correctness.

## 60. Change Management

Significant architecture changes require an ADR.

An ADR is required when changing:

- service boundaries;
- primary database technology;
- messaging technology;
- authentication model;
- API versioning strategy;
- payment provider architecture;
- media-storage approach;
- deployment platform;
- major cross-cutting framework;
- consistency model for a critical workflow.

ADRs must include context, decision, alternatives, consequences, and status.

## 61. Definition of Architecture Done

An architectural capability is not complete until:

- boundaries are documented;
- security is reviewed;
- contracts are specified;
- failure modes are understood;
- data ownership is clear;
- observability exists;
- tests cover critical rules;
- deployment and rollback are understood;
- operational ownership is assigned;
- related documentation is updated.

Working code alone is not sufficient.

## 62. Prohibited Patterns

The following patterns are prohibited unless justified through an ADR:

- shared writable database across independently deployed services;
- direct database access from mobile or admin clients;
- controllers containing business logic;
- JPA entities exposed as API models;
- synchronous chains across many services for one user request;
- unlimited retries;
- silent exception swallowing;
- secrets in source control;
- business-critical behavior controlled only by the client;
- unrestricted administrative endpoints;
- unbounded queries;
- binary media stored in relational tables;
- permanent feature flags without ownership;
- logging personal or secret data by default;
- schema changes without migrations;
- breaking API changes without versioning or migration;
- child-facing external links without review;
- direct provider payloads leaking into the domain.

## 63. Initial Technology Direction

The current preferred technology direction is:

| Area | Preferred technology |
|---|---|
| Backend language | Java 21 |
| Backend framework | Spring Boot |
| Mobile | Flutter |
| Relational database | PostgreSQL |
| Database migrations | Flyway |
| Distributed cache | Redis |
| Messaging | RabbitMQ |
| API contract | OpenAPI 3 |
| Containers | Docker |
| Metrics | Micrometer and Prometheus-compatible export |
| Dashboards | Grafana |
| Logs | Structured JSON with centralized aggregation |
| Tracing | OpenTelemetry-compatible instrumentation |
| Binary media | S3-compatible object storage plus CDN |

These are defaults, not unchangeable laws. Replacements require evidence and an ADR.

## 64. Review Checklist

Every new feature should be reviewed with the following questions:

1. Which bounded context owns it?
2. What data does it create or modify?
3. Does it collect personal or child-related data?
4. What are its authorization rules?
5. What happens when dependencies fail?
6. Is the operation idempotent where necessary?
7. Does it require synchronous communication?
8. Which events does it emit or consume?
9. What is cached, and how is it invalidated?
10. What must be logged, measured, and audited?
11. How does it behave offline?
12. How is it tested?
13. How is it rolled back?
14. Does it preserve Child First and Parent in Control?
15. Which documentation and ADRs must change?

## 65. Governance

This document is maintained by the project architecture owner.

Changes must be reviewed against product goals, security requirements, operational cost, and implementation reality.

The document should evolve when evidence shows a better approach. It must not change simply to legitimize an implementation shortcut after the fact.

Architecture is successful when developers can make consistent decisions without repeatedly asking what the system is supposed to be.
