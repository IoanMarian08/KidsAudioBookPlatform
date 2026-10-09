# Definition of Done

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owners | Engineering and Quality |
| Last Updated | 2026-07-15 |
| Scope | Engineering completion criteria for code, configuration, migrations and documentation |

---

## 1. Purpose

This document defines when an engineering work item is complete and safe to merge or release.

It operationalizes the project-level Definition of Done from `docs/00_Project/Definition_of_Done.md`. The project-level document defines the product-wide quality bar; this document defines the concrete engineering checks required to meet it.

A task is not done because code compiles or because the happy path works locally.

---

## 2. Core Done Criteria

Every completed engineering item must be:

- functionally correct;
- secure and privacy-aware;
- architecturally consistent;
- tested at the appropriate levels;
- observable and supportable;
- documented where behavior or contracts changed;
- reviewed;
- compatible with supported clients and environments;
- deployable and reversible or recoverable;
- free of unresolved critical defects.

---

## 3. Requirement Completion

Before marking an item done:

- all acceptance criteria are satisfied;
- implemented behavior matches the approved scope;
- non-scope remains excluded;
- deviations are documented and approved;
- edge cases and failure states are handled;
- no hidden follow-up work is required for the feature to operate safely;
- deferred work is captured as explicit tasks with owners.

---

## 4. Code Completion

Code must:

- follow `Coding_Standards.md`;
- use clear names and cohesive responsibilities;
- avoid dead, commented-out or temporary debug code;
- avoid unresolved TODOs without linked work items;
- respect module and dependency boundaries;
- avoid duplication where a stable abstraction is justified;
- handle expected failures explicitly;
- avoid leaking framework concerns into the domain layer;
- contain no hard-coded secrets or environment-specific credentials;
- pass formatting, linting and static analysis.

Generated code must be reproducible and clearly separated from manually maintained code.

---

## 5. Backend Done Criteria

Backend work is done when applicable criteria are met:

- domain invariants are enforced;
- authorization and ownership are validated server-side;
- transaction boundaries are explicit;
- database access is bounded and indexed appropriately;
- API contracts use the standard error model;
- idempotency is implemented for retry-prone operations;
- asynchronous consumers are idempotent;
- retries are bounded and dead-letter behavior is defined;
- outbox or equivalent reliable publication is used where required;
- logs, metrics and traces are added for material behavior;
- sensitive data is not logged;
- audit records exist for high-risk operations;
- integration and contract tests pass.

---

## 6. Flutter Done Criteria

Mobile work is done when:

- loading, success, empty, offline and failure states are implemented;
- navigation and Parent Zone guards are correct;
- sensitive values use secure storage;
- local persistence migrations are handled;
- offline operations survive process restart where required;
- server authority is preserved for entitlement and security decisions;
- resources, listeners and streams are disposed correctly;
- accessibility labels, text scaling and touch targets are verified;
- supported iOS and Android behavior is validated;
- widget and integration tests cover critical paths;
- visible changes include screenshots or recordings in the pull request.

---

## 7. Admin Dashboard Done Criteria

Admin work is done when:

- backend authorization protects every operation;
- forms validate input and display useful errors;
- destructive actions require appropriate confirmation;
- high-risk actions capture reasons and create audit records;
- tables use pagination for potentially large data sets;
- filters and sorting behave predictably;
- sensitive values are masked;
- bulk actions report partial failures;
- HTML and external content are sanitized;
- relevant component and browser tests pass.

---

## 8. API Done Criteria

An API change is done when:

- OpenAPI is updated;
- authentication and authorization are documented;
- validation rules are implemented;
- success and error responses are defined;
- versioning and compatibility were evaluated;
- pagination, sorting and filtering behavior is documented where relevant;
- idempotency behavior is defined;
- examples are accurate;
- contract tests pass;
- affected clients are updated or remain compatible.

Breaking changes require an approved migration and deprecation plan.

---

## 9. Event Done Criteria

An event change is done when:

- the event represents a fact that occurred;
- ownership and producer are clear;
- schema and version are documented in the Event Catalog;
- payload contains only necessary data;
- sensitive information is excluded;
- consumers tolerate compatible additions;
- publication reliability is addressed;
- consumer idempotency is tested;
- retry and dead-letter behavior is defined;
- contract tests pass;
- observability includes event ID and correlation context.

---

## 10. Database Done Criteria

Database work is done when:

- a Flyway migration exists;
- the migration is deterministic and immutable after application;
- clean database creation succeeds;
- supported upgrade paths succeed;
- schema changes are backward compatible for rolling deployment where required;
- constraints protect important invariants;
- indexes support actual query patterns;
- lock and performance impact were evaluated;
- backfill execution and monitoring are defined;
- restore or forward-fix behavior is understood;
- data retention and privacy implications are addressed.

---

## 11. Security Done Criteria

Security-sensitive work is done only when:

- trust boundaries are understood;
- abuse and misuse cases were considered;
- authentication and authorization checks are tested;
- least privilege is preserved;
- secrets remain outside source control and telemetry;
- rate limiting or brute-force protection is applied where required;
- uploads and external payloads are validated;
- child and parent data exposure is minimized;
- dependencies have no accepted critical vulnerability without a documented exception;
- security logging and audit requirements are met;
- security tests pass.

