# ADR-0010: Testing Strategy

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision Owners:** Architecture and Engineering
- **Last reviewed:** 2026-07-15

## Context

KidsAudioBookPlatform contains backend services, a Flutter mobile application, an admin dashboard, asynchronous messaging, media workflows, subscriptions, offline synchronization, and security-sensitive parent controls. A single testing style is insufficient because defects can originate in domain logic, persistence, API contracts, event processing, mobile state, infrastructure integration, or provider behavior.

The product handles children, premium entitlements, parental controls, downloads, purchases, and content publication. These areas require stronger assurance than ordinary presentation logic. The testing strategy must support fast developer feedback while still validating real infrastructure, contracts, and end-to-end journeys.

## Decision

Adopt a layered testing strategy based on the testing pyramid, with contract, integration, security, and critical-journey testing treated as first-class requirements.

Testing is part of feature implementation, not a separate phase after development.

## Testing Principles

1. Test behavior and contracts, not implementation details.
2. Keep most tests fast, deterministic, and isolated.
3. Use real infrastructure where integration risk matters.
4. Validate critical business journeys end to end.
5. Treat flaky tests as defects.
6. Keep test data privacy-safe and reproducible.
7. Match test depth to business, security, and data-integrity risk.
8. Require tests for every bug fix where practical.
9. Prefer explicit fixtures and builders over hidden shared state.
10. Keep contract definitions synchronized with tests.

## Test Portfolio

The platform uses:

- unit tests;
- component and slice tests;
- repository and infrastructure integration tests;
- API contract tests;
- event contract tests;
- consumer and provider contract tests;
- security tests;
- end-to-end tests;
- performance and load tests;
- resilience and failure-injection tests;
- migration tests;
- mobile and browser tests;
- smoke and synthetic checks.

## Backend Testing

### Unit tests

Unit tests cover:

- domain rules;
- value objects;
- application use cases;
- entitlement calculations;
- profile limits;
- publication state transitions;
- playback progress merge rules;
- ad eligibility;
- retry classification;
- notification preference logic.

Unit tests must not require Spring or external infrastructure unless framework behavior is the subject under test.

### Slice tests

Use focused framework tests for:

- controllers and serialization;
- security configuration;
- validation;
- repository mappings;
- message serialization;
- configuration binding.

Slice tests should load only the necessary application context.

### Integration tests

Use Testcontainers or equivalent for:

- PostgreSQL;
- Redis;
- RabbitMQ;
- MinIO or S3-compatible storage;
- external HTTP adapters through WireMock or provider sandboxes.

Integration tests validate:

- transactions;
- migrations;
- repository queries;
- outbox publication;
- idempotent consumers;
- retry and dead-letter behavior;
- cache invalidation;
- signed URL generation;
- provider response mapping.

### Architecture tests

Architecture tests enforce:

- module boundaries;
- forbidden package dependencies;
- no direct cross-module repository access;
- domain independence from Spring, JPA, and provider SDKs;
- naming and package conventions;
- separation of API, application, domain, and infrastructure layers.

## API Contract Testing

The OpenAPI contract is validated in CI.

Tests verify:

- request and response schemas;
- required fields;
- error contracts;
- status codes;
- pagination;
- version compatibility;
- examples;
- authentication and authorization requirements.

Breaking changes must fail contract validation unless accompanied by an approved major-version migration.

## Event Contract Testing

Every asynchronous event has schema tests covering:

- envelope fields;
- event type and version;
- required payload fields;
- backward-compatible additions;
- consumer tolerance for unknown optional fields;
- serialization and deserialization;
- idempotency behavior;
- retry classification.

Important producer-consumer relationships require consumer contract tests before deployment.

## Mobile Testing

### Unit tests

Cover:

- repositories;
- use cases;
- state controllers;
- local persistence rules;
- progress merge logic;
- offline queue behavior;
- entitlement presentation;
- formatters and validators.

### Widget tests

Cover:

- reusable components;
- profile selection;
- story cards;
- player controls;
- Parent Zone entry;
- error and empty states;
- premium-lock presentation;
- accessibility behavior.

### Integration tests

Critical mobile scenarios include:

- registration and login;
- profile creation and selection;
- story discovery;
- playback start and resume;
- background playback;
- offline download and playback;
- offline progress synchronization;
- subscription activation;
- Parent Zone protection;
- notification deep links;
- local database migration.

### Golden tests

Golden tests are used only for stable, high-value screens where visual regression detection provides clear value. They must not become the primary UI testing method.

### Device matrix

Release candidates are tested against a documented minimum matrix of:

- supported Android versions;
- supported iOS versions;
- small and large screens;
- low-memory or representative constrained devices;
- interrupted connectivity;
- background and foreground transitions.

## Admin Dashboard Testing

### Unit and component tests

Cover:

- permissions;
- forms and validation;
- tables and filters;
- content state rendering;
- destructive-action confirmations;
- bulk operation behavior;
- error mapping.

### Browser-level tests

Use Playwright for:

- authentication;
- role-based access;
- story creation and editing;
- media upload;
- review and publication;
- rollback;
- subscription support workflows;
- notification campaigns;
- audit exploration.

Backend authorization must still be tested independently; browser tests do not replace server-side security tests.

## Security Testing

Security-sensitive flows require explicit tests for:

- authentication failures and lockout;
- refresh-token rotation and reuse detection;
- authorization matrices;
- Parent Zone access;
- profile ownership enforcement;
- admin role boundaries;
- rate limiting;
- input validation;
- SQL injection resistance;
- file upload validation;
- signed URL scope and expiry;
- secret and token redaction;
- webhook signature and replay protection;
- account deletion authorization.

Automated dependency, container, and secret scanning runs in CI.

## Subscription and Entitlement Testing

Required scenarios include:

- valid purchase verification;
- duplicate purchase events;
- renewal;
- grace period;
- expiration;
- refund and revocation;
- provider outage;
- reconciliation;
- delayed webhook delivery;
- entitlement cache invalidation;
- premium-to-free transitions;
- offline entitlement expiry.

Provider simulators or sandboxes must be used where available.

## Offline and Synchronization Testing

Test:

- queued operation persistence;
- app restart with pending operations;
- duplicate operation delivery;
- stale progress updates;
- explicit restart behavior;
- cursor advancement;
- rejected and retryable operations;
- entitlement revocation;
- corrupted download recovery;
- local database migration;
- storage quota exhaustion;
- long periods without connectivity.

## Media Testing

Test:

- upload intent creation;
- file signature validation;
- size and codec limits;
- malware rejection;
- checksum mismatch;
- derivative generation;
- processing idempotency;
- missing object recovery;
- publication blocking when assets are not ready;
- CDN or signed URL authorization;
- lifecycle cleanup.

## End-to-End Testing

End-to-end tests are reserved for critical journeys and must remain limited enough to be reliable and maintainable.

Critical journeys:

1. Parent registration and verification.
2. Login and child profile creation.
3. Story discovery and playback.
4. Progress resume on another session.
5. Premium purchase and entitlement activation.
6. Offline download and playback.
7. Content creation, approval, and publication.
8. Subscription expiration and access downgrade.
9. Parent Zone protection.
10. Account deletion request.

## Performance and Load Testing

Performance tests cover:

- catalog home;
- story details;
- playback authorization;
- progress updates;
- login and refresh;
- purchase verification;
- notification creation;
- event consumer throughput;
- media manifest generation.

Tests measure:

- throughput;
- p50, p95, and p99 latency;
- error rate;
- database and connection-pool saturation;
- queue growth;
- cache behavior;
- resource utilization.

Load tests must use realistic traffic shapes and privacy-safe synthetic data.

## Resilience Testing

Test expected behavior when:

- Redis is unavailable;
- RabbitMQ is unavailable;
- PostgreSQL connections are saturated;
- object storage is unavailable;
- CDN requests fail;
- purchase providers time out;
- notification providers reject requests;
- messages are redelivered;
- workers restart mid-operation.

Retries, timeouts, circuit breakers, fallback behavior, and dead-letter handling must be verifiable.

## Database Migration Testing

CI must validate:

- migration from an empty database;
- migration from supported previous versions;
- checksum consistency;
- application compatibility with expanded schemas;
- rollback-safe deployment sequencing;
- repeatable migrations where used;
- local test database parity with production PostgreSQL behavior.

## Test Data Strategy

