# ADR-0010: Testing Strategy

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture and Engineering

## Context

KidsAudioBookPlatform contains backend services, a Flutter mobile application, an admin dashboard, asynchronous messaging, media workflows, subscriptions, offline synchronization, and security-sensitive parent controls. A single testing style is insufficient because defects can originate in domain logic, persistence, API contracts, event processing, mobile state, or infrastructure integration.

## Decision

Adopt a layered testing strategy based on the testing pyramid, with contract and integration testing treated as first-class requirements.

### Backend

1. Unit tests for domain rules and application services.
2. Slice tests for controllers, repositories, serialization, and security configuration.
3. Integration tests using Testcontainers for PostgreSQL, Redis, RabbitMQ, and object storage adapters.
4. API contract tests against the OpenAPI specification.
5. End-to-end tests for critical user journeys.

### Mobile

1. Unit tests for repositories, use cases, formatters, and state controllers.
2. Widget tests for reusable components and important screens.
3. Integration tests for login, profile selection, playback, offline mode, subscription state, and Parent Zone access.
4. Golden tests only for stable, high-value screens.

### Admin Dashboard

1. Unit tests for business utilities and permissions.
2. Component tests for forms, tables, filters, and bulk actions.
3. Browser-level tests for publishing, moderation, and subscription support workflows.

### Quality Gates

Pull requests must pass compilation, linting, unit tests, selected integration tests, and contract validation. The main branch must additionally run the full integration suite. Release candidates must pass smoke, security, and end-to-end suites.

## Coverage Policy

Coverage is a diagnostic, not a target in isolation. New domain logic must be tested. Critical modules such as authentication, subscription entitlements, child profile rules, offline synchronization, and content publishing require high branch coverage and scenario coverage.

## Test Data

Tests must use deterministic factories and builders. Production data must never be copied into non-production environments. Fixtures must avoid real personal data.

## Consequences

### Positive

- Earlier defect detection.
- Safer refactoring.
- Verifiable API and event contracts.
- Repeatable infrastructure testing.

### Negative

- Higher CI execution time.
- Additional maintenance for fixtures and containers.
- More discipline required when changing contracts.

## Rejected Alternatives

- Unit tests only: insufficient for persistence and integration risk.
- End-to-end tests only: too slow and difficult to diagnose.
- Manual testing as primary validation: not repeatable and not scalable.

## Implementation Notes

Use JUnit 5, AssertJ, Mockito where isolation is appropriate, Testcontainers, Spring Boot Test, WireMock for external providers, Flutter test tooling, and Playwright for the admin dashboard. Flaky tests must be fixed or quarantined with an owner and expiry date.