# Technology Stack

Version: 1.1.0  
Status: Active Draft  
Owner: Project Architecture  
Last updated: 2026-07-15

## 1. Purpose

This document defines the approved technology stack for KidsAudioBookPlatform and the rules that govern its use. It is the default implementation decision source for backend, mobile, administration, persistence, messaging, media delivery, observability, testing, infrastructure, security tooling, and developer experience.

A technology not listed here is not automatically forbidden, but introducing an alternative or overlapping tool requires a documented need, an impact assessment, and an Architecture Decision Record when the change affects architecture, operations, security, data ownership, or long-term maintenance.

## 2. Decision Principles

Technology choices must follow these principles:

1. **Prefer mature and supported technologies.** Long-term support, ecosystem health, documentation, and operational knowledge matter more than novelty.
2. **Optimize for maintainability before theoretical scale.** The initial team must be able to understand, test, deploy, and operate the platform safely.
3. **Use the simplest tool that satisfies a verified requirement.** Complexity is introduced only when evidence justifies it.
4. **Keep local development reproducible.** A developer must be able to run the platform without depending on manually configured shared infrastructure.
5. **Avoid overlapping tools.** The platform should not adopt multiple libraries for the same responsibility without a strong reason.
6. **Treat security and observability as selection criteria.** Libraries must support secure configuration, structured telemetry, and automated validation.
7. **Prefer open standards and portable interfaces.** OpenAPI, OAuth-compatible patterns, SQL, S3-compatible storage, OpenTelemetry, and OCI containers reduce vendor lock-in.
8. **Pin versions and upgrade deliberately.** Production dependencies are not allowed to float unpredictably.
9. **Separate product code from provider SDKs.** External providers are accessed through adapters so they can be replaced or tested independently.
10. **Document operational ownership.** Every major technology must have backup, recovery, monitoring, patching, and incident expectations.

## 3. Runtime Baseline

| Area | Approved baseline |
|---|---|
| Backend runtime | Java 21 LTS |
| Backend framework | Spring Boot 3.x |
| Mobile | Flutter and Dart |
| Administrative web | React and TypeScript |
| Primary database | PostgreSQL |
| Cache and ephemeral coordination | Redis |
| Message broker | RabbitMQ |
| Media storage | S3-compatible object storage |
| Media delivery | CDN |
| Packaging | OCI-compatible Docker images |
| CI/CD | GitHub Actions |
| API contract | OpenAPI 3.1 |
| Architecture documentation | Markdown, Mermaid, C4 model, ADRs |

Exact versions are pinned in build files and dependency-management configuration. This document defines product-level choices, not a substitute for lock files or build descriptors.

## 4. Backend Platform

### 4.1 Core technologies

| Technology | Role | Decision rationale |
|---|---|---|
| Java 21 | Backend language | LTS lifecycle, strong performance, records, sealed types, improved concurrency primitives, and a mature tooling ecosystem |
| Spring Boot 3.x | Application framework | Production-ready configuration, REST, validation, persistence, messaging, security, metrics, and testing support |
| Spring Framework | Dependency injection and application infrastructure | Mature programming model and clear integration with the selected stack |
| Spring Security | Authentication and authorization | Standard security layer for consumer APIs, Parent Zone, and administrative access |
| Spring Data JPA | Relational persistence abstraction | Reduces repository boilerplate while preserving explicit transaction and query control |
| Hibernate | JPA implementation | Mature ORM, batching, locking, and PostgreSQL integration |
| Bean Validation | Request and command validation | Standard declarative validation with custom domain validators where required |
| Flyway | Database schema migration | Versioned, ordered, reviewable, and auditable database evolution |
| Maven | Build and dependency management | Stable Java ecosystem support and predictable CI usage |
| Jackson | JSON serialization | Spring-compatible serialization with centrally controlled configuration |
| MapStruct | Explicit DTO mapping where beneficial | Compile-time mapping without reflection-heavy runtime behavior |

### 4.2 Backend architecture rules

- Controllers translate transport input and call application use cases; they do not contain business workflows.
- Domain and application packages do not depend directly on controllers, JPA entities, RabbitMQ clients, or provider SDKs.
- Public APIs use dedicated request and response DTOs.
- Persistence entities never become API contracts.
- Transactions are short, explicit, and centered on one business use case.
- External network calls are not performed while holding database locks unless the flow explicitly requires it and has been reviewed.
- Background consumers are idempotent and safe under redelivery.
- Cross-module access uses application interfaces or events, not another module's repository.
- Reflection-based convenience libraries are evaluated carefully because they can hide behavior and complicate debugging.
- New dependencies require a clear owner, purpose, license review, and vulnerability review.