- Use deterministic factories and builders.
- Use synthetic identifiers and content.
- Never copy production personal data into non-production environments.
- Keep fixtures minimal and explicit.
- Reset or isolate state between tests.
- Version large fixtures intentionally.
- Avoid shared mutable global fixtures.
- Use representative multilingual and accessibility examples.

## Mocking Policy

Mocks are appropriate for narrow collaborator behavior in unit tests.

Do not mock:

- domain objects unnecessarily;
- JPA behavior when repository integration matters;
- RabbitMQ delivery semantics when consumer reliability is under test;
- provider contracts where a simulator, sandbox, or WireMock integration test is more appropriate.

Over-mocking that allows tests to pass while real integration is broken is prohibited.

## Coverage Policy

Coverage is a diagnostic, not a target in isolation.

Requirements:

- new domain logic must be tested;
- bug fixes should include regression tests;
- authentication, entitlements, profile rules, offline synchronization, content publishing, and deletion workflows require high branch and scenario coverage;
- generated code and trivial accessors may be excluded;
- coverage drops in critical modules require review.

Coverage percentage alone cannot approve a change with missing important scenarios.

## Flaky Test Policy

A flaky test is a defect.

When detected:

1. identify an owner;
2. capture evidence and frequency;
3. fix immediately where practical;
4. quarantine only when necessary;
5. add an expiry date and tracking issue;
6. never silently ignore the test permanently.

Quarantined critical-path tests block release unless risk is explicitly accepted.

## Quality Gates

### Pull requests

Must pass:

- compilation;
- formatting and linting;
- unit tests;
- architecture tests;
- relevant slice tests;
- selected integration tests;
- OpenAPI and event contract validation;
- dependency and secret scanning.

### Main branch

Additionally runs:

- full integration suite;
- migration tests;
- broader contract tests;
- mobile and admin build validation.

### Release candidates

Must pass:

- smoke tests;
- critical end-to-end journeys;
- security suite;
- performance checks against approved thresholds;
- mobile device matrix;
- deployment and rollback validation;
- production-readiness checklist.

## Test Environments

- Local development uses Docker Compose and targeted tests.
- CI uses ephemeral infrastructure where practical.
- Shared development supports exploratory integration testing.
- Staging mirrors production contracts and infrastructure behavior.
- Production uses smoke and synthetic checks only; destructive test data is prohibited.

## Ownership

Feature owners maintain tests for their capability.

Platform or DevOps owners maintain shared CI infrastructure, not feature correctness.

Architecture owns boundary and contract-test standards.

Security owns security-test requirements and reviews.

## Tooling

Approved tools include:

- JUnit 5;
- AssertJ;
- Mockito where isolation is appropriate;
- Spring Boot Test;
- Testcontainers;
- WireMock;
- ArchUnit or equivalent architecture testing;
- Flutter test tooling;
- Patrol or `integration_test` for mobile journeys;
- Playwright for the admin dashboard;
- k6 or Gatling for performance testing;
- OWASP-compatible dependency and security scanning tools.

Tool replacements require equivalent capability and documented justification.

## Consequences

### Positive

- Earlier defect detection.
- Safer refactoring.
- Verifiable API and event contracts.
- Repeatable infrastructure testing.
- Better protection for child safety, purchases, and parental controls.
- Clear release quality gates.

### Negative

- Higher CI execution time.
- Additional maintenance for fixtures, containers, and end-to-end environments.
- More discipline required when changing contracts.
- Device and provider testing can increase operational cost.

## Rejected Alternatives

- **Unit tests only:** insufficient for persistence and integration risk.
- **End-to-end tests only:** too slow and difficult to diagnose.
- **Manual testing as primary validation:** not repeatable and not scalable.
- **Coverage percentage as the only quality gate:** easy to game and does not prove scenario coverage.
- **Mock every external boundary:** hides real serialization, protocol, and infrastructure defects.

## Follow-up Actions

- Add shared test factories and builders.
- Configure Testcontainers for PostgreSQL, Redis, RabbitMQ, and MinIO.
- Add OpenAPI and event schema validation to CI.
- Define the initial end-to-end suite.
- Define the supported mobile device matrix.
- Add flaky-test reporting and quarantine expiry checks.
- Add performance baselines for critical endpoints.
- Add architecture tests for module boundaries.
