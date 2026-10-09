# Service Extraction and Migration Playbook

Version: 1.0.0  
Status: Active Draft  
Owners: Architecture, Backend Engineering, DevOps, Security  
Last reviewed: 2026-07-15

## 1. Purpose

This document defines how a bounded context may be extracted from the initial modular monolith into an independently deployable service without losing data integrity, security, operability, or delivery speed.

Service extraction is an architectural migration, not a code-copy exercise. It changes deployment, ownership, data access, failure modes, observability, security boundaries, and operating cost.

## 2. Guiding principle

A module is extracted only when evidence shows that independent deployment creates more value than operational complexity.

Valid drivers include:

- sustained independent scaling needs;
- materially different availability objectives;
- separate team ownership;
- security or compliance isolation;
- release cadence conflicts;
- resource contention inside the monolith;
- provider-specific operational requirements;
- stable domain boundaries and mature contracts.

Extraction must not be justified only by preference for microservices.

## 3. Preconditions

Before approval, the candidate module must have:

- explicit domain ownership;
- no circular module dependencies;
- public application contracts;
- documented events and synchronous APIs;
- known data ownership;
- architecture tests protecting boundaries;
- independent integration tests;
- measurable operational reason for extraction;
- an accountable service owner;
- a cost and capacity estimate;
- rollback and coexistence plans.

If these are absent, improve modularity before changing deployment topology.

## 4. Extraction assessment

The proposal must score the following areas:

| Area | Questions |
|---|---|
| Domain maturity | Is the boundary stable and understandable? |
| Coupling | How many synchronous and data dependencies exist? |
| Data | Can authoritative data be separated safely? |
| Operations | Who owns runtime, alerts, incidents, and releases? |
| Reliability | What new network and queue failure modes appear? |
| Security | Does the new boundary improve or weaken control? |
| Cost | What infrastructure and support cost is added? |
| Delivery | Does independent deployment remove a real bottleneck? |
| Migration | Can old and new implementations coexist safely? |

An ADR records the decision and supporting evidence.

## 5. Preferred migration pattern

Use an incremental strangler-style migration:

1. harden the internal module boundary;
2. define versioned external contracts;
3. introduce an adapter at the call site;
4. deploy the new service in shadow or non-authoritative mode;
5. replicate or migrate data safely;
6. shift selected reads;
7. shift writes under controlled routing;
8. verify correctness and SLOs;
9. remove old implementation paths;
10. remove obsolete data and compatibility code later.

A big-bang extraction is prohibited unless the domain is isolated and rollback is trivial.

## 6. Target service boundary

The extracted service owns:

- its domain model;
- application use cases;
- persistence schema or database;
- migrations;
- public synchronous API;
- produced events;
- consumed events;
- runtime configuration;
- dashboards, alerts, and runbooks;
- release and rollback lifecycle.

The monolith must stop writing the extracted service's authoritative data.

## 7. Contract design

Before extraction, define:

- operation purpose;
- authentication and authorization;
- request and response schemas;
- error catalog;
- idempotency semantics;
- timeout and retry policy;
- consistency expectations;
- event contracts;
- versioning and deprecation;
- rate limits;
- observability fields;
- ownership and support path.

Internal Java interfaces are not sufficient as distributed contracts.

## 8. Communication choice

Use synchronous communication when the caller requires an immediate business decision. Use asynchronous events when eventual consistency is acceptable and temporal decoupling is valuable.

Do not replace every in-process call with HTTP. Reconsider the workflow and minimize chatty communication.

A distributed transaction is not introduced to preserve the shape of the old monolith flow. Use local transactions, outbox, idempotent consumers, sagas, or compensating actions.

## 9. Data-separation strategies

Choose one strategy explicitly.

### 9.1 Schema transfer

Move the owned schema or tables to the new service database after all cross-module access is removed.

### 9.2 Online copy and cutover

Copy data while the old system remains active, synchronize deltas, validate, then switch authority.

### 9.3 Event-built read model

Build a new service-owned model from authoritative events, then switch reads once completeness is verified.

### 9.4 New-data ownership

The service owns only new records after a cutover point while historical data remains available through a controlled legacy adapter.

The selected approach must document consistency, reconciliation, rollback, retention, and deletion behavior.

## 10. Data migration phases

1. inventory tables, constraints, indexes, jobs, and hidden consumers;
2. classify authoritative and derived data;
3. remove unauthorized direct access;
4. define migration identifiers and checkpoints;
5. perform dry runs with production-like volume;
6. copy data in bounded batches;
7. verify counts, checksums, invariants, and samples;
8. synchronize changes after the initial copy;
9. freeze or coordinate final writes;
10. switch authority;
11. monitor reconciliation;
12. retain rollback data for the approved window;
13. remove obsolete copies after formal approval.

## 11. Dual-write policy

Uncoordinated dual writes are prohibited.

When temporary dual writing is unavoidable:

- one system remains authoritative;
- every write has an idempotency key;
- failures are persisted and retried;
- reconciliation detects divergence;
- ordering expectations are documented;
- the dual-write period has an expiry;
- rollback behavior is tested.

Prefer transactional outbox and asynchronous replication over two independent synchronous database writes.

## 12. Read migration

Reads may move before writes when the new service can build a trusted read model.

Use feature flags or routing percentages to control:

- internal test accounts;
- selected environments;
- a small traffic percentage;
- read-only endpoints;
- specific regions or client versions.

Shadow reads compare old and new responses without affecting the user. Differences must be classified before increasing traffic.

