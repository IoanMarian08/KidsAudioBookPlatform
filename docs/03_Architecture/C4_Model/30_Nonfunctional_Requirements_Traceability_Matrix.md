# Nonfunctional Requirements Traceability Matrix

Version: 1.0.0  
Status: Active  
Owners: Architecture, Engineering, QA, Security, DevOps  
Last reviewed: 2026-07-15

## 1. Purpose

This document maps the platform's nonfunctional requirements to architecture decisions, controls, implementation responsibilities, validation evidence, and operational indicators.

The matrix exists to prevent qualities such as security, reliability, performance, accessibility, privacy, and maintainability from remaining informal intentions. Every important requirement must be traceable from expectation to implementation and from implementation to evidence.

## 2. Traceability model

Each requirement is connected through the following chain:

```text
Requirement
   -> Architecture principle or ADR
   -> Design control
   -> Implementation owner
   -> Verification method
   -> Runtime indicator
   -> Review evidence
```

A requirement is not considered satisfied only because a document mentions it. There must be testable and observable evidence.

## 3. Requirement classification

| Category | Scope |
|---|---|
| Security | Authentication, authorization, secrets, abuse resistance, supply chain |
| Privacy | Data minimization, retention, deletion, telemetry safety, child-data protection |
| Reliability | Availability, resilience, recovery, idempotency, failure isolation |
| Performance | Latency, throughput, resource use, startup and background execution |
| Scalability | Capacity growth, horizontal scaling, queue and storage behavior |
| Maintainability | Modularity, testability, documentation, dependency discipline |
| Operability | Monitoring, alerts, runbooks, deployment, rollback, supportability |
| Accessibility | Usability across abilities, assistive technology, readable interaction |
| Compatibility | Mobile versions, API evolution, event and schema compatibility |
| Cost efficiency | Capacity planning, retention, provider and infrastructure controls |

## 4. Requirement levels

- **Mandatory**: required for launch or legal/security correctness;
- **Target**: expected objective with explicit measurement;
- **Guardrail**: boundary that must not be crossed;
- **Evolutionary**: required at a later maturity or scale threshold.

## 5. Core traceability matrix