### 4.3 Java coding baseline

The backend uses:

- records for immutable transport and value-oriented data where appropriate;
- sealed types when they make closed result models clearer;
- `java.time` for all temporal values;
- UTC for persisted timestamps;
- explicit locale and time-zone handling at product boundaries;
- `BigDecimal` for money and provider financial values;
- stable identifiers such as UUID or ULID according to database design decisions;
- structured concurrency or virtual threads only after workload-specific validation and an ADR if they change the runtime model materially.

Lombok is not a default dependency. It may be introduced only if the reduction in boilerplate outweighs IDE, build, debugging, and implicit-code costs.

## 5. API and Contract Technologies

| Technology | Role |
|---|---|
| OpenAPI 3.1 | Machine-readable REST API contract |
| Swagger UI | Development and internal contract exploration |
| JSON | Default synchronous API representation |
| RFC 7807-style problem details | Standard error response structure |
| JSON Schema | Event payload and configuration schema support where applicable |
| Idempotency keys | Safe retry behavior for selected write operations |

API rules:

- Contracts are versioned and validated in CI.
- Generated documentation must match implemented request and response models.
- Backward-compatible additive change is preferred.
- Breaking changes require a versioning and migration plan.
- Pagination, filtering, sorting, localization, and error semantics are consistent across modules.
- Internal database identifiers or provider-specific representations are not exposed without a deliberate contract decision.
- Consumer and administrative APIs use separate route namespaces and authorization policies.

## 6. Data and Storage

### 6.1 PostgreSQL

PostgreSQL is the authoritative transactional system of record.

Approved usage includes:

- account and session metadata;
- child profiles and preferences;
- catalog metadata and publication workflow;
- subscriptions, provider transaction history, and entitlements;
- playback progress and listening sessions;
- notification records and delivery attempts;
- administrative audit records;
- download manifests and reconciliation state;
- transactional outbox records.

Rules:

- each bounded context owns its write model and migrations;
- schemas may be used to reinforce module ownership;
- database constraints protect critical invariants;
- indexes are justified by query patterns and reviewed for write cost;
- unbounded queries are forbidden in user-facing endpoints;
- optimistic locking is preferred for normal concurrent updates;
- pessimistic locking is reserved for narrowly defined conflicts;
- JSONB is used for flexible provider metadata or append-only payloads, not as a replacement for relational modeling;
- production migrations are backward-compatible with rolling deployment whenever possible;
- destructive migrations require backup, verification, and rollback planning.

### 6.2 Redis

Redis is approved for:

- short-lived catalog and home-screen projections;
- entitlement snapshots;
- rate-limiting counters;
- idempotency response storage;
- revocation and short-lived session metadata;
- narrowly scoped distributed locks;
- transient coordination and deduplication.

Redis is never the authoritative source for business state. Every cached value must have an expiry or an explicit invalidation strategy, and the platform must define safe behavior when Redis is unavailable.

### 6.3 Object storage

| Environment | Technology |
|---|---|
| Local development | MinIO or compatible local S3 implementation |
| Shared and production environments | Managed S3-compatible object storage |

Object storage holds:

- source audio;
- normalized and encoded audio variants;
- illustrations and thumbnails;
- synchronized text artifacts;
- temporary upload objects;
- derived media metadata files where justified.

Rules:

- object keys are opaque and generated by the platform;
- buckets and prefixes follow data classification and lifecycle rules;
- direct public access is disabled unless a specific public-content decision exists;
- uploads use narrowly scoped pre-signed URLs;
- delivery uses CDN URLs, signed URLs, or signed cookies;
- checksums and technical metadata are stored in PostgreSQL;
- lifecycle policies remove abandoned uploads and expired derived assets;
- malware and file-signature validation occur before an asset becomes usable.

### 6.4 CDN

A CDN is mandatory for production media delivery. It reduces origin load, improves playback start time, and isolates application servers from large binary transfer.

Cache-control policies distinguish:

- immutable versioned public assets;
- protected premium assets;
- short-lived signed delivery;
- invalidated or suspended content.

