# 12 — End-to-End Acceptance, Requirement Traceability and Release Gates

**Owners:** Product, QA, UX, all owning microservice teams and DevOps.
**Sources:** [PRD](../Product_Requirements_Document.md), [Functional Requirements](../Functional_Requirements.md), [Testing Strategy](../../06_Testing/Testing_Strategy.md), [Definition of Done](../../04_Engineering/Definition_of_Done.md), [Decision Register](../../00_Project/DECISION_REGISTER.md).

## 1. Requirements are verifiable, not just narrative

Every feature has:
1. a stable product need (PRD/FR and this FS rule);
2. an authorized actor and screen/entry point;
3. a positive, negative, empty, offline and interruption outcome where applicable;
4. the owning microservice and existing public API contract or named API change request;
5. data owner, analytics/privacy impact and critical events;
6. automated tests demonstrating behavior and non-bypass of Parent Zone/profile boundaries;
7. rollout/flag policy, logs/metrics and recoverability.

No child-safety or entitlement bypass can be excused because unit test coverage is high. Conversely, a Product Bible capability being P1 does not silently remove it from committed launch scope [DEC-006].

## 2. Module traceability map

| Functional area | Product requirements | Functional IDs | Implementation owner | Acceptance anchor |
|---|---|---|---|---|
| Adult identity/recovery | PRD-01 | FR-ID-001..005 | identity-service | ID-AT |
| Child profiles and switching | PRD-02 | FR-PR-001..003 | profiles-service | PR-AT |
| Parent Zone / parental settings | PRD-06 | FR-PR-004/005 | identity-service + profiles-service | PZ-AT |
| Home/catalog/search | PRD-03 | FR-CA-001..003/006 | catalog-service | CA-AT |
| Editorial/publication/media | PRD-08 | FR-CA-004/005/007, FR-AD-001/002 | catalog-service + media-service + admin-service | AM-AT |
| Streaming/player | PRD-04 | FR-PL-001/002/007 | playback-service + media-service | PL-AT |
| Progress/history/favorites | PRD-05 | FR-PL-003/004 | playback-service | OF-AT |
| Downloads/offline | PRD-09 | FR-PL-005 | playback-service + media-service | OF-AT |
| Ambient/bedtime | PRD-11 | FR-PL-006 | Flutter + catalog/media | PL-AT |
| Premium, trial and billing | PRD-07 | FR-SU-001..006 | billing-service | SU-AT |
| Parent notifications | PRD-12 | FR-NO-001..003 | notifications-service | NO-AT |
| Parent support/privacy | PRD-01/06 | FR-SP-001, FR-ID-004 | identity-service + admin-service | PV-AT/SP-AT |
| Advertising eligibility | PRD-13 | [GATED] | advertising-policy-service | AD-AT |

The PRD/FR documents can expand IDs as feature work is refined; when they do, update this matrix in the same PR. The API Specification is authoritative for exact route shapes and error codes, not this table.

## 3. End-to-end household journeys

### Journey A — First story on a new account

Adult registers and verifies; creates first child profile; selects it; sees safe curated Child Room; opens an eligible free story; playback authorization succeeds; audio begins; progress checkpoint saves; reopening app offers Continue Listening. Acceptance requires adult login, ownership checks, catalog eligibility, signed media access, progress read model and a usable error state for network loss.

### Journey B — Sibling isolation

Adult has profiles A and B. A adds favorite and reaches 70% of a story. Adult changes to B. B sees its own home and no A-specific favorite, playback session, progress or locally cached download labels. B attempts direct A profile API -> server refuses. Changing back to A recovers A-only state.

### Journey C — Premium purchase and safe entitlement

Adult opens Parent Zone, compares approved plans and launches native provider purchase. The client receives a success callback while server verification is still pending: Premium stays ungranted. After verified provider result, account entitlements update, selected authorized story can play/download according to policy, and ad-policy gate remains disabled unless separately approved.

### Journey D — Unavailable story after editorial takedown

Child bookmarks a story then staff suspends it. The cached detail card may briefly exist, but new play authorization is denied. Search and recommendations remove it. Staff audit records the reason; a replay of the publication event cannot accidentally republish the story.

### Journey E — Offline conflict and account safety