| ID | Requirement | Level | Architecture source | Primary controls | Verification | Runtime evidence | Owner |
|---|---|---|---|---|---|---|---|
| NFR-SEC-001 | Protected operations require authenticated and authorized server-side decisions | Mandatory | Security Architecture, ADR-0005, ADR-0006 | Spring Security, resource ownership checks, parent elevation | Security integration tests, authorization matrix tests | Denied-access rate, suspicious-access alerts | Security and Backend |
| NFR-SEC-002 | Refresh-token theft must have bounded impact | Mandatory | ADR-0005 | Opaque hashed tokens, rotation, family reuse detection, device sessions | Token lifecycle and replay tests | Reuse detections, forced revocations | Identity |
| NFR-SEC-003 | Dependencies and artifacts must be verifiable and scanned | Mandatory | Document 23 | Lockfiles, SBOM, scanning, protected CI, signed provenance where supported | CI dependency and container scans | Vulnerability age, policy violations | Security and DevOps |
| NFR-PRI-001 | Child-related data must be minimized and excluded from uncontrolled telemetry | Mandatory | Architecture Principles, documents 12 and 14 | Redaction, allow-listed analytics, structured logging policy | Privacy review, automated log tests | Redaction failures, telemetry audit results | Privacy and Engineering |
| NFR-PRI-002 | Deletion and retention rules must be enforceable and auditable | Mandatory | Document 14, Database Design | Retention jobs, deletion workflows, tombstones where needed | End-to-end deletion tests, restoration-boundary tests | Deletion backlog, retention job success | Data and Backend |
| NFR-REL-001 | Core authenticated API availability target is at least 99.9% monthly after production stabilization | Target | ADR-0009, Logging Monitoring | Health checks, redundancy, graceful degradation, incident response | Load and resilience testing | SLI availability and error budget | DevOps and Backend |
| NFR-REL-002 | Retried write operations must not create duplicate business effects | Mandatory | ADR-0003, Event Catalog | Idempotency keys, unique constraints, inbox/outbox patterns | Retry and duplicate-delivery tests | Duplicate rejection count, inbox conflicts | Backend |
| NFR-REL-003 | Critical data must be recoverable within approved RPO and RTO | Mandatory | Document 18 | Backups, PITR, object versioning, restore runbooks | Scheduled restoration exercises | Restore-test age, backup freshness | DevOps |
| NFR-REL-004 | External-provider failure must not corrupt authoritative state | Mandatory | Documents 13 and 28 | Timeouts, retries, reconciliation, circuit breakers, state machines | Fault-injection and provider-stub tests | Provider errors, reconciliation backlog | Integration owners |
| NFR-PERF-001 | Catalog API p95 latency remains below 300 ms excluding media delivery under approved load profile | Target | ADR-0009, Performance Guidelines | Query design, caching, pagination, indexes | Performance and load tests | API latency percentiles | Backend |
| NFR-PERF-002 | Playback authorization p95 remains below 250 ms under approved load profile | Target | ADR-0009 | Cached entitlement summaries, bounded provider dependency, optimized ownership checks | Load and dependency-degradation tests | Authorization p95 and failures | Entitlements and Media |
| NFR-PERF-003 | Mobile child experience remains responsive on supported lower-end devices | Target | ADR-0004, Mobile Architecture | Frame-budget monitoring, lazy loading, bounded image/audio memory | Device matrix and performance tests | Crash-free sessions, slow frames, memory events | Mobile |
| NFR-SCA-001 | Stateless request processing supports horizontal backend scaling | Evolutionary | ADR-0001, ADR-0005 | Externalized sessions, shared persistence, no local authoritative state | Multi-replica integration tests | Replica saturation and scaling events | Backend and DevOps |
| NFR-SCA-002 | Queue consumers tolerate duplicate, delayed, and out-of-order delivery | Mandatory | ADR-0003 | Idempotent handlers, version checks, ordering rules per aggregate | Messaging contract and chaos tests | Redelivery, DLQ, lag, duplicate count | Backend |
| NFR-MNT-001 | Module boundaries prevent repository and entity access across bounded contexts | Mandatory | ADR-0001, Backend Architecture | Public module APIs, architecture tests, package visibility | ArchUnit or equivalent tests | Boundary violations in CI | Architecture and Backend |
| NFR-MNT-002 | Critical behavior is protected by layered automated tests | Mandatory | ADR-0010 | Unit, integration, contract, E2E suites | CI quality gates | Test pass rate, flaky-test age | QA and Engineering |
| NFR-MNT-003 | Architecture documentation and implementation remain aligned | Guardrail | Document 26, C4 README | Review checklist, ADR process, docs-as-code | Periodic architecture conformance review | Documentation drift findings | Architecture |
| NFR-OPS-001 | Every production request and event can be correlated across components | Mandatory | ADR-0009, Logging Monitoring | Correlation IDs, trace context, event metadata | Integration telemetry tests | Trace coverage, missing-context rate | DevOps and Engineering |
| NFR-OPS-002 | Critical alerts must be actionable, owned, and linked to runbooks | Mandatory | ADR-0009, Operations Handbook | Alert ownership, severity rules, runbook links | Alert simulation and incident drills | Unowned alerts, false-positive rate | DevOps |
| NFR-OPS-003 | Releases support rollback or safe forward recovery | Mandatory | Document 17, ADR-0012 | Immutable artifacts, expand-and-contract migrations, feature flags | Deployment rehearsal and rollback tests | Rollback success, change failure rate | DevOps and Engineering |
| NFR-ACC-001 | Core child and parent journeys support accessibility requirements | Mandatory | Architecture Principles, Mobile Architecture | Semantics, scalable text, contrast, reduced motion, screen-reader labels | Automated and manual accessibility tests | Accessibility defect backlog | Mobile and Product |
| NFR-CMP-001 | Supported mobile clients remain compatible with backend changes | Mandatory | ADR-0013, document 24 | Additive API changes, capability negotiation, deprecation windows | Contract tests against supported client versions | Unsupported-client traffic | Backend and Mobile |
| NFR-CMP-002 | Event consumers tolerate additive schema evolution | Mandatory | ADR-0013, Event Catalog | Versioned envelopes, tolerant readers, dual publishing when needed | Consumer-driven contract tests | Event-deserialization failures | Backend |
| NFR-COST-001 | Infrastructure growth is monitored against active-user and workload growth | Target | Document 22 | Budgets, capacity model, retention limits, scaling thresholds | Monthly cost and capacity review | Cost per active account, storage growth | Architecture and DevOps |