## 7. Messaging and Background Processing

| Technology or pattern | Role |
|---|---|
| RabbitMQ | Durable domain and integration event delivery |
| Transactional outbox | Atomic persistence of state changes and events |
| Dead-letter queues | Isolation and investigation of repeatedly failing messages |
| Scheduled workers | Reconciliation, cleanup, publication, retention, and campaign jobs |
| Retry with backoff | Recovery from transient dependencies |

RabbitMQ is selected because the initial platform requires durable queues, routing, retries, work distribution, and moderate event volume without Kafka's operational overhead.

Kafka is not selected for the initial product. It may be reconsidered when long-term replay, very high event throughput, stream processing, or extended event retention becomes a measured requirement.

Messaging rules:

- event envelopes contain event ID, type, version, occurrence time, producer, correlation ID, and payload;
- consumers deduplicate by event ID or business operation ID;
- retries are bounded and classified by error type;
- poison messages move to a dead-letter queue with diagnostic metadata;
- sensitive values are not copied unnecessarily into event payloads;
- schema compatibility is reviewed before deployment;
- broker availability must not cause committed business data to disappear.

## 8. Mobile Platform

| Technology | Role | Decision rationale |
|---|---|---|
| Flutter | Android and iOS application | One codebase, precise UI control, strong rendering, and mature cross-platform tooling |
| Dart | Mobile language | Native language and tooling for Flutter |
| Riverpod | State and dependency management | Explicit dependencies, testability, and feature-oriented composition |
| GoRouter | Navigation | Declarative routing and guarded Child Experience / Parent Zone transitions |
| Dio | HTTP client | Interceptors, cancellation, timeout control, upload progress, and structured failures |
| Drift | Structured offline persistence | Typed SQLite access, migrations, and testability |
| flutter_secure_storage | Sensitive local storage | Platform-backed keychain and keystore integration |
| just_audio | Audio playback engine | Flexible audio playback primitives |
| audio_service | Background playback integration | Lock-screen controls, background execution, and media notifications |
| Firebase Cloud Messaging | Push delivery | Cross-platform push notification support |
| Freezed or equivalent generated immutable models | Optional model generation | Allowed when generation remains deterministic and maintainable |

### 8.1 Mobile rules

- Features are organized by product capability, not by technical file type alone.
- Child Experience and Parent Zone have separate navigation guards and presentation policies.
- Access and refresh tokens are stored only through secure platform storage.
- Offline media is stored in application-private storage.
- Local databases contain only the minimum data needed for offline behavior.
- The server remains authoritative for ownership, subscription, entitlement, publication, and revocation.
- Network requests use bounded timeouts and explicit retry policies.
- Background synchronization is idempotent and battery-aware.
- Crash reports, analytics, and logs must not include raw child data, tokens, PINs, receipts, or private media URLs.
- Accessibility, text scaling, localization, and reduced-motion behavior are considered from the first implementation.

## 9. Administrative Dashboard

| Technology | Role |
|---|---|
| React | Administrative user interface |
| TypeScript | Type-safe frontend implementation |
| Vite | Development and production build tooling |
| React Router | Dashboard routing |
| TanStack Query | Server-state fetching, caching, and mutation coordination |
| React Hook Form | Form-state management |
| Zod | Client-side schema validation and typed parsing |
| Playwright | End-to-end dashboard testing |

A component system may be selected during implementation, but it must support accessibility, theming, keyboard navigation, and predictable customization. Adoption requires a lightweight UI decision record if it creates a long-term design dependency.

Dashboard rules:

- TypeScript strict mode is mandatory.
- Server state and local UI state remain separate.
- The backend enforces all permissions.
- Privileged and destructive actions require confirmation and audit metadata.
- Long-running operations expose progress or asynchronous status.
- Sensitive values are not persisted in browser storage unless explicitly approved.
- Content preview must represent the child-facing result accurately.
- Tables use server-side pagination for large datasets.

## 10. Identity and Security Technologies

| Capability | Approved approach |
|---|---|
| Password hashing | Argon2id preferred, or a reviewed adaptive alternative |
| Access tokens | Short-lived signed JWTs |
| Refresh sessions | Rotating opaque or securely managed refresh tokens with server-side state |
| Mobile secret storage | Platform keychain / keystore through secure storage |
| Transport security | TLS at ingress and provider boundaries |
| Secret storage | Managed secret manager in production |
| Dependency scanning | Automated CI vulnerability scanning |
| Container scanning | CI and registry image scanning |
| Static analysis | Java, Dart, TypeScript, and infrastructure linters |

