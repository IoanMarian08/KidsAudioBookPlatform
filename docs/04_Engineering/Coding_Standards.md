# Coding Standards

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owner | Engineering |
| Last Updated | 2026-07-15 |
| Scope | Backend, Mobile, Admin Dashboard, Shared Tooling |

---

## 1. Purpose

This document defines the mandatory coding standards for KidsAudioBookPlatform. It applies to human-written code, AI-assisted code, generated code that is committed to the repository, tests, migration scripts, build configuration, and automation.

The goals are to keep the codebase:

- understandable;
- maintainable;
- secure;
- testable;
- consistent;
- easy to review;
- safe to evolve.

A rule may be overridden only by an accepted Architecture Decision Record or a documented module-specific standard.

---

## 2. General Engineering Principles

All code must follow these principles:

1. Prefer clarity over cleverness.
2. Keep business rules explicit.
3. Keep methods and classes focused on one responsibility.
4. Avoid hidden side effects.
5. Reject invalid state early.
6. Make failure behavior explicit.
7. Do not duplicate authoritative business rules across clients and backend.
8. Do not introduce infrastructure without a demonstrated need.
9. Do not bypass module boundaries for convenience.
10. Code must be reviewable without relying on undocumented context.

---

## 3. Repository-Wide Rules

### 3.1 Language

- Source code, identifiers, comments, documentation, commit messages, and log messages use English.
- User-facing content may be localized.
- Avoid abbreviations unless they are widely understood in the domain.

### 3.2 Formatting

- Use the repository formatter and linter configuration.
- Do not mix formatting-only changes with unrelated functional changes.
- Files must use UTF-8 and LF line endings.
- Remove trailing whitespace.
- End text files with a newline.

### 3.3 Naming

Names must communicate intent.

Prefer:

```text
calculateEffectiveEntitlement
subscriptionRenewalDate
PlaybackProgressRepository
```

Avoid:

```text
doStuff
processData
obj
mgr
helper2
```

Boolean names should read naturally:

```text
isPremium
hasActiveSubscription
canDownloadOffline
```

### 3.4 Comments

Comments explain why, constraints, trade-offs, or non-obvious behavior. They must not repeat what the code already says.

Temporary comments must include an issue reference or removal condition.

Avoid commented-out code. Git already preserves history.

---

## 4. Backend Standards — Java 21 and Spring Boot

### 4.1 Package Organization

Use package-by-feature and preserve module boundaries.

Recommended module structure:

```text
<module>/
  api/
  application/
  domain/
  infrastructure/
```

The domain layer must not depend on Spring MVC, JPA, RabbitMQ, Redis, HTTP SDKs, or provider-specific classes.

### 4.2 Classes and Methods

- Classes must have a clear responsibility.
- Prefer composition over inheritance.
- Avoid static mutable state.
- Avoid utility classes that collect unrelated behavior.
- Public APIs must be intentionally small.
- Methods should operate at one level of abstraction.
- Long methods must be decomposed when this improves understanding.
- Parameter lists should remain small; use value objects or request types when multiple parameters form one concept.

### 4.3 Immutability

Prefer immutable domain objects and records where appropriate.

- Use final fields by default.
- Do not expose mutable internal collections.
- Return immutable views or copies.
- Mutation must occur through behavior that protects invariants.

### 4.4 Null Handling

- Do not return `null` collections.
- Use empty collections when absence is valid.
- Use `Optional` for return values where absence is meaningful.
- Do not use `Optional` as an entity field, DTO field, or method parameter without a documented reason.
- Validate required values at boundaries.

### 4.5 Exceptions

- Use domain-specific exceptions for business failures.
- Do not expose stack traces or infrastructure messages to clients.
- Do not catch `Exception` unless translating at an application boundary or performing guaranteed cleanup.
- Never silently swallow exceptions.
- Retry only failures classified as transient.
- Preserve the original cause when translating exceptions.

### 4.6 Transactions

- Define transactions at the application-service boundary.
- Keep transactions short.
- Do not perform slow network calls inside database transactions.
- Do not publish events directly before a transaction is committed.
- Use the transactional outbox where reliable event publication is required.

### 4.7 Persistence

- JPA entities remain inside infrastructure or persistence boundaries.
- Do not expose entities directly through APIs.
- Repository methods must represent real query needs.
- Avoid uncontrolled N+1 queries.
- Every production query must be bounded or paginated unless a strict maximum is guaranteed.
- Database constraints must protect critical invariants.
- Schema changes use Flyway migrations.

### 4.8 REST APIs

- OpenAPI is the canonical public contract.
- Controllers validate transport concerns and delegate business work.
- Controllers must not contain domain logic.
- Use standard error envelopes and correlation IDs.
- Support idempotency for retry-prone commands.
- Never trust profile IDs, roles, entitlements, or prices supplied by a client.

### 4.9 Messaging

- Events describe facts in past tense.
- Consumers must be idempotent.
- Event payloads must be versioned.
- Personally identifiable data must be minimized.
- Retries must be bounded and use dead-letter routing.
- Handlers must distinguish retryable and permanent failures.

### 4.10 Logging

- Use structured logs.
- Never log passwords, PINs, access tokens, refresh tokens, secrets, raw payment data, or child names.
- Include correlation and trace context where available.
- Log meaningful lifecycle and failure events, not every method call.