Device A downloads an eligible story and listens to 300 seconds offline. Device B completes it online. Device A reconnects; sync deduplicates operation and preserves authoritative Completed. If parent later deletes the account, no offline device can restore it through old tokens or cached grants.

### Journey F — Parent restriction changes

Adult enters Parent Zone, selects profile A and blocks an age/category. Change is saved in profiles-service. Catalog and playback-authority check updated settings; A cannot bypass using a deep link. Sibling B's policy remains unchanged.

### Journey G — Administrative publication

Editor uploads asset to private storage. Worker validates and transcodes. Reviewer approves rights/age/metadata. Catalog schedules/publishes. Search and media eligibility become available only after full readiness. A failed scan blocks publication, and a second processing callback does not duplicate release.

## 4. Cross-cutting release blockers

| Gate | Required evidence |
|---|---|
| Child/parent authorization | IDOR attempts across accounts, profiles and sessions rejected in every owning service |
| Parent Zone security | PIN/biometric proof expiry, brute-force protections and deep-link bypass tests |
| Content safety | Editorial rights, scans, publication gates, age restriction and takedown tests |
| Verified billing | Apple/Google approved sandbox purchase/restore/refund/replay and entitlement reconciliation |
| Offline integrity | Device binding, grant expiry, corrupt/partial download and progress conflict tests |
| Privacy/compliance | Data map, consent notices, retention, deletion saga and market-specific legal sign-off |
| Accessibility | Core child and parent journeys work with screen readers, text scaling and reduced motion |
| Reliability/DevOps | Service-level CI, traceability, DB privilege isolation, backup/restore, canary/rollback |
| Product scope | Owner signs off the MVP functionality/priority decision DEC-006 |
| Optional ads | Explicit DEC-004 legal/security/store approval before ANY activation |

## 5. Test levels and evidence

Unit tests exercise business eligibility, timing/seek, progress merging, restrictions, entitlement transition rules, notification consent and editorial transitions. Service integration tests use isolated logical PostgreSQL databases and test containers. REST/event contract tests prove compatibility of independently deployed microservices. E2E covers iOS/Android Flutter and admin scenarios against a representative staging environment.

Failure injection includes expired token, refused proof, invalid transaction, duplicate/out-of-order webhook, RabbitMQ replay, remote service timeout, PostgreSQL outage of ONE owning service, CDN outage, malformed media, offline reconnection, stalled deletion saga and stale cache after takedown. Every high-risk failure has a safe result and an owner on call.

## 6. UX handoff checklist

Before a screen is coded, record actor, navigation entrance/exit, input fields, interaction order, default values, parent/child permissions, content/empty/loading/offline/error states, text scaling, accessible names, localization keys, analytics events (if approved), privacy review, and mocked API contract. Illustrative copy must be approved before localization and release.

## 7. Decision and scope workflow

An unresolved DEC item is not a developer choice. The owner decides with options/tradeoffs, writes an accepted policy, updates Product Bible if the product promise changes, then synchronizes FR/PRD/FS, API/contracts, QA cases and any mobile/backend feature flags. An unapproved monetization or child data choice remains unshipped.

## 8. Minimum definition of Done

A feature is done only if:
- business outcomes and edge cases are documented and reviewed;
- security tests prove service-side account/profile/parent boundaries;
- API/event contracts are versioned and backward compatible;
- applicable database migrations, outbox/inbox and failure behavior are tested;
- acceptance scenarios pass on device/staging;
- user-visible errors and accessibility work;
- observability/support/runbooks are available;
- rollout and rollback can be executed independently for each service;
- relevant Product/Legal decisions have recorded approval.

## 9. Release modes

The product may be released with feature flags where an optional nonessential capability has a documented gate; this does not authorize incomplete essential identity/child safety/billing verification. A gated ads implementation stays off. A product promise in Product Bible can only be excluded from launch through the explicit DEC-006 product decision, never by a developer silently ignoring P1.

## 10. QA acceptance sign-off template

For every PRD ID: record scenario IDs, platforms, locales/markets, account plan, child age band, accessibility mode, tested provider state, API/service builds, expected/actual outcomes, blocking defect references, responsible approvers and date. Save evidence in the test management system or PR without real child data, receipts or secret credentials.

**Release condition:** Product + QA + Security/Privacy + Engineering/DevOps sign off every applicable gate. The documented handbook is necessary but not itself a production-ready app.
