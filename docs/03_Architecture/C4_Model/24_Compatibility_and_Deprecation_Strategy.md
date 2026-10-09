# Compatibility and Deprecation Strategy

Version: 1.0.0  
Status: Active Draft  
Owners: Architecture, Backend Engineering, Mobile Engineering, Product  
Last reviewed: 2026-07-15

## 1. Purpose

This document defines how KidsAudioBookPlatform evolves APIs, events, database schemas, mobile clients, administrative interfaces, configuration, and external integrations without causing uncontrolled breaking changes.

The platform must support clients and components that do not upgrade at the same time. Compatibility is therefore a deliberate architectural responsibility, not an implementation detail.

## 2. Scope

This strategy applies to:

- public mobile APIs;
- administrative APIs;
- internal module contracts;
- asynchronous event contracts;
- provider webhooks;
- database schemas and migrations;
- cached value formats;
- offline synchronization payloads;
- mobile local-database schemas;
- feature flags and configuration keys;
- notification templates and deep links;
- object-storage manifests;
- external SDK and provider versions.

## 3. Compatibility principles

1. Additive changes are preferred over destructive changes.
2. Producers evolve before consumers depend on new data.
3. Consumers tolerate unknown optional fields.
4. Existing fields never silently change meaning.
5. Removal requires telemetry, ownership, notice, and a migration path.
6. Mobile compatibility windows are longer than backend deployment windows.
7. Security-critical incompatibilities may require accelerated retirement.
8. Database and application rollback must remain possible during the approved deployment window.
9. Compatibility decisions must be testable.
10. Temporary parallel versions must have a removal deadline.

## 4. Change classification

| Change type | Classification |
|---|---|
| Add optional response field | Backward compatible |
| Add optional request field with default behavior | Backward compatible |
| Add endpoint | Backward compatible |
| Add event field ignored by old consumers | Backward compatible |
| Add enum value consumed by tolerant clients | Conditionally compatible |
| Rename or remove field | Breaking |
| Change field type | Breaking |
| Change validation to reject previously accepted input | Potentially breaking |
| Change default behavior | Potentially breaking |
| Change authorization semantics | Breaking unless explicitly coordinated |
| Change event meaning while keeping the same version | Prohibited |

Potentially breaking changes require explicit compatibility analysis.

## 5. HTTP API compatibility

Public APIs use path-based major versions such as `/api/v1`.

Within one major version:

- new fields are optional for clients;
- clients must ignore unknown response fields;
- existing required request fields are not added;
- response fields are not removed or renamed;
- field meaning and units remain stable;
- error codes are additive and documented;
- pagination ordering remains deterministic;
- idempotency semantics remain stable;
- authorization requirements may only become stricter through a coordinated security change.

A new major path version is required for intentionally incompatible contracts.

## 6. Request evolution

New request capabilities should use optional fields with explicit defaults.

Example:

```json
{
  "storyId": "uuid",
  "startPositionSeconds": 120,
  "playbackMode": "NORMAL"
}
```

An older client that omits `playbackMode` receives documented default behavior.

Do not repurpose an existing field or interpret absence differently without versioning.

## 7. Response evolution

Response changes must be additive. Clients must not depend on field order.

When an enum may expand, clients should implement an `UNKNOWN` or safe fallback state. A new value must not cause a child-facing screen to crash or expose an unsafe action.

## 8. Error compatibility

Error envelopes keep a stable structure:

```json
{
  "code": "SUBSCRIPTION_REQUIRED",
  "message": "Premium access is required.",
  "correlationId": "uuid",
  "details": {}
}
```

Rules:

- machine-readable codes remain stable;
- user-facing text may change and must not drive client logic;
- new codes are documented before release;
- clients implement a safe generic fallback;
- security-sensitive details are not exposed;
- HTTP status changes require compatibility review.

## 9. Event compatibility

Every event includes an explicit `eventVersion`.

Compatible changes within a version may add optional fields. Breaking changes require a new version or a new event type.

Consumers must:

- ignore unknown optional fields;
- validate required fields;
- reject unsupported major event versions safely;
- remain idempotent;
- record unsupported-event metrics;
- route poison messages according to dead-letter policy.

Dual publishing may be used during migrations, but it must be time-bounded and observable.

## 10. Database compatibility

Schema changes follow expand-and-contract:

1. introduce additive schema;
2. deploy code compatible with old and new representations;
3. backfill safely;
4. switch readers and writers;
5. verify telemetry;
6. remove obsolete schema in a later release.

Application releases must document the schema versions they support. Destructive migrations must never be coupled to the first release that stops using the old structure.

## 11. Cache compatibility

Cached values include a schema or key version. Incompatible changes use a new key namespace.

Example:

```text
prod:catalog:story:<id>:v3
```

Deployments must tolerate old cached entries until expiration or explicitly invalidate them after the authoritative transaction succeeds.

## 12. Mobile compatibility model

The backend publishes:

- minimum supported app version;
- recommended app version;
- current API capabilities;
- platform-specific upgrade information;
- maintenance or forced-upgrade reason where applicable.

Forced upgrades are reserved for:

- security vulnerabilities;
- provider or store incompatibility;
- data corruption risk;
- legal requirements;
- backend contracts that cannot safely support the old client.

Feature flags and capability negotiation are preferred over routine forced upgrades.

## 13. Offline synchronization compatibility

Offline operations include operation type and schema version. The server must understand operations generated during the supported offline window.

When an operation becomes obsolete:

- the server returns a structured migration or rejection result;
- the client preserves user intent where possible;
- rejected operations remain diagnosable;
- destructive local migration requires explicit UX and telemetry.

Download manifests and locally persisted content include format versions and checksums.

## 14. Mobile local-database migrations

Local migrations must be deterministic and tested across supported upgrade paths.

Rules:

- do not delete pending offline operations during normal migration;
- preserve downloaded-content references when formats remain compatible;
- use transactional migration where supported;
- maintain recovery behavior for interrupted migration;
- record migration outcome without logging child-sensitive data;
- provide a safe cache-reset path distinct from account-data deletion.

## 15. Provider webhook compatibility

Webhook endpoints accept supported provider versions explicitly. Raw payloads may be retained securely for a limited period when required for reconciliation and audit.

Provider SDK upgrades must validate:

- signature verification;
- event-type mapping;
- duplicate handling;
- out-of-order delivery;
- unknown fields;
- retry behavior;
- reconciliation against provider state.

## 16. Configuration compatibility

Configuration keys follow additive migration:

1. introduce the new key with fallback to the old key;
2. deploy all consumers;
3. update environments and secrets;
4. verify usage telemetry;
5. remove fallback in a later release;
6. delete the obsolete key.

Changing units, value meanings, or defaults under the same key is prohibited.

## 17. Deep-link compatibility

Deep links are versioned and validated. Unsupported or expired links route to a safe destination rather than failing or bypassing Parent Zone restrictions.

Links must not encode secrets, raw tokens, child names, or unrestricted administrative actions.

## 18. Deprecation lifecycle

Every deprecation records:

- contract or capability;
- owner;
- announcement date;
- replacement;
- migration guide;
- telemetry source;
- minimum support window;
- target removal date;
- security and business impact;
- rollback plan.

Lifecycle:

```text
ACTIVE -> DEPRECATED -> MIGRATION_REQUIRED -> DISABLED -> REMOVED
```

A contract cannot move to `REMOVED` until the approved exit criteria are met.

## 19. Default support windows

| Contract | Default minimum window |
|---|---|
| Public mobile API major version | At least two supported app-release cycles and usage review |
| Admin API | One coordinated admin deployment cycle |
| Event version | Until all registered consumers migrate and telemetry confirms zero use |
| Configuration key | Two production releases after full migration |
| Database column/table | At least one compatible application rollback window |
| Deep link | Defined by campaign and supported app versions |

These are defaults, not guarantees. Product, security, and store constraints may require longer or shorter windows with approval.

## 20. Usage telemetry

Before removal, measure:

- requests by API version and app version;
- event consumption by consumer and version;
- deprecated field usage where observable;
- unsupported-operation counts;
- old configuration-key reads;
- provider webhook versions;
- forced-upgrade exposure;
- failed migrations and fallback use.

Telemetry must avoid personal and child-sensitive data.

## 21. Contract testing

CI must validate:

- OpenAPI backward compatibility;
- event schema compatibility;
- serialization of old and new payloads;
- database migration from supported previous versions;
- mobile parsing of additive fields and enum values;
- offline operation replay from supported app versions;
- provider webhook fixtures;
- configuration fallback behavior.

Breaking changes require explicit approval and a new contract version where applicable.

## 22. Removal gates

A deprecated contract may be removed only when:

- the replacement is production-ready;
- documentation and migration tooling exist;
- usage is below the approved threshold or zero;
- dependent owners confirm migration;
- support windows have elapsed;
- rollback implications are understood;
- alerts and dashboards are updated;
- data retention obligations are preserved.

## 23. Emergency incompatibility

A security or data-integrity incident may require accelerated disablement. The incident commander must document:

- affected versions;
- reason for incompatibility;
- mitigation and customer impact;
- communication plan;
- forced-upgrade or feature-disable strategy;
- recovery criteria;
- follow-up architecture actions.

## 24. Ownership

Contract producers own compatibility and deprecation. Consumers are responsible for migrating within the published window and reporting blockers early.

Architecture maintains the compatibility policy, while Product owns user communication for visible changes.

## 25. Definition of done

A contract change is complete only when:

- compatibility classification is documented;
- schemas and specifications are updated;
- automated compatibility tests pass;
- telemetry is available;
- migration and rollback paths are understood;
- affected owners are identified;
- deprecation dates exist for temporary parallel versions.
