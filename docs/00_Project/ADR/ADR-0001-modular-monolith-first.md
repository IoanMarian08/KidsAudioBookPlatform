# ADR-0001: Start with a Modular Monolith

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture and Backend Engineering
- **Last reviewed:** 2026-07-15

## Context

KidsAudioBookPlatform targets a future microservice-capable architecture, but the first releases will be built by a small team and must minimize operational complexity while preserving clear business boundaries.

The product contains multiple business capabilities: identity, parent security, child profiles, catalog, media, playback, subscriptions, entitlements, advertising, notifications, administration, audit, and analytics. These capabilities have different responsibilities, but they do not initially justify separate deployment pipelines, databases, on-call ownership, and distributed failure modes.

Starting with many independently deployed services would introduce:

- network failures inside ordinary business workflows;
- distributed transactions and eventual-consistency concerns before they are required;
- duplicated deployment, configuration, observability, and security infrastructure;
- higher local-development and testing cost;
- more difficult refactoring while the domain model is still evolving;
- increased operational burden without production evidence that independent scaling is necessary.

A traditional unstructured monolith would reduce deployment complexity but would not protect domain boundaries or provide a safe path toward future extraction.

## Decision

The initial backend will be implemented as a **modular monolith** using Java 21 and Spring Boot.

The backend is deployed as one primary application unit, while business capabilities are separated into explicit modules aligned with bounded contexts.

Initial modules include:

- Identity and Access;
- Family and Profiles;
- Catalog and Editorial;
- Media;
- Listening and Progress;
- Subscriptions and Entitlements;
- Advertising Policy;
- Notifications;
- Administration;
- Audit and Compliance;
- Analytics.

Deployment topology does not define domain ownership. A module remains an independent conceptual boundary even while several modules run in the same process.

## Module Contract

Every business module must:

1. own its domain model and business invariants;
2. own its application use cases;
3. expose explicit public application interfaces;
4. keep internal classes inaccessible to other modules;
5. own its persistence mappings and migrations;
6. publish domain events for meaningful state changes;
7. consume other modules only through public contracts or events;
8. remain independently testable;
9. avoid circular dependencies;
10. define an accountable technical owner.

A module must not:

- access another module's repositories directly;
- import another module's JPA entities;
- write another module's tables;
- expose internal package structures through public APIs;
- use shared mutable domain objects across boundaries;
- depend on deployment-specific assumptions.

## Dependency Direction

The preferred internal structure is:

```text
API / Messaging / Schedulers
            ↓
      Application Layer
            ↓
        Domain Layer

Infrastructure Adapters → Application and Domain Ports
```

The domain layer must remain independent of Spring MVC, JPA, RabbitMQ, Redis, object-storage SDKs, and external-provider models.

Cross-module dependencies must point toward stable public contracts. Architecture tests must reject dependencies on internal packages.

## Communication Rules

### Synchronous communication

Use direct in-process application interfaces when:

- the caller requires an immediate result;
- the operation belongs to the same transaction boundary;
- temporary unavailability cannot be tolerated;
- the interaction does not create prohibited coupling.

In-process calls must not be disguised as HTTP calls inside the same deployment.

### Asynchronous communication

Use domain or integration events when:

- several consumers may react independently;
- eventual consistency is acceptable;
- processing is slow or retryable;
- the producer does not require an immediate result;
- the interaction should remain extraction-ready.

Events must follow the Event Catalog and use reliable publication through the transactional outbox where consistency matters.

## Data Ownership

PostgreSQL is initially shared as infrastructure, but business ownership remains explicit.

Each module must have:

- clearly named tables or schemas;
- module-owned Flyway migrations;
- no direct writes from other modules;
- documented read-model or contract access;
- a defined extraction path.

Shared-database deployment does not permit shared ownership.

Redis, RabbitMQ, and object storage must follow the same ownership rules through namespaced keys, exchanges, queues, buckets, prefixes, and lifecycle policies.

## Transaction Boundaries

A database transaction should normally remain inside one module.

A temporary cross-module transaction is permitted only when all of the following are true:

- the modules run in the same deployment;
- the invariant genuinely requires atomicity;
- ownership remains explicit;
- the coupling is documented;
- an extraction strategy is understood.

Long-running workflows must use process managers, orchestration, or events instead of holding database transactions open.

## Shared Kernel

A small shared kernel is permitted for technical concerns such as:

- identifiers;
- clocks and time abstractions;
- standard API errors;
- correlation context;
- event-envelope primitives;
- common testing utilities.

The shared kernel must not contain business entities, business services, or rules owned by a specific module.

Every addition to the shared kernel requires review because shared code increases coupling.

## Runtime Isolation

Although the application initially runs as one process, module-specific work must be operationally visible.

Metrics, logs, traces, scheduled jobs, event consumers, and failure counts must identify the owning module.