Security libraries and algorithms are configured centrally. Product code must not invent custom cryptographic schemes.

Sensitive configuration is supplied through environment-specific secret injection. Secrets, signing keys, provider credentials, private certificates, and production connection strings are never committed to Git.

## 11. Observability

| Technology | Role |
|---|---|
| Micrometer | Application and JVM metrics |
| Prometheus | Metrics collection and query |
| Grafana | Dashboards and alert visualization |
| Loki | Centralized structured logs |
| OpenTelemetry | Trace and correlation context |
| Spring Boot Actuator | Health, readiness, liveness, and operational endpoints |

Every API request, event, scheduled job, and provider callback carries correlation information.

Minimum telemetry includes:

- latency, throughput, and error rate;
- JVM, thread, memory, and connection-pool metrics;
- PostgreSQL saturation and slow-query indicators;
- Redis latency and hit ratio;
- RabbitMQ queue depth, event age, retries, and dead-letter count;
- playback authorization and playback-start success;
- media-processing duration and failures;
- subscription verification and reconciliation outcomes;
- notification delivery status;
- offline synchronization failures;
- administrative privileged actions.

Logs are structured JSON in shared environments. Local development may use a human-readable encoder while preserving the same fields.

## 12. Testing Stack

### 12.1 Backend

| Technology | Role |
|---|---|
| JUnit 5 | Unit, integration, and application tests |
| AssertJ | Readable assertions |
| Mockito | Isolated collaborator tests where a fake is not more appropriate |
| Testcontainers | PostgreSQL, Redis, RabbitMQ, and compatible integration environments |
| WireMock | External HTTP provider simulation |
| REST Assured or MockMvc | API testing |
| ArchUnit | Module and dependency-rule enforcement |
| PIT or equivalent | Optional mutation testing for critical domain rules |

### 12.2 Mobile

| Technology | Role |
|---|---|
| flutter_test | Unit and widget testing |
| integration_test or Patrol | Critical device-level flows |
| Mocktail or equivalent | Test doubles where required |
| Golden tests | Selected stable child-facing visual components |

### 12.3 Administrative web

| Technology | Role |
|---|---|
| Vitest | Unit and component logic tests |
| Testing Library | User-oriented component tests |
| Playwright | Browser-level critical workflows |

### 12.4 Performance and security

| Technology | Role |
|---|---|
| k6 or Gatling | Load and performance testing |
| OWASP ZAP | Automated dynamic security checks in suitable environments |
| Dependency and container scanners | Known-vulnerability detection |

Test technology is selected to validate architecture boundaries and real integration behavior, not only isolated line coverage.

## 13. Delivery and Infrastructure

| Technology | Role |
|---|---|
| Docker | Reproducible application packaging |
| Docker Compose | Local platform orchestration |
| GitHub Actions | Continuous integration and delivery automation |
| OCI-compatible registry | Versioned image storage |
| Reverse proxy or ingress | TLS termination, routing, request limits, and security headers |
| Managed secret manager | Production secret storage and rotation |
| Infrastructure as Code | Repeatable shared and production environment provisioning |

The exact production hosting platform remains replaceable behind container, database, object-storage, and observability abstractions.

Infrastructure rules:

- production artifacts are immutable;
- the same image is promoted between environments;
- configuration is externalized;
- readiness and liveness probes are distinct;
- migrations run as a controlled deployment step;
- rollback procedures are documented and tested;
- backups are encrypted and restore tests are scheduled;
- infrastructure changes require review and an auditable plan;
- direct manual production changes are exceptional and recorded.

## 14. Local Development Tooling

The supported local environment includes:

- Java 21 JDK;
- Maven Wrapper;
- Flutter SDK pinned by project guidance;
- Node.js LTS for the administrative dashboard;
- Docker Desktop or compatible Docker engine;
- Docker Compose;
- PostgreSQL, Redis, RabbitMQ, and MinIO through containers;
- an IDE with Java, Dart, TypeScript, Docker, and Mermaid support;
- DBeaver or another SQL client;
- Postman, Bruno, or generated OpenAPI clients for API exploration.

Repository scripts should minimize platform-specific manual setup. Required environment variables are documented through safe example files without real credentials.

