# ADR-0013: Versioning Strategy

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture and Engineering

## Context

KidsAudioBookPlatform contains independently evolving mobile, backend, admin, API, event, database, local-storage, and media-manifest contracts. Releases must remain understandable and compatible, especially because mobile clients cannot be upgraded instantly and background workers may process messages produced by older application versions.

A single version number cannot safely represent every contract. The platform therefore requires a coordinated strategy that distinguishes product releases from API, event, schema, and content compatibility.

## Decision

Use:

- semantic versioning for deployable applications and reusable libraries;
- explicit major versions for public HTTP APIs;
- explicit schema versions for asynchronous events;
- Flyway-controlled versions for PostgreSQL schema evolution;
- migration versions for the mobile local database;
- explicit versions for offline manifests and persisted client payloads;
- documented compatibility ranges between independently deployed components.

Versioning must communicate compatibility, not merely release chronology.

## General Principles

1. Breaking changes are explicit.
2. Backward-compatible evolution is preferred.
3. Mobile compatibility windows are treated as a product and operational requirement.
4. Clients branch on stable contracts, not informal message text or undocumented behavior.
5. Deprecation requires telemetry and a removal plan.
6. A version number does not replace feature flags or capability negotiation.
7. Database versions are not coupled numerically to application versions.
8. Event and API versions are owned by the producing contract owner.

## Application Versions

Backend, mobile, admin dashboard, workers, and reusable internal libraries follow:

```text
MAJOR.MINOR.PATCH
```

### MAJOR

Incremented for intentionally incompatible platform or application behavior, such as:

- removing a supported integration contract;
- replacing a persistence format without migration compatibility;
- dropping support for an established public capability;
- introducing a product-level behavior that requires coordinated migration.

### MINOR

Incremented for backward-compatible capabilities, such as:

- new API endpoints;
- optional response fields;
- new administrative workflows;
- new mobile features compatible with the existing backend contract;
- new event types.

### PATCH

Incremented for backward-compatible fixes, security patches, performance improvements, and documentation-only release corrections.

Build metadata may identify CI builds:

```text
1.4.2+build.183.sha.abc1234
```

Build metadata does not replace the release version and must not be used as the only compatibility signal.

## Release Identity

Each deployed artifact must expose:

- application name;
- semantic version;
- build identifier;
- source commit SHA;
- build timestamp;
- environment;
- supported API versions;
- compatible database schema range where applicable.

This information is available through internal diagnostics and must not expose secrets.

## HTTP API Versioning

Public mobile and administrative APIs use path-based major versioning:

```text
/api/v1/...
```

### Compatible changes within a major version

Allowed changes include:

- adding optional response fields;
- adding endpoints;
- adding optional request fields with safe defaults;
- expanding enum values only when clients are required to handle unknown values safely;
- adding pagination metadata;
- adding headers that clients may ignore.

### Breaking changes

A new major API version is required when:

- removing or renaming fields;
- changing a field type;
- changing field meaning;
- making an optional request field mandatory;
- changing authentication semantics;
- changing pagination or error semantics incompatibly;
- changing identifiers in a way old clients cannot understand.

### Contract rules

- Existing fields must not silently change meaning.
- New fields are optional for existing clients unless a new major version is introduced.
- Clients must ignore unknown response fields.
- Servers must reject unsupported request versions with a structured error.
- Error codes are versioned by semantic stability and are not reused for a new meaning.
- OpenAPI is the authoritative HTTP contract.

## API Version Lifecycle

Every API major version has:

- owner;
- introduction date;
- supported client range;
- deprecation date when applicable;
- replacement path;
- usage telemetry;
- planned removal date;
- migration documentation.

Old and new API versions may coexist during a migration window. Shared domain logic should be reused behind version-specific adapters rather than duplicated without control.

## Event Versioning

Every event envelope contains:

```json
{
  "eventType": "StoryPublished",
  "eventVersion": 1,
  "eventId": "01J...",
  "occurredAt": "2026-07-15T18:20:31Z",
  "producer": "catalog",
  "correlationId": "01J...",
  "payload": {}
}
```

### Compatible event evolution

The same event version may be retained when:

- adding optional fields;
- adding metadata that consumers may ignore;
- clarifying documentation without changing semantics.

### Breaking event evolution

A new event version is required when:

- removing or renaming a field;
- changing a field type;
- changing field meaning;
- changing requiredness incompatibly;
- changing identifier semantics;
- changing ordering or delivery assumptions encoded in the contract.

Consumers must ignore unknown optional fields and remain idempotent.

## Event Migration Strategies

Depending on risk, producers may use:

- dual publishing of old and new versions;
- adapter consumers that translate old events;
- replay into a new projection;
- a bounded support window for the previous version;
- coordinated cutover after consumer telemetry confirms readiness.

Event versions are never inferred from queue names alone; the envelope remains authoritative.

## Database Versioning

The PostgreSQL schema version is controlled by Flyway migrations and is not coupled numerically to application releases.

Deployments must document:

- required minimum schema version;
- maximum known compatible schema version where relevant;
- whether the release supports expand-and-contract overlap;
- any required backfill or feature-flag gate.

Application rollback is allowed only while the database remains compatible with the previous application version.

## Mobile Local Database Versioning

The Flutter application local database uses explicit migration versions.

Rules:

1. Every local schema change has a deterministic migration.
2. App upgrades must preserve valid downloads, progress, favorites, and queued operations where possible.
3. Failed migration must not silently corrupt local state.
4. Security-sensitive values remain in secure storage rather than ordinary local tables.
5. Destructive reset is a last resort and must preserve server-recoverable state where possible.
6. Migration tests cover supported upgrade paths.

## Offline Manifest Versioning

Download and playback manifests include an explicit manifest version.

A new major manifest version is required when the client can no longer interpret:

- asset structure;
- checksum rules;
- encryption metadata;
- entitlement expiry behavior;
- synchronization cursor semantics;
- required media components.

The backend may serve different manifest versions based on client capability.

## Mobile Compatibility

The backend publishes:

- minimum supported mobile version;
- recommended mobile version;
- current store version where known;
- capability requirements for selected features.

### Minimum supported version

A client below this version may be blocked only when continued operation is unsafe, insecure, incompatible, or legally non-compliant.

### Recommended version

A client below this version may continue with a non-blocking upgrade recommendation.

### Capability negotiation

Feature flags and server-returned capabilities are preferred over unnecessary forced upgrades.

Examples:

```json
{
  "capabilities": {
    "offlineManifestV2": true,
    "synchronizedText": true,
    "parentZoneBiometrics": false
  }
}
```

The server remains authoritative for security, entitlement, and subscription decisions regardless of client version.

## Admin Dashboard Compatibility

The admin dashboard is deployed more rapidly than mobile, but it still requires compatibility with backend APIs during rolling deployment and rollback.

Admin releases must:

- declare supported API major versions;
- avoid depending on a new backend field before the backend is available;
- tolerate additive response fields;
- use feature flags for staged rollout of privileged workflows;
- display a clear maintenance state when no compatible backend contract exists.

## Dependency and Library Versioning

Internal reusable libraries follow semantic versioning.

Rules:

- dependency versions are pinned;
- incompatible library changes require a major version;
- snapshot or floating versions are not allowed in production builds;
- dependency upgrades are tested and recorded;
- security patches may require accelerated patch releases;
- a library version is not used as a substitute for application contract versioning.

## Content and Media Versioning

Published story versions are immutable. Corrections create a new content version rather than silently changing the meaning of an already published version.

Media metadata includes version or checksum information sufficient to invalidate stale caches and offline downloads.

Clients receive explicit signals when:

- a story version is superseded;
- an asset checksum changes;
- a download manifest is outdated;
- content is withdrawn or rolled back.

## Deprecation Policy

Every deprecated API, event, capability, or persisted format must include:

- owner;
- replacement;
- announcement date;
- deprecation reason;
- affected consumers;
- usage telemetry;
- support window;
- planned removal date;
- rollback plan if removal causes unexpected impact.

Removal occurs only after:

1. supported clients have a migration path;
2. usage falls below the approved threshold;
3. the support window ends;
4. contract tests for the old version are intentionally removed;
5. documentation and operational dashboards are updated.

## Compatibility Matrix

Release documentation should maintain a matrix similar to:

| Component | Version | Compatible dependencies |
|---|---|---|
| Mobile app | 1.4.x | API v1, manifest v1-v2 |
| Backend API | 2.3.x | DB schema 41-44, event v1-v2 |
| Worker | 2.3.x | event v1-v2, DB schema 41-44 |
| Admin dashboard | 1.8.x | Admin API v1 |

The exact ranges are generated or verified during release preparation.

## Contract Testing

CI must validate:

- OpenAPI compatibility against the previous supported contract;
- event-schema compatibility;
- old mobile request fixtures against the current backend;
- supported local-database upgrade paths;
- manifest parsing for supported client versions;
- database compatibility for rolling deployments;
- deprecation metadata completeness where required.

## Observability

Track:

- requests by API version;
- active mobile versions;
- blocked and recommended upgrades;
- event consumption by version;
- deprecated contract usage;
- manifest versions served;
- schema compatibility failures;
- unknown enum or field handling errors;
- forced-upgrade impact.

Version telemetry must avoid storing unnecessary child data.

## Consequences

### Positive

- Predictable compatibility rules.
- Safer mobile and backend evolution.
- Clear contract ownership and deprecation.
- Better rolling-deployment and rollback safety.
- Easier operational diagnosis.

### Negative

- Temporary maintenance of parallel versions.
- Additional contract testing and telemetry.
- More release metadata and governance.
- Risk of stale versions when removal discipline is weak.

## Rejected Alternatives

### No explicit versioning

Rejected because it creates accidental breaking changes and ambiguous incident diagnosis.

### Version every minor API change

Rejected because additive changes would create unnecessary fragmentation and maintenance cost.

### Header-only API versions

Rejected because path-based versions are more visible, easier to route, and simpler to document for this project.

### One shared version for all components

Rejected because mobile, backend, events, database, and content evolve independently and have different compatibility rules.

## Follow-up Actions

- Add API compatibility validation to CI.
- Add event-schema compatibility tests.
- Define mobile minimum-version and recommended-version endpoints.
- Add release metadata to health diagnostics.
- Create a compatibility matrix template for releases.
- Document deprecation thresholds before production launch.