Resource-intensive work such as media processing and large notification batches may run in separate worker processes while remaining part of the same logical modular architecture.

## Failure Containment

The modular monolith must avoid allowing one optional capability to destabilize core listening flows.

Required controls include:

- bounded thread pools for background work;
- timeouts for external providers;
- circuit breakers where appropriate;
- queue-based isolation for slow work;
- bulkheads for media and notification processing;
- graceful degradation for cache and analytics failures;
- health indicators that distinguish critical and non-critical dependencies.

## Security Boundaries

Module boundaries do not replace authorization.

Every protected use case must independently validate:

- authenticated actor;
- account status;
- profile ownership;
- entitlement;
- Parent Zone elevation where required;
- administrative permission;
- resource state.

Internal calls must not be treated as automatically trusted simply because they occur in the same process.

## Testing and Enforcement

The architecture is enforced through:

- unit tests for domain rules;
- module-level integration tests;
- architecture tests for dependency direction;
- contract tests for public module interfaces;
- event-schema tests;
- repository tests with PostgreSQL;
- full-application tests for critical cross-module workflows.

CI must fail when a module imports another module's internal package or creates a forbidden circular dependency.

Recommended enforcement tools include ArchUnit, Maven module boundaries, package visibility, and Spring Modulith-compatible verification where appropriate.

## Deployment Model

The initial production deployment may include:

- one Spring Boot API application;
- one or more worker processes using the same codebase;
- PostgreSQL;
- Redis;
- RabbitMQ;
- object storage;
- CDN and external providers.

All deployments use the same reviewed module contracts. Scaling additional application replicas does not change domain ownership.

## Extraction Criteria

A module may become an independently deployed service only when one or more conditions are sustained and measurable:

- independent scaling is required;
- release cadence differs materially;
- availability objectives differ;
- ownership moves to a separate team;
- resource use causes platform contention;
- security or compliance isolation is required;
- provider integration risk should be isolated;
- the domain boundary is stable;
- integration contracts are mature;
- deployment independence provides more value than operational cost.

A single temporary performance incident is not enough to justify extraction.

## Extraction Readiness Checklist

Before extraction, confirm:

- the module owns all required data;
- cross-module database access has been removed;
- synchronous dependencies are documented;
- events and APIs are versioned;
- idempotency is implemented;
- observability exists at the boundary;
- failure and retry policies are defined;
- data migration and rollback plans exist;
- security policies remain enforceable;
- service-level objectives justify independent operation.

Extraction requires a new ADR.

## Consequences

### Positive

- faster initial delivery;
- simpler local development;
- lower infrastructure cost;
- easier transactional workflows during early development;
- clearer domain boundaries than a traditional monolith;
- easier refactoring while the domain is evolving;
- measurable and controlled path toward service extraction;
- fewer distributed failure modes in the first releases.

### Negative

- modules share one primary deployment unit;
- a process-level failure may affect several capabilities;
- independent scaling is limited before extraction;
- architecture discipline is required to prevent boundary erosion;
- shared infrastructure can hide ownership problems;
- large builds and test suites may require later optimization.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Accidental cross-module repository access | Package restrictions and architecture tests |
| Shared database becomes shared ownership | Explicit schemas, migration ownership, and reviews |
| One module consumes excessive resources | Metrics, bounded executors, worker isolation, and extraction review |
| Events are added without reliable delivery | Transactional outbox and contract tests |
| Shared kernel grows into a business dumping ground | Strict review and ownership rules |
| Premature extraction | Require production evidence and a dedicated ADR |
| Delayed extraction despite clear need | Review extraction indicators during architecture governance |

## Alternatives Considered

### Microservices from the first release

Rejected because expected early traffic, team size, and release needs do not justify the operational and cognitive cost.

### Traditional layered monolith

Rejected because it encourages horizontal technical layers, shared repositories, unclear ownership, and difficult future extraction.

### Serverless functions for all capabilities

Rejected because the platform contains transactional workflows, long-lived business state, media orchestration, offline synchronization, and shared operational requirements that benefit from a cohesive backend.

### Separate deployable service for every bounded context

Rejected because bounded contexts define ownership, not necessarily deployment. Independent deployment must be earned through measurable need.

## Validation Indicators

The decision remains appropriate while:

- the team can deploy the backend safely as one coordinated unit;
- release frequency is not constrained by unrelated modules;
- no module requires materially different scaling or availability;
- build and test duration remain manageable;
- incidents can be isolated operationally;
- module boundaries remain enforceable.

The decision must be reviewed when these indicators stop being true.

## Follow-up Actions

- enforce module dependency rules with architecture tests;
- maintain module-level package and schema conventions;
- define public module interfaces explicitly;
- use outbox-ready domain events before physical extraction;
- add module ownership to logs, metrics, and dashboards;
- maintain the data-ownership matrix;
- document cross-module contracts;
- review extraction candidates using production evidence;
- create a new ADR for every approved service extraction.