---

## 12. Privacy Done Criteria

Work involving personal data is done when:

- data purpose is documented;
- only necessary fields are collected or propagated;
- child-related data is minimized;
- retention and deletion behavior is defined;
- exports and deletion workflows remain correct;
- logs and analytics do not expose unnecessary personal information;
- test data is synthetic;
- access is limited to authorized roles and services.

---

## 13. Testing Done Criteria

The required test suite must pass.

Depending on the change, this includes:

- unit tests;
- slice, component or widget tests;
- integration tests;
- API and event contract tests;
- migration tests;
- end-to-end tests;
- security tests;
- performance tests;
- manual exploratory validation.

Tests must be deterministic and cover relevant failure behavior. A fixed defect requires a regression test unless technically impossible and documented.

Flaky tests cannot be ignored. They must be fixed or quarantined with an owner and expiry date.

---

## 14. Observability Done Criteria

Material behavior must be supportable after release.

Confirm:

- important operations have structured logs;
- correlation and trace context propagate correctly;
- new failure modes are visible;
- metrics exist for critical rates, errors, duration and saturation;
- alerts are added only when actionable;
- dashboards are updated when operational understanding changes;
- no secret, raw token or unnecessary child data is emitted;
- support can identify the affected flow from a correlation ID.

---

## 15. Documentation Done Criteria

Documentation must be updated in the same change when applicable:

- API Specification;
- Event Catalog;
- Error Catalog;
- database design;
- architecture documents;
- ADRs;
- setup and operational guides;
- changelog or release notes;
- user-facing or admin behavior documentation;
- code comments or JavaDoc for non-obvious public contracts.

The pull request must not leave documentation knowingly inconsistent with implementation.

---

## 16. Pull Request and Review Done Criteria

Before merge:

- the pull request description is complete;
- the diff has been self-reviewed;
- the branch contains only intended changes;
- automated checks pass;
- required reviewers approved;
- blocking and major comments are resolved;
- screenshots or evidence are attached where relevant;
- migrations, configuration and rollout notes are explicit;
- follow-up tasks are linked;
- merge strategy follows `Git_Workflow.md`.

---

## 17. Deployment Done Criteria

A deployable change must include:

- environment configuration requirements;
- secret and permission requirements;
- migration order;
- feature-flag or rollout behavior where applicable;
- health and smoke checks;
- rollback or forward-recovery procedure;
- compatibility with currently supported clients;
- operational ownership;
- release-note impact.

A change that cannot be safely deployed is not done.

---

## 18. Defect Done Criteria

A defect is done when:

- root cause is understood or the containment decision is documented;
- expected behavior is restored;
- a regression test exists where feasible;
- related failure paths were evaluated;
- logs and telemetry support future diagnosis;
- temporary mitigation is removed or tracked;
- affected documentation is updated;
- user or data impact is recorded when relevant.

---

## 19. Documentation-Only Done Criteria

Documentation work is done when:

- the target audience and purpose are clear;
- content is complete and internally consistent;
- links and examples are valid;
- terminology matches the project glossary and current architecture;
- contradictory or obsolete guidance is removed;
- status, version, owner and update date are accurate;
- the document is discoverable from the appropriate index.

---

## 20. AI-Assisted Work Done Criteria

When AI tools contributed to the change:

- generated output was reviewed line by line;
- assumptions were validated against repository contracts;
- no secrets or prohibited data were supplied;
- dependencies and licenses were checked;
- tests were written or updated;
- hallucinated APIs, files or requirements were removed;
- the final author accepts full responsibility for the result.

AI authorship never lowers the engineering quality bar.

---

## 21. Exceptions

A criterion may be deferred only when:

- the reason is documented;
- risk is understood;
- an owner accepts the risk;
- a follow-up item exists;
- the exception does not violate child safety, data integrity, security or legal obligations.

Critical security and privacy requirements cannot be waived for delivery convenience.

---

## 22. Final Engineering Checklist

- [ ] Acceptance criteria are satisfied.
- [ ] Scope is complete and coherent.
- [ ] Code follows engineering standards.
- [ ] Architecture boundaries are respected.
- [ ] Security and privacy were validated.
- [ ] Tests are sufficient and passing.
- [ ] API, event and database contracts are updated.
- [ ] Migrations are safe and validated.
- [ ] Observability is sufficient.
- [ ] Documentation is current.
- [ ] Pull request review is complete.
- [ ] Rollout and recovery are understood.
- [ ] No unresolved blocker or major issue remains.
- [ ] Follow-up work is explicitly tracked.

Only after all applicable criteria are met may the item be considered done.

---

## 23. Related Documents

- `../00_Project/Definition_of_Done.md`
- `Definition_of_Ready.md`
- `Coding_Standards.md`
- `Code_Review.md`
- `Git_Workflow.md`
- `Documentation_Standards.md`
- `AI_Development_Guide.md`
- `../03_Architecture/Architecture_Principles.md`
