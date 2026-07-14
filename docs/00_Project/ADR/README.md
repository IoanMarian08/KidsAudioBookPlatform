# Architecture Decision Records

Version: 1.1.0  
Status: Active  
Owner: Project Architecture  
Last updated: 2026-07-15

## 1. Purpose

This directory contains the Architecture Decision Records (ADRs) for KidsAudioBookPlatform. ADRs preserve the context, decision, alternatives, consequences, and follow-up work for significant technical and architectural choices.

An ADR explains **why** an important decision was made. The architecture documents describe the resulting system, while ADRs preserve the decision history that led to it.

## 2. When an ADR Is Required

Create an ADR when a change introduces, replaces, or materially modifies:

- the system architecture style or deployment model;
- a primary framework, runtime, datastore, broker, or infrastructure platform;
- a source of truth or data ownership boundary;
- synchronous or asynchronous communication patterns;
- authentication, authorization, encryption, or trust-boundary strategy;
- API, event, database, or compatibility versioning policy;
- an offline, caching, observability, testing, or migration strategy;
- a new independently deployable service;
- a decision with meaningful long-term cost, risk, or vendor commitment;
- a deliberate exception to an established architecture principle.

An ADR is normally not required for:

- routine implementation details inside an already accepted boundary;
- dependency patch updates with no behavioral or operational impact;
- formatting, naming, or local refactoring choices;
- temporary experiments that cannot reach production and create no persistent contract.

When uncertain, prefer a short ADR over leaving a consequential decision undocumented.

## 3. Status Values

| Status | Meaning |
|---|---|
| `Proposed` | The decision is under discussion and must not be treated as approved architecture. |
| `Accepted` | The decision is approved and is the current architectural direction. |
| `Rejected` | The proposal was considered but not selected. |
| `Superseded` | A newer ADR replaces this decision. The replacement ADR must be referenced. |
| `Deprecated` | The decision remains historically relevant but should no longer be used for new work. |

Only `Accepted` ADRs define the active architecture unless a newer accepted ADR supersedes them.

## 4. Naming and Numbering

File names use:

```text
ADR-XXXX-short-kebab-case-title.md
```

Example:

```text
ADR-0001-modular-monolith-first.md
```

Rules:

- numbers are four digits and never reused;
- numbering is chronological, not grouped by domain;
- titles describe the decision rather than the implementation task;
- renaming an accepted ADR should be avoided because external references may depend on its path;
- a rejected or superseded ADR keeps its original number.

## 5. Required ADR Structure

Each ADR must contain:

1. **Title**
2. **Status**
3. **Date**
4. **Decision owners or reviewers**
5. **Context**
6. **Decision drivers**
7. **Decision**
8. **Consequences**
9. **Alternatives considered**
10. **Risks and mitigations**
11. **Follow-up actions**
12. **Related documents and ADRs**

The decision section must be explicit enough that two reviewers reach the same interpretation of what is approved.

## 6. ADR Lifecycle

### 6.1 Proposal

1. Copy the ADR structure and allocate the next unused number.
2. Set status to `Proposed`.
3. Describe the problem independently from the preferred solution.
4. Record measurable decision drivers where possible.
5. Include viable alternatives and the cost of doing nothing.
6. Link the ADR from the pull request introducing the proposal.

### 6.2 Review

Reviewers validate:

- alignment with product requirements and architecture principles;
- security, privacy, child-safety, and compliance impact;
- data ownership and migration consequences;
- reliability, scalability, observability, and recovery impact;
- implementation and operational cost;
- compatibility with mobile, admin, API, event, and database contracts;
- whether the decision can be reversed and at what cost.

Significant unresolved objections must be captured in the ADR rather than lost in chat or pull-request comments.

### 6.3 Acceptance or Rejection

After review:

- set status to `Accepted` when approved;
- set status to `Rejected` when the proposal is not selected;
- record the decision date and key reviewers;
- update affected architecture documents in the same delivery sequence;
- create implementation tasks for unresolved follow-up actions.

An accepted ADR does not mean implementation is complete. It means the architectural direction is approved.

### 6.4 Superseding a Decision

Accepted ADRs are immutable historical records except for typo fixes, broken links, or factual metadata corrections.

To change an accepted decision:

1. create a new ADR;
2. explain why the previous decision is no longer sufficient;
3. reference the previous ADR in the new one;
4. set the old ADR to `Superseded`;
5. add a link to the replacement ADR in the old record;
6. update architecture documents, migration plans, and implementation roadmaps.

Historical rationale must never be deleted merely because the architecture changed.

