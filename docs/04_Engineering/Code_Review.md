# Code Review

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owners | Engineering and Architecture |
| Last Updated | 2026-07-15 |
| Scope | Backend, Flutter mobile, admin dashboard, infrastructure and documentation |

---

## 1. Purpose

This document defines how code reviews are prepared, performed, resolved and approved in KidsAudioBookPlatform.

Code review exists to improve correctness, security, maintainability and shared understanding. It is not a substitute for automated testing, static analysis or architecture documentation.

Every production change must be reviewable by another engineer or, when the project is maintained by one engineer, through an explicit self-review process supported by automated checks and a documented checklist.

---

## 2. Review Principles

1. Review the change, not the person.
2. Prioritize correctness, safety and architectural consistency over style preferences.
3. Explain why a change is required.
4. Distinguish blocking issues from suggestions.
5. Keep feedback specific, actionable and respectful.
6. Do not approve code that you do not understand.
7. Do not rely on manual review for checks that can be automated.
8. Small pull requests should be preferred over large, mixed changes.
9. Security-sensitive and child-data-related changes require additional scrutiny.
10. AI-generated code receives the same review standard as human-written code.

---

## 3. Pull Request Author Responsibilities

Before requesting review, the author must:

- confirm the task satisfies the Definition of Ready;
- keep the pull request focused on one coherent objective;
- rebase or update the branch against the target branch;
- run the required local checks;
- remove temporary code, debug logging and commented-out code;
- review the complete diff personally;
- document behavior changes and migration impact;
- link the relevant task, issue, ADR or requirement;
- include testing evidence;
- identify known limitations or follow-up work;
- update documentation when behavior or contracts change.

A reviewer should not be expected to discover the purpose of the pull request by reverse-engineering the diff.

---

## 4. Required Pull Request Description

Every pull request must state:

- what problem is solved;
- why the change is needed;
- the implementation approach;
- affected modules and contracts;
- database, API, event or configuration changes;
- security and privacy impact;
- tests executed;
- rollout and rollback considerations;
- screenshots or recordings for relevant UI changes;
- follow-up tasks, if any.

For changes with no user-visible behavior, explicitly state that there is no visible change.

---

## 5. Review Priority Order

Reviewers should evaluate changes in this order:

1. child safety and privacy;
2. authorization and security boundaries;
3. business correctness and data integrity;
4. architecture and module ownership;
5. API, event and database compatibility;
6. failure handling and resilience;
7. observability and auditability;
8. test quality;
9. maintainability and readability;
10. performance and resource use;
11. style and formatting.

Cosmetic feedback must not distract from correctness or safety issues.

---

## 6. Review Comment Severity

Use clear severity labels:

| Label | Meaning | Merge impact |
|---|---|---|
| `BLOCKER` | Security, data loss, broken requirement, unsafe behavior or unrecoverable operational risk | Must be resolved before merge |
| `MAJOR` | Incorrect behavior, architecture violation, missing critical test or significant maintainability issue | Must normally be resolved before merge |
| `MINOR` | Local improvement that does not affect core correctness | Should be resolved or explicitly acknowledged |
| `SUGGESTION` | Optional alternative or readability improvement | Does not block merge |
| `QUESTION` | Reviewer needs clarification | Must be answered before approval when material |
| `PRAISE` | Good design or implementation worth reinforcing | No action required |

Example:

```text
MAJOR: This repository call crosses the Catalog module boundary. Please use the public application port so that the module can remain independently extractable.
```

---

## 7. Backend Review Checklist

Reviewers must verify, where applicable:

- domain rules are enforced server-side;
- module boundaries are respected;
- domain code does not depend on framework or infrastructure types;
- transactions have clear boundaries;
- database writes preserve invariants;
- optimistic locking or idempotency is used where concurrent updates are possible;
- API validation is explicit;
- authorization checks use authenticated ownership, not client-provided trust;
- errors use the standard error catalog;
- logs do not expose secrets or child-sensitive data;
- events are published reliably through the approved pattern;
- consumers are idempotent;
- retries are bounded;
- database migrations are backward compatible;
- tests cover success, failure and boundary cases.

---

## 8. Flutter Review Checklist

Reviewers must verify, where applicable:

- feature boundaries and dependency direction are respected;
- state is not duplicated unnecessarily;
- asynchronous states include loading, success, empty and failure behavior;
- secure data uses platform-secure storage;
- entitlement and authorization decisions are not made authoritatively on the client;
- offline operations are durable and idempotent;
- navigation guards protect Parent Zone routes;
- child-facing flows do not expose destructive or adult actions;
- accessibility labels, text scaling and touch targets are supported;
- animations remain calm and interruptible;
- resources and subscriptions are disposed correctly;
- widget and integration tests cover critical behavior.

---

## 9. Admin Dashboard Review Checklist

Reviewers must verify:

