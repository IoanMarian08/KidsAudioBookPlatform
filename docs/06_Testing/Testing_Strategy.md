# Testing Strategy

Version: 2.0.0  
Status: Required quality strategy  
Owner: QA and Engineering

## 1. Objective

Verify KidsAudioBookPlatform as a safe, reliable child-first experience, not just as compilable code. Tests must prove parent authorization, isolated child profiles, curated catalog, correct entitlements, resilient audio playback, trustworthy progress synchronization and safe editorial workflows.

## 2. Layers and ownership

| Layer | Scope | Owner | Gate |
|---|---|---|---|
| Unit | Domain policies, validators, mappers, component logic | Feature developers | PR |
| Integration | Spring+PostgreSQL/Redis/RabbitMQ, repositories, workers | Backend | PR |
| Contract | REST/OpenAPI and versioned async events | Producer and consumer teams | PR |
| Flutter widget | Navigation, screen states, accessibility semantics | Mobile | PR |
| E2E/acceptance | Critical parent and child journeys | QA + feature team | Staging/release |
| Security | AuthN/AuthZ, child data isolation, misuse cases | Security + QA | PR and release |
| Performance | API latency, media startup, queue lag, capacity | Performance/DevOps | Pre-release |
| Recovery | Backup restore, failover, controlled rollback | DevOps | Production readiness |

No single layer replaces another. Prefer many fast deterministic tests plus targeted realistic integration and E2E tests.

## 3. Release-critical scenarios

**P0 scenarios:** parent registration/verification/recovery; session revocation; Parent Zone elevation; cross-account and cross-profile access denial; published-only catalog; playback authorization; progress sync conflict safety; refund/expiry entitlement correctness; editorial takedown; admin audit; account deletion workflow.

Security/child privacy defects can block release regardless of numeric coverage.

## 4. Traceability model

~~~text
PRD objective -> FR-ID -> user story -> API/event/schema contract
             -> test IDs -> CI evidence -> release approval
~~~

Every P0 user story must have at least one happy path and relevant negative/edge acceptance scenarios. Test plans name owner and test level. Never rely on a screenshot as the only evidence for server-side access rules.

## 5. Test data and isolation

Use synthetic parent/child records and factory builders; avoid real child information. Each test runs with independently created state. Testcontainers owns ephemeral PostgreSQL/broker for integration. Avoid persistent dependencies, shared global mutable fixtures, sleep-based synchronization and reliance on external provider production APIs.

Use provider sandboxes/fakes and signed sample payloads for billing. Keep fixture data age-appropriate and rights-cleared.

## 6. Coverage and quality gates

Coverage is a signal, not a substitute for business correctness. For each bounded context require meaningful unit coverage of critical domain branches, integration evidence for persistence/messaging and an explicit risk-based scenario inventory. Any numeric coverage thresholds must be approved in CI policy rather than guessed from a document.

Fail a release on critical assertion failures, leaked child data, unauthorized premium access, migrations that break compatibility, or unreviewed security severity. Quarantined flaky tests require an owner and expiry.

## 7. CI execution tiers

PR: unit + static/arch tests + selected integration/contract + lint + secrets/SCA.  
Nightly: full integration, widget/golden, end-to-end on emulators, security regression.  
Staging release: P0 acceptance, store sandbox reconciliation, load, resilience and restore smoke.  
Post-release: synthetic core journeys and error-budget dashboard.

## 8. Failure diagnostics

Each failing test reports scenario, expected/actual behavior, owning module, correlation ID and minimal sanitized fixture. CI keeps logs/screenshots/traces with retention and access controls. Do not publish tokens, signed URLs or PII in test artifacts.

## 9. Review checklist

[ ] Business rules and boundary values covered  
[ ] Server-side owner checks tested independently of UI  
[ ] Retry/duplicate/out-of-order messaging tested  
[ ] Expired sessions, revoked entitlements and draft content denied  
[ ] Offline, timeout, re-entry and reconnect scenarios tested  
[ ] User-facing error states and accessibility tested  
[ ] No brittle sleeps or production accounts  
[ ] Test suites runnable locally and in CI

Related: [Functional Requirements](../01_Product/Functional_Requirements.md), [Definition of Done](../04_Engineering/Definition_of_Done.md).