## 7. Writing Guidelines

ADRs should be concise but decision-complete.

- Write in clear technical English.
- State facts separately from assumptions.
- Make constraints and uncertainty explicit.
- Avoid promotional language and unsupported claims.
- Quantify cost, volume, latency, availability, or migration impact where evidence exists.
- Record negative consequences, not only benefits.
- Do not copy large sections of general architecture documentation into an ADR.
- Use stable links to related repository documents.
- Never include secrets, credentials, private user data, or sensitive provider payloads.

## 8. Pull Request Rules

A pull request that changes architectural direction must:

- include the proposed or accepted ADR;
- identify affected architecture documents and contracts;
- update diagrams when boundaries or runtime collaboration change;
- include migrations or compatibility steps where applicable;
- identify rollout, rollback, and operational ownership;
- add follow-up work to the implementation roadmap when the change is staged.

A reviewer may block a pull request when a significant decision exists only in code or conversation and is not represented by an ADR.

## 9. Traceability

Accepted ADRs should be referenced from the relevant source-of-truth documents, including as applicable:

- `docs/03_Architecture/Software_Architecture.md`;
- `docs/03_Architecture/Architecture_Principles.md`;
- `docs/03_Architecture/Technology_Stack.md`;
- `docs/03_Architecture/Database_Design.md`;
- `docs/03_Architecture/API_Specification.md`;
- `docs/03_Architecture/Event_Catalog.md`;
- `docs/03_Architecture/Security_Architecture.md`;
- `docs/03_Architecture/C4_Model/README.md`;
- `docs/03_Architecture/Implementation_Roadmap.md`.

Code modules, infrastructure definitions, migrations, and operational runbooks may reference an ADR when the decision materially constrains their implementation.

## 10. Governance and Review Cadence

The architecture owner reviews the ADR index:

- before each major implementation phase;
- before production-readiness approval;
- after a significant incident or scalability constraint;
- when a primary technology approaches end of support;
- when an accepted ADR no longer matches implementation.

The review verifies that:

- every active ADR still reflects the intended architecture;
- superseded decisions point to their replacements;
- follow-up actions are tracked;
- architecture documentation and code do not silently contradict accepted decisions;
- proposed ADRs do not remain unresolved indefinitely.

## 11. Current ADR Index

| ADR | Decision | Status |
|---|---|---|
| [ADR-0001](ADR-0001-modular-monolith-first.md) | Start with a modular monolith | Accepted |
| [ADR-0002](ADR-0002-postgresql-primary-system-of-record.md) | Use PostgreSQL as the primary system of record | Accepted |
| [ADR-0003](ADR-0003-rest-and-rabbitmq-communication.md) | Use REST for synchronous APIs and RabbitMQ for asynchronous events | Accepted |
| [ADR-0004](ADR-0004-flutter-mobile-platform.md) | Use Flutter for the mobile application | Accepted |
| [ADR-0005](ADR-0005-jwt-refresh-token-strategy.md) | Use short-lived JWT access tokens and rotating refresh tokens | Accepted |
| [ADR-0006](ADR-0006-parent-zone-security.md) | Protect Parent Zone with an independent verification boundary | Accepted |
| [ADR-0007](ADR-0007-redis-caching-strategy.md) | Use Redis for rebuildable cache and short-lived coordination data | Accepted |
| [ADR-0008](ADR-0008-object-storage-and-cdn.md) | Store media in object storage and deliver it through a CDN | Accepted |
| [ADR-0009](ADR-0009-observability-stack.md) | Adopt the platform observability stack | Accepted |
| [ADR-0010](ADR-0010-testing-strategy.md) | Adopt a layered automated testing strategy | Accepted |
| [ADR-0011](ADR-0011-feature-flags.md) | Use governed feature flags for controlled rollout | Accepted |
| [ADR-0012](ADR-0012-flyway-database-migrations.md) | Use Flyway for database migrations | Accepted |
| [ADR-0013](ADR-0013-versioning-strategy.md) | Apply explicit API, event, and compatibility versioning | Accepted |
| [ADR-0014](ADR-0014-offline-synchronization.md) | Use operation-based offline synchronization with server authority | Accepted |

## 12. Definition of Done for an ADR

An ADR is complete when:

- its status and ownership are explicit;
- the problem and constraints are understandable without external conversation;
- the selected option and alternatives are documented;
- positive and negative consequences are recorded;
- security, privacy, operational, and migration impact are addressed;
- follow-up work has owners or tracking references;
- affected architecture documents are linked;
- reviewers can determine what implementation is compliant with the decision.