## 15. Code Quality and Static Analysis

Approved categories include:

- Java compiler warnings and Maven quality gates;
- Checkstyle, SpotBugs, Error Prone, or equivalent after a documented selection;
- Dart analyzer and Flutter lint rules;
- ESLint and TypeScript strict checks;
- Prettier or another single formatting standard for web code;
- Markdown linting and Mermaid rendering checks;
- OpenAPI validation;
- Flyway migration validation;
- architecture tests;
- secret scanning.

The project should choose one primary formatter and one primary linting approach per language to avoid conflicting automation.

## 16. Dependency Governance

Dependencies are governed by the following rules:

- versions are pinned or controlled through dependency management;
- automated update proposals are reviewed rather than merged blindly;
- unsupported libraries are replaced before they become operational risks;
- transitive dependencies are inspected for security and license impact;
- licenses must be compatible with commercial mobile and backend distribution;
- dependencies that execute code generation are reproducible in CI;
- provider SDKs are isolated behind adapters;
- unnecessary dependencies are removed;
- major framework upgrades include migration notes and rollback considerations;
- a software bill of materials should be generated for release artifacts.

## 17. Technology Lifecycle

Each major technology is classified as:

- **Approved** — standard choice for new implementation;
- **Trial** — limited evaluation with owner and exit criteria;
- **Deprecated** — retained temporarily but forbidden for new usage;
- **Retired** — removed from supported architecture.

A lifecycle review occurs before major releases and whenever a critical vulnerability, end-of-support announcement, licensing change, or provider deprecation occurs.

## 18. Explicit Non-Selections

The following are not selected for the initial platform:

- microservice framework diversity;
- Kafka without a measured streaming requirement;
- MongoDB as a parallel primary datastore;
- GraphQL without demonstrated client-contract benefit;
- Kubernetes for local development;
- multiple state-management libraries in Flutter;
- multiple ORMs or database migration tools;
- custom authentication or cryptography;
- application-server proxying of large media files;
- provider-specific business logic embedded directly in domain code.

These are not permanent prohibitions. They are safeguards against premature complexity and require evidence plus an ADR before adoption.

## 19. Environment Matrix

| Capability | Local | Development / Staging | Production |
|---|---|---|---|
| PostgreSQL | Docker container | Managed or shared instance | Managed HA instance |
| Redis | Docker container | Shared managed instance | Managed resilient instance |
| RabbitMQ | Docker container | Shared broker | Managed or resilient broker cluster |
| Object storage | MinIO | S3-compatible bucket | Managed S3-compatible storage |
| CDN | Optional local bypass | Staging distribution | Production distribution |
| Secrets | Local uncommitted environment | Environment secret store | Managed secret manager |
| Logs | Console | Centralized | Centralized with retention controls |
| Metrics | Optional local stack | Prometheus-compatible | Monitored with alerts |
| Push | Provider sandbox | Test project | Production project |
| Store purchases | Sandbox | Sandbox / test tracks | Production stores |

## 20. Change Process

A proposed technology change must document:

1. the problem being solved;
2. why the existing stack is insufficient;
3. alternatives considered;
4. security and privacy impact;
5. operational and cost impact;
6. migration and rollback strategy;
7. testing approach;
8. ownership and support plan;
9. compatibility with mobile-store and commercial licensing requirements.

An ADR is mandatory when the proposal changes a datastore, framework, messaging platform, deployment model, authentication strategy, public contract style, or major observability component.

## 21. Related Documents

- `Software_Architecture.md`
- `Backend_Architecture.md`
- `Mobile_Architecture.md`
- `Admin_Dashboard.md`
- `Database_Design.md`
- `API_Specification.md`
- `Security_Architecture.md`
- `Performance_Guidelines.md`
- `Logging_Monitoring.md`
- `System_Flows.md`
- `Event_Catalog.md`
- `Implementation_Roadmap.md`
- `../00_Project/ADR/README.md`

## 22. Definition of Technology Readiness

A selected technology is ready for implementation when:

- its purpose and owner are documented;
- the approved version range is known;
- secure configuration is defined;
- local development is reproducible;
- CI validation exists;
- production observability is planned;
- backup and recovery responsibilities are known where applicable;
- license and vulnerability checks pass;
- failure and degradation behavior are understood;
- its use does not contradict an existing ADR or architecture document.
