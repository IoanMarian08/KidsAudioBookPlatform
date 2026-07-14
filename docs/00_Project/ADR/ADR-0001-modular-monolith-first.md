# ADR-0001: Start with a Modular Monolith

Status: Accepted
Date: 2026-07-14

## Context

KidsAudioBookPlatform targets a future microservice-capable architecture, but the first release will be built by a small team and must minimize operational complexity while preserving clear business boundaries. Deploying many services from the beginning would introduce distributed transactions, network failure modes, duplicated infrastructure, increased local-development cost, and a larger observability burden before real scaling data exists.

## Decision

The initial backend will be implemented as a modular monolith using Java 21 and Spring Boot. Business capabilities will be separated into explicit modules aligned with bounded contexts such as identity, profiles, catalog, playback, subscriptions, notifications, media, and administration.

Each module must:

- own its domain model and application services;
- expose explicit internal interfaces;
- avoid direct access to another module's repositories;
- publish domain events for important state changes;
- keep database ownership visible through schema and migration conventions;
- remain independently testable;
- avoid circular dependencies.

Extraction into a standalone service is permitted only when operational or organizational evidence justifies it.

## Consequences

### Positive

- Faster delivery and easier local development.
- Simpler transactions for early business flows.
- Lower infrastructure and observability cost.
- Clear path toward later service extraction.
- Easier refactoring while the domain is still evolving.

### Negative

- Modules share one deployment unit initially.
- Poor discipline could allow accidental coupling.
- A failure in one module may affect the entire backend process.
- Independent scaling is unavailable until extraction.

## Alternatives Considered

### Microservices from the first release

Rejected because the expected early traffic and team size do not justify the operational cost.

### Traditional layered monolith without bounded modules

Rejected because it encourages shared repositories, unclear ownership, and difficult future extraction.

### Serverless functions for all capabilities

Rejected because the domain includes long-lived workflows, transactional state, media orchestration, and shared operational requirements that are better served by a cohesive backend.

## Extraction Criteria

A module may become a service when one or more conditions are sustained:

- independent scaling is required;
- release cadence differs materially;
- availability requirements differ;
- ownership moves to a separate team;
- resource usage causes platform contention;
- security or compliance isolation is required;
- the boundary is stable and integration contracts are mature.

## Follow-up Actions

- Enforce module dependency rules with architecture tests.
- Maintain module-level package and schema conventions.
- Use outbox-ready domain events even before physical extraction.
- Review extraction candidates after production metrics are available.