## 6. Security verification evidence

Acceptable evidence includes:

- authentication and authorization integration tests;
- privilege-escalation and tenant-isolation tests;
- dependency, image, and secret scans;
- secure configuration checks;
- penetration-test findings and closure records;
- threat-model reviews;
- incident simulations;
- audit-log validation.

Security evidence must identify the tested version, environment, date, owner, and unresolved findings.

## 7. Reliability verification evidence

Reliability evidence includes:

- timeout and retry behavior tests;
- dependency outage simulation;
- duplicate event and idempotency tests;
- queue backlog and recovery exercises;
- database failover and restore tests;
- object-storage recovery tests;
- rollback or forward-recovery rehearsals;
- mobile offline/online transition tests.

A happy-path integration test alone is insufficient evidence for reliability.

## 8. Performance verification model

Performance targets must always reference a documented load profile containing:

- concurrent users;
- request mix;
- dataset size;
- cache state;
- infrastructure allocation;
- external-dependency behavior;
- test duration;
- warm-up period;
- success and error thresholds.

Results without a reproducible load profile cannot be used to approve capacity or release readiness.

## 9. Accessibility verification

Accessibility validation combines:

- static analysis where available;
- widget and component checks;
- screen-reader testing on iOS and Android;
- scalable-text testing;
- contrast and focus validation;
- reduced-motion behavior;
- interaction testing for users with motor limitations;
- parent-zone form and error-message review.

Critical child and parent journeys require manual validation on representative devices before release.

## 10. Evidence status

Each requirement should be tracked as:

- **Not started**;
- **Designed**;
- **Implemented**;
- **Verified**;
- **Operationally proven**;
- **Exception approved**.

`Operationally proven` means runtime evidence confirms that the implementation works under real or production-like conditions.

## 11. Exception process

An unmet mandatory requirement requires:

1. documented gap and affected capability;
2. risk assessment;
3. temporary compensating controls;
4. accountable owner;
5. remediation target date;
6. explicit approval by architecture and the relevant security, privacy, or product owner;
7. expiry and re-review date.

Exceptions must not be hidden in issue comments or informal chat.

## 12. Release use

Before a production release, the release owner must identify:

- which NFRs are affected by the change;
- evidence that affected requirements remain satisfied;
- new or changed runtime indicators;
- known exceptions;
- rollback or containment actions if indicators regress.

High-risk changes require direct links from the release record to the relevant evidence.

## 13. Maintenance

The matrix must be updated when:

- an ADR changes architecture behavior;
- an SLO or supported-platform target changes;
- a new provider or bounded context is introduced;
- incidents reveal a missing requirement;
- compliance or privacy obligations change;
- test evidence is replaced or invalidated;
- a requirement becomes operationally proven.

## 14. Definition of done

A nonfunctional requirement is considered fully traceable when:

- its wording and scope are unambiguous;
- an architecture source exists;
- implementation controls are identified;
- an owner is accountable;
- repeatable verification exists;
- runtime evidence is available where applicable;
- exceptions and residual risks are visible;
- the evidence is reviewed and current.
