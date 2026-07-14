# ADR-0013: Versioning Strategy

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture and Engineering

## Context

The platform includes independently evolving mobile, backend, admin, API, event, and database contracts. Releases must remain understandable and compatible, especially because mobile clients cannot be upgraded instantly.

## Decision

Use semantic versioning for deployable applications and libraries, explicit major versions for public HTTP APIs, and schema versions for asynchronous event payloads.

## Application Versions

Backend, mobile, and admin releases follow `MAJOR.MINOR.PATCH`:

- MAJOR: intentionally incompatible product or platform change.
- MINOR: backward-compatible features.
- PATCH: backward-compatible fixes.

Build metadata may identify CI builds but does not replace the release version.

## HTTP API Versioning

Public client APIs use path-based major versioning:

```text
/api/v1/...
```

Minor compatible additions do not create a new path version. Existing fields must not change meaning. New response fields are optional for clients. Removing or renaming fields requires a new major API version and a documented migration window.

## Event Versioning

Every event envelope contains `eventType`, `eventVersion`, `eventId`, `occurredAt`, `producer`, `correlationId`, and `payload`. Consumers must ignore unknown optional fields. Breaking payload changes create a new event version and may temporarily use dual publishing.

## Database Versioning

Database schema version is controlled by Flyway migrations and is not coupled numerically to application releases. Deployments must document compatible application and schema ranges.

## Mobile Compatibility

The backend publishes minimum supported and recommended mobile versions. Unsupported clients receive a structured upgrade-required response only when continued operation is unsafe or impossible. Feature flags and capability negotiation are preferred over unnecessary forced upgrades.

## Deprecation

Deprecated APIs and events must include ownership, replacement, announcement date, telemetry, and removal date. Removal occurs only after usage falls below the approved threshold and the support window ends.

## Consequences

### Positive

- Predictable compatibility rules.
- Safer mobile and backend evolution.
- Clear contract deprecation.

### Negative

- Temporary maintenance of parallel versions.
- Additional contract testing and telemetry.

## Rejected Alternatives

- No explicit versioning: creates accidental breaking changes.
- Versioning every minor API change: produces unnecessary fragmentation.
- Header-only API versions: less visible and harder to operate for this project.