# Definition of Ready

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owners | Product and Engineering |
| Last Updated | 2026-07-15 |
| Scope | Product work, engineering tasks, defects, spikes and technical changes |

---

## 1. Purpose

This document defines the minimum conditions that a work item must satisfy before implementation begins.

A ready item is sufficiently understood, bounded and testable. It does not need every implementation detail, but the team must understand the expected outcome, constraints, dependencies and acceptance criteria well enough to make a responsible commitment.

The Definition of Ready prevents avoidable rework, hidden dependencies, unsafe assumptions and architecture drift.

---

## 2. Core Principle

Work should not enter active development merely because a title exists.

A work item is ready when:

- the problem is understood;
- the desired outcome is explicit;
- scope and non-scope are known;
- acceptance criteria are testable;
- dependencies and risks are visible;
- security, privacy and architecture implications were considered;
- the item is small enough to implement and review safely.

Urgency does not remove the need for clarity. Emergency work may use an abbreviated readiness check, but missing information must be documented.

---

## 3. Required Work Item Information

Every implementation item must contain:

- clear title;
- problem statement;
- user, business or technical value;
- scope;
- explicit non-scope when ambiguity is likely;
- acceptance criteria;
- affected user type or system component;
- dependencies;
- known risks;
- relevant design, requirement, ADR or architecture references;
- priority and owner;
- expected validation method.

---

## 4. Acceptance Criteria Standard

Acceptance criteria must be:

- observable;
- unambiguous;
- testable;
- focused on behavior rather than implementation;
- complete for relevant success and failure cases.

Preferred form:

```text
Given a Premium account with a valid child profile
When the parent downloads an eligible story
Then the application stores the validated offline package
And the story remains playable without connectivity during the permitted offline window
```

Avoid criteria such as:

```text
The download feature should work correctly.
```

---

## 5. Product Readiness

For product-facing work, confirm:

- the target user is identified;
- the user problem is described;
- the expected experience is consistent with the Product Bible;
- child and parent experiences remain clearly separated;
- copy, state and error behavior are defined;
- empty, loading and failure states are considered;
- Free, Premium and trial behavior is defined where applicable;
- analytics or product metrics are identified when useful;
- accessibility expectations are included;
- content and localization needs are known.

---

## 6. UX and UI Readiness

UI work is ready when applicable designs provide:

- relevant screens or components;
- interaction states;
- responsive behavior;
- navigation behavior;
- loading, empty, disabled and error states;
- accessibility notes;
- child-safe interaction requirements;
- parent confirmation requirements for sensitive actions;
- assets and copy or a clearly assigned source for them.

A polished visual mockup is not required for every engineering task, but behavior must be unambiguous.

---

## 7. Backend Readiness

Backend work must identify, where applicable:

- owning bounded context;
- domain rules and invariants;
- synchronous or asynchronous interaction model;
- transaction boundary;
- authorization and ownership rules;
- API or event contract impact;
- database and migration impact;
- idempotency requirements;
- failure and retry behavior;
- audit and observability requirements;
- compatibility constraints.

A task is not ready if ownership of the business capability is unclear.

---

## 8. Mobile Readiness

Flutter work must identify, where applicable:

- feature ownership;
- online and offline behavior;
- local persistence impact;
- navigation and route guards;
- Parent Zone requirements;
- platform-specific integrations;
- minimum supported operating systems;
- permissions;
- accessibility behavior;
- app-version compatibility;
- expected widget and integration tests.

---

## 9. Admin Dashboard Readiness

Admin work must define:

- required role or permission;
- intended administrative workflow;
- validation and confirmation behavior;
- audit requirements;
- table, filter and pagination behavior;
- bulk-action behavior;
- partial failure handling;
- sensitive data masking;
- support or operational ownership.

---

## 10. API and Event Readiness

Contract-affecting work is ready only when:

- the owning system is identified;
- request and response or event payloads are outlined;
- authentication and authorization are defined;
- versioning impact is understood;
- error behavior is defined;
- idempotency and retry semantics are defined;
- compatibility with existing clients and consumers is evaluated;
- deprecation or migration requirements are identified;
- contract-test expectations are known.

OpenAPI and Event Catalog updates may be part of implementation, but the intended contract must be understood before coding starts.

---

## 11. Database Readiness

Database work must include:

- affected tables or ownership area;
- expected migration type;
- data volume assumptions;
- nullability and default behavior;
- index requirements;
- backfill needs;
- compatibility with running application versions;
- retention and deletion implications;
- rollback or forward-fix approach;
- test-data requirements.

Large backfills or destructive changes require a separate operational plan.

---

## 12. Security and Privacy Readiness

Every item must answer whether it affects:

- authentication;
- authorization;
- child data;
- parent account data;
- subscriptions or payment evidence;
- secrets or credentials;
- uploads or external content;
- data export or deletion;
- admin actions;
- external integrations.

When any answer is yes, the task must include relevant abuse cases and security acceptance criteria.

Security-sensitive work is not ready when the trust boundary or threat is unclear.

---

## 13. Observability Readiness

The work item must define relevant telemetry when the change introduces or alters:

- a critical user journey;
- a background process;
- an external integration;
- an asynchronous consumer;
- a security event;
- a performance-sensitive operation;
- a new failure mode.

Expected logs, metrics, traces, audit records and alerts should be identified before implementation where material.

---

## 14. Testing Readiness

The expected test approach must be clear:

- unit tests;
- component or widget tests;
- integration tests;
- contract tests;
- end-to-end tests;
- security tests;
- migration tests;
- manual exploratory checks.

The task should identify critical scenarios and test data needs.

---

## 15. Dependency Readiness

A task is not ready when a required dependency is unknown or unavailable without a plan.

Dependencies may include:

- another feature or API;
- approved design;
- external credentials or sandbox;
- provider documentation;
- content or media assets;
- database migration;
- infrastructure capability;
- architecture decision;
- legal or privacy decision.

Each dependency must have an owner and status.

---

## 16. Sizing and Decomposition

A ready item must be small enough to:

- understand as one coherent change;
- implement without hiding several unrelated objectives;
- test meaningfully;
- review in a focused pull request;
- roll back or disable safely.

Split an item when it contains multiple independent outcomes, unrelated modules or high-risk migration work mixed with feature delivery.

---

## 17. Defect Readiness

A defect is ready when it contains:

- observed behavior;
- expected behavior;
- reproduction steps or evidence;
- affected environment and version;
- user or business impact;
- logs, screenshots or correlation IDs when available;
- severity;
- suspected area, if known;
- regression-test expectation.

For production incidents, implementation may start before full reproduction when impact is severe, but evidence and assumptions must be recorded.

---

## 18. Technical Spike Readiness

A spike must define:

- question to answer;
- decision it enables;
- time or scope boundary;
- expected output;
- evaluation criteria;
- artifacts to retain;
- whether production code is expected.

A spike is not an unlimited exploration task.

---

## 19. Documentation-Only Work

Documentation work is ready when:

- the target audience is known;
- the document owner is known;
- source material is available;
- expected scope is defined;
- related documents are identified;
- validation method is known;
- the change does not create contradictory guidance.

---

## 20. Emergency Exception

For an urgent incident or security fix, the minimum readiness information is:

- impact;
- affected component;
- immediate containment objective;
- owner;
- validation approach;
- rollback approach;
- known risks.

Missing normal readiness information must be completed after stabilization.

---

## 21. Ready Checklist

Before development starts, confirm:

- [ ] Problem and value are clear.
- [ ] Scope and non-scope are understood.
- [ ] Acceptance criteria are testable.
- [ ] Owning module or component is known.
- [ ] Dependencies have owners and status.
- [ ] UX states are defined where applicable.
- [ ] API, event and database impact is understood.
- [ ] Security and privacy impact was evaluated.
- [ ] Failure behavior is understood.
- [ ] Test strategy is identified.
- [ ] Observability requirements are identified.
- [ ] Relevant documents and decisions are linked.
- [ ] The item is small enough for one coherent implementation and review.

If a material checkbox is not satisfied, the item should remain in refinement rather than active development.

---

## 22. Related Documents

- `../00_Project/Product_Bible.md`
- `../00_Project/Project_Goals.md`
- `../00_Project/Definition_of_Done.md`
- `Coding_Standards.md`
- `Git_Workflow.md`
- `Code_Review.md`
- `Definition_of_Done.md`
- `Documentation_Standards.md`
- `../03_Architecture/Architecture_Principles.md`