---

## 5. Flutter and Dart Standards

### 5.1 Structure

Use feature-first organization with explicit layers:

```text
feature/
  presentation/
  application/
  domain/
  data/
```

Platform-specific functionality must be isolated behind adapters.

### 5.2 State Management

- Riverpod is the default dependency-injection and state-management approach.
- State must be explicit and testable.
- Avoid global mutable singletons.
- UI widgets must not make authoritative entitlement or security decisions.
- Async state must represent loading, success, empty, and failure states clearly.

### 5.3 Widgets

- Prefer small reusable widgets.
- Keep business logic out of widgets.
- Use const constructors where possible.
- Avoid deeply nested build methods; extract meaningful components.
- Provide semantic labels and accessibility support.
- Child-facing controls must remain large, simple, and safe.

### 5.4 Navigation

- GoRouter is the default router.
- Protected routes must use explicit guards.
- Deep links must never bypass Parent Zone controls.
- Navigation state must remain predictable after authentication or profile changes.

### 5.5 Local Persistence

- Sensitive credentials use platform secure storage.
- Offline operations use a durable queue.
- Local schemas require versioned migrations.
- Cached data must have an owner, invalidation rule, and expiry behavior.

---

## 6. Admin Dashboard Standards

- Use typed API clients.
- Escape and sanitize untrusted content.
- Enforce permissions on the backend; frontend checks are only usability controls.
- Forms must provide client-side feedback but rely on server validation.
- Destructive actions require confirmation and clear consequences.
- High-risk actions must capture an audit reason where required.
- Tables must be paginated and support predictable loading, empty, and error states.

---

## 7. Security Standards

Every change must consider:

- authentication;
- authorization;
- input validation;
- output encoding;
- sensitive-data exposure;
- injection risks;
- abuse and rate limiting;
- auditability;
- dependency risk;
- child privacy.

Mandatory rules:

- Secrets never enter source control.
- Passwords and PINs are never stored or logged in plaintext.
- File uploads are treated as hostile until validated and scanned.
- Authorization is enforced server-side on every protected operation.
- Dependencies must come from approved repositories.
- Known critical vulnerabilities block release unless a documented exception is approved.

---

## 8. Testing Standards

- New business logic requires tests.
- Bug fixes require a regression test where practical.
- Tests must be deterministic and independent.
- Do not use production personal data in tests.
- Avoid excessive mocking of internal implementation details.
- Prefer behavior-focused assertions.
- Integration tests use realistic infrastructure through Testcontainers where appropriate.
- Contract changes require contract-test updates.
- Flaky tests must be fixed or quarantined with an owner and expiry date.

Test names should describe behavior:

```text
shouldRejectDownloadWhenSubscriptionIsExpired
shouldKeepFurthestPlaybackProgressDuringSync
```

---

## 9. Database Migration Standards

- Applied migrations are immutable.
- Migrations must be deterministic.
- Destructive changes use expand-and-contract.
- Large backfills must not block normal deployments.
- Every migration must be tested on a clean database.
- Production rollback relies on compatible application rollback, forward correction, or restoration procedures—not arbitrary automatic reverse SQL.

---

## 10. Dependency Standards

- Add a dependency only when its value exceeds its maintenance and security cost.
- Prefer actively maintained libraries with clear licensing.
- Avoid multiple libraries solving the same problem.
- Pin or centrally manage dependency versions.
- Remove unused dependencies.
- Review transitive dependencies and vulnerability reports.
- Major upgrades require compatibility testing and release notes.

---

## 11. Generated and AI-Assisted Code

Generated or AI-assisted code is held to the same standard as human-written code.

It must be:

- reviewed;
- tested;
- secure;
- consistent with architecture boundaries;
- free of invented APIs or dependencies;
- traceable to the requested task.

AI-generated code must not be accepted solely because it compiles.

Reviewers must verify:

- business correctness;
- failure behavior;
- security;
- data ownership;
- test quality;
- unnecessary complexity;
- license or provenance concerns.

---

## 12. Prohibited Patterns

The following are prohibited unless explicitly justified:

- direct cross-module repository access;
- shared mutable global state;
- business logic in controllers or UI widgets;
- secrets in code or configuration committed to Git;
- unbounded database queries;
- arbitrary request/response body logging;
- catching and ignoring exceptions;
- disabling tests to make CI pass;
- manual production schema changes;
- feature behavior controlled by undocumented magic values;
- copying generated code without review;
- bypassing security controls in non-local environments.

---

## 13. Review Checklist

Before approving code, confirm:

- the change is understandable;
- naming is clear;
- module boundaries are respected;
- business rules are in the correct layer;
- validation and authorization are present;
- errors are classified correctly;
- logs do not expose sensitive data;
- queries are bounded;
- concurrency and idempotency are considered;
- tests cover important paths;
- documentation and contracts are updated;
- no unnecessary dependency or abstraction was introduced.

---

## 14. Enforcement

These standards are enforced through:

- automated formatting and linting;
- static analysis;
- architecture tests;
- compiler warnings;
- dependency and vulnerability scanning;
- unit, integration, and contract tests;
- pull-request templates;
- code review;
- Definition of Done checks.

A deliberate exception must be documented in the pull request and linked to an ADR or follow-up issue.