- administrative permissions are checked by the backend;
- destructive actions require confirmation and reason capture where required;
- forms display validation errors clearly;
- tables support pagination and safe filtering;
- sensitive values are masked;
- HTML content is sanitized;
- high-risk actions create audit records;
- bulk operations support partial failure reporting;
- UI changes include relevant tests and screenshots.

---

## 10. Database and Migration Review

Every migration review must consider:

- compatibility with the currently deployed application;
- lock duration and table size;
- indexes required by new queries;
- default values and nullability;
- backfill strategy;
- rollback or forward-fix strategy;
- data retention and privacy requirements;
- validation in a clean database and supported upgrade path.

Applied migration files must never be edited.

---

## 11. Security Review Triggers

Additional security review is required for changes involving:

- authentication or session handling;
- Parent Zone access;
- child profile data;
- subscriptions or payment verification;
- signed media URLs;
- file uploads;
- authorization rules;
- data export or deletion;
- cryptography or secrets;
- external provider callbacks;
- admin roles and permissions.

The reviewer must verify abuse cases, not only the expected user flow.

---

## 12. Test Review

Reviewers evaluate test quality, not only test quantity.

Tests should:

- express observable behavior;
- cover relevant failure modes;
- be deterministic;
- avoid unnecessary implementation coupling;
- use realistic boundaries for integration tests;
- validate authorization and ownership;
- include regression coverage for fixed defects;
- avoid real personal or production data.

A high coverage percentage does not compensate for missing critical scenarios.

---

## 13. Performance Review

Performance concerns should be evidence-driven.

Review for:

- unbounded queries or collections;
- N+1 database access;
- synchronous external calls on critical paths;
- large payloads;
- repeated expensive serialization;
- uncontrolled cache cardinality;
- memory-heavy mobile state;
- blocking work on the Flutter UI thread;
- missing pagination or streaming;
- excessive telemetry labels.

Material performance claims should include measurement or a reproducible test.

---

## 14. Review Size and Scope

Preferred pull requests are small enough to review in one focused session.

A pull request should be split when it mixes:

- refactoring and new behavior without necessity;
- unrelated modules;
- formatting changes with functional changes;
- architecture migration with product functionality;
- generated code with manually written logic.

Large changes require a review guide that identifies the recommended reading order.

---

## 15. Review Resolution

The author must respond to every material comment by:

- applying the requested change;
- explaining why another solution was chosen;
- creating a follow-up task when deferral is acceptable;
- asking for clarification.

Comments must not be silently resolved when the concern remains.

The reviewer who raised a blocking concern should confirm its resolution when practical.

---

## 16. Approval Rules

A pull request may be approved only when:

- the purpose and implementation are understood;
- blocking and major comments are resolved;
- required checks pass;
- tests are adequate;
- documentation and contracts are updated;
- rollout and migration risks are acceptable;
- no known security or data-integrity issue remains.

Approval means the reviewer accepts shared responsibility for the merged change.

---

## 17. Self-Review for Solo Development

When no second reviewer is available, the author must:

1. finish the implementation;
2. pause before the final review when practical;
3. read the full diff from the perspective of a reviewer;
4. execute the checklist in this document;
5. run all required automated checks;
6. document risks and test evidence in the pull request;
7. use AI review only as supplementary input, never as the sole quality gate;
8. avoid merging security-sensitive changes without additional independent validation where feasible.

---

## 18. AI-Assisted Review

AI tools may assist with:

- summarizing a diff;
- identifying missing tests;
- checking common security mistakes;
- detecting inconsistent naming or duplicated logic;
- comparing implementation with documented requirements.

AI review output must be verified by a human. The tool must not receive secrets, production data, private keys or unnecessary child-related information.

---

## 19. Prohibited Review Behavior

The following are not acceptable:

- approving without reading the change;
- using vague comments such as "bad code";
- blocking based only on personal preference;
- requesting unrelated refactoring;
- moving requirements during review without documenting the scope change;
- using review comments to assign blame;
- ignoring failing checks;
- merging with unresolved security concerns.

---

## 20. Review Completion Checklist

Before approval, confirm:

- [ ] Scope is coherent and documented.
- [ ] Requirements are satisfied.
- [ ] Architecture boundaries are respected.
- [ ] Security and privacy were evaluated.
- [ ] API, event and database compatibility were evaluated.
- [ ] Failure behavior is safe.
- [ ] Tests are meaningful and passing.
- [ ] Logs and metrics are appropriate.
- [ ] Documentation is updated.
- [ ] Rollout and rollback are understood.
- [ ] All blocking comments are resolved.

---

## 21. Related Documents

- `Coding_Standards.md`
- `Git_Workflow.md`
- `Branching_Strategy.md`
- `Definition_of_Ready.md`
- `Definition_of_Done.md`
- `Documentation_Standards.md`
- `AI_Development_Guide.md`
- `../00_Project/Definition_of_Done.md`
- `../03_Architecture/Architecture_Principles.md`