## 13. Write migration

Write cutover requires:

- idempotent commands;
- stable latency and error rate;
- complete authorization enforcement;
- verified event publication;
- reconciliation dashboards;
- tested retries and duplicate handling;
- rollback routing;
- support and incident readiness.

A write is never considered successful until it is committed in the authoritative service.

## 14. Authentication and authorization

The new service validates identity and authorization independently. It must not trust headers supplied directly by an untrusted client.

Document:

- token audience;
- required scopes or roles;
- service-to-service identity;
- Parent Zone elevation requirements;
- profile ownership checks;
- entitlement checks;
- administrative permissions;
- audit requirements.

## 15. Network and resilience model

Extraction introduces partial failure. Define:

- connection and request timeouts;
- bounded retries with jitter;
- circuit breaking where useful;
- bulkheads and concurrency limits;
- queue retry and dead-letter policy;
- fallback behavior;
- degraded-mode behavior;
- dependency health signals;
- overload and backpressure handling.

Retries must not multiply across layers without a bounded end-to-end budget.

## 16. Observability requirements

Before production traffic, the service must expose:

- request rate, error rate, and latency percentiles;
- dependency latency and failures;
- database and connection-pool saturation;
- queue depth, lag, retries, and dead letters;
- business-success and rejection metrics;
- deployment version;
- trace and correlation propagation;
- migration and reconciliation metrics;
- SLO dashboards and actionable alerts.

Logs, metrics, and traces must correlate across the monolith and extracted service.

## 17. Service-level objectives

The extraction ADR defines:

- availability target;
- latency target;
- event-processing delay;
- recovery time objective;
- recovery point objective;
- support hours;
- error-budget policy;
- dependency expectations.

The target must be no weaker than the user journey requires.

## 18. Deployment strategy

The service has an independent pipeline with:

- deterministic build;
- security and dependency scans;
- unit, integration, contract, and smoke tests;
- infrastructure provisioning;
- migration validation;
- progressive deployment;
- health and readiness checks;
- automated rollback triggers where safe;
- release evidence and artifact retention.

The monolith and service releases must not require permanent lockstep deployment.

## 19. Testing strategy

Required tests include:

- domain and application unit tests;
- persistence integration tests;
- producer and consumer contract tests;
- authentication and authorization tests;
- event idempotency and ordering tests;
- timeout, retry, and unavailable-dependency tests;
- migration and reconciliation tests;
- load and capacity tests;
- rollback and failback exercises;
- end-to-end tests for affected journeys.

## 20. Shadow mode

Where practical, deploy the new service before it is authoritative.

Shadow mode may:

- consume copies of production events;
- perform read comparisons;
- calculate decisions without applying them;
- produce metrics without user-visible effects.

Shadow processing must not send notifications, mutate provider state, charge users, or create duplicate business effects.

## 21. Cutover checklist

Before cutover confirm:

- contracts are versioned and published;
- data is reconciled;
- alerts and dashboards are active;
- on-call ownership is assigned;
- runbooks exist;
- rollback is tested;
- feature flags and routing controls work;
- capacity has headroom;
- security review is complete;
- support teams understand expected behavior;
- old and new systems can coexist for the rollback window.

## 22. Rollback

Rollback may mean:

- route reads back to the monolith;
- route writes back before authority changes;
- stop event consumption;
- restore the previous service version;
- replay persisted commands or events;
- reconcile data after recovery.

After write authority moves, rollback must not discard writes accepted by the new service. A tested reverse-synchronization or forward-fix plan is required.

## 23. Failure scenarios

The migration plan must cover:

- service unavailable during cutover;
- database migration failure;
- incomplete data copy;
- event backlog growth;
- duplicate events;
- out-of-order events;
- inconsistent authorization results;
- stale DNS or routing configuration;
- partial region failure;
- rollback after new writes exist;
- provider-rate-limit exhaustion;
- reconciliation mismatch above threshold.

## 24. Decommissioning the old implementation

Decommission only after:

- production traffic has remained stable for the approved period;
- old-path usage is zero;
- data reconciliation is complete;
- rollback window has expired;
- audit and retention obligations are preserved;
- documentation and diagrams are updated;
- old alerts, jobs, credentials, tables, and flags are inventoried.

Removal occurs in stages and in separate releases from the initial cutover.

## 25. Cost controls

Track incremental cost for:

- compute;
- database;
- messaging;
- network transfer;
- observability;
- backups;
- CI/CD;
- on-call and operational support.

The service must have capacity assumptions and scaling thresholds. Extraction is reconsidered if cost grows without delivering the expected organizational or technical benefit.

## 26. Ownership transfer

The receiving team accepts:

- source ownership;
- production support;
- security remediation;
- dependency upgrades;
- data stewardship;
- contract evolution;
- incident response;
- documentation maintenance;
- cost accountability.

Ownership is incomplete until operational responsibilities are transferred.

## 27. Migration evidence

Retain:

- ADR and assessment;
- approved architecture diagrams;
- contract versions;
- migration scripts and reports;
- reconciliation results;
- load-test evidence;
- security review;
- cutover timeline;
- incident and rollback records;
- final decommission approval.

## 28. Definition of done

Extraction is complete only when:

- the service is authoritative for its domain;
- the monolith no longer accesses its internal data;
- contracts and ownership are explicit;
- SLOs and alerts are active;
- data is reconciled;
- rollback obligations are closed;
- old code, schemas, flags, credentials, and jobs are removed;
- architecture documentation is current;
- operational cost and outcomes are reviewed.
