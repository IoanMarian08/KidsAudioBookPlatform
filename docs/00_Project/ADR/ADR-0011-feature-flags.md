# ADR-0011: Feature Flags

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture and Product Engineering
- Last reviewed: 2026-07-15

## 1. Context

KidsAudioBookPlatform will release capabilities gradually across the backend, Flutter mobile application, and administrative dashboard. Some capabilities require controlled rollout, rapid rollback, limited audience exposure, staged migration, or operational disablement without waiting for a full application release.

Examples include:

- advertisements for free users;
- premium trials and subscription offers;
- recommendation algorithms;
- new playback behavior;
- offline synchronization changes;
- notification campaigns;
- moderation and administrative tools;
- provider migrations;
- emergency disablement of unstable integrations.

A feature-flag mechanism is therefore required, but it must not become a hidden configuration system, a replacement for authorization, or a permanent source of conditional complexity.

## 2. Decision

Introduce a centralized feature-flag capability with **server-side evaluation as the authoritative source of truth**.

The backend owns:

- flag definitions;
- targeting rules;
- environment-specific values;
- security-sensitive evaluation;
- audit history;
- rollout state;
- flag lifecycle and expiration.

Mobile and administrative clients may receive already evaluated flags or non-sensitive configuration, but they must never independently grant access to premium, administrative, security-sensitive, or child-restricted capabilities.

The initial implementation may be built inside the modular monolith. A dedicated external feature-management platform is not required for the MVP and may be introduced later through a compatible adapter if operational needs justify it.

## 3. Decision Scope

This ADR applies to:

- backend release control;
- mobile feature exposure;
- administrative dashboard exposure;
- experiments;
- operational kill switches;
- staged provider migrations;
- temporary compatibility behavior.

This ADR does not authorize flags to replace:

- authentication;
- role-based authorization;
- subscription entitlement checks;
- child-profile age restrictions;
- content publication state;
- legal or privacy controls;
- durable product settings.

## 4. Flag Categories

### 4.1 Release flags

Temporary flags used to separate code deployment from user exposure.

Examples:

- `mobile.new_player_enabled`;
- `catalog.new_search_enabled`;
- `admin.bulk_publish_enabled`.

Release flags must be removed after rollout completion.

### 4.2 Operational flags

Kill switches used to disable a risky or failing capability quickly.

Examples:

- `ads.delivery_enabled`;
- `notifications.push_enabled`;
- `downloads.authorization_enabled`.

Operational flags must default to the safest degraded behavior.

### 4.3 Experiment flags

Flags used for controlled product experiments.

Examples:

- alternative home-page ordering;
- alternative premium upsell presentation;
- recommendation-ranking variants.

Experiments must not expose children to unsafe content, use sensitive child profiling, or bypass privacy rules.

### 4.4 Migration flags

Temporary flags used during data, provider, API, or algorithm migration.

Examples:

- dual-write activation;
- read-from-new-store activation;
- provider cutover;
- schema compatibility path.

Migration flags require explicit rollback and removal plans.

### 4.5 Permission-supporting flags

Flags may hide or expose an already authorized internal capability, but they may not grant permission by themselves.

A user must pass both:

1. authorization policy;
2. feature-flag evaluation.

## 5. Naming Convention

Flag keys use lowercase dot notation:

```text
<domain>.<capability>.<purpose>
```

Examples:

```text
playback.new_engine.enabled
subscriptions.trial_offer.enabled
admin.story_bulk_edit.enabled
notifications.email_delivery.enabled
```

Rules:

- keys are stable and never silently reused;
- names describe capability and intent;
- environment names are not embedded in the key;
- negative or ambiguous naming is avoided;
- renamed flags are treated as new flags with a migration plan.

## 6. Required Metadata

Every flag must define:

- stable key;
- human-readable description;
- category;
- owner;
- creation date;
- default value;
- safe fallback value;
- environment;
- targeting dimensions;
- rollout strategy;
- expected removal date;
- linked issue, roadmap item, or ADR;
- monitoring expectations;
- rollback instructions.

A flag without an owner or expiration policy must not be introduced.

## 7. Evaluation Model

### 7.1 Server-side authority

The backend evaluates flags for:

- security-sensitive behavior;
- premium or free-tier access;
- administrative capabilities;
- child safety restrictions;
- provider selection;
- data migration behavior;
- write-path changes.

### 7.2 Client-visible evaluation

The backend may return evaluated client flags for presentation or optional behavior.

Example response:

```json
{
  "version": "2026-07-15T18:00:00Z",
  "flags": {
    "mobile.new_player.enabled": true,
    "subscriptions.trial_offer.enabled": false
  },
  "expiresAt": "2026-07-15T18:05:00Z"
}
```

Clients must:

- treat unknown flags as disabled;
- use documented fallback behavior;
- never infer authorization from UI visibility;
- refresh evaluated flags after authentication or profile changes;
- tolerate stale non-sensitive values for a bounded period;
- avoid logging the complete targeting context.

### 7.3 Evaluation context

Permitted targeting dimensions include:

- environment;
- account identifier;
- child-profile identifier where privacy-safe;
- device identifier;
- app version;
- platform;
- locale;
- country or region where legally required;
- internal role;
- deterministic percentage cohort.

Sensitive personal data must not be copied into flag definitions or analytics labels.

## 8. Deterministic Rollout

Percentage rollouts use stable deterministic hashing over a documented subject identifier and flag key.

Requirements:

- the same subject remains in the same cohort;
- changing percentage expands or contracts predictably;
- the hashing strategy is versioned;
- anonymous and authenticated subjects use separate documented keys;
- child-profile targeting is used only when the experience genuinely requires profile-level consistency.

Random evaluation per request is forbidden because it creates unstable behavior and invalid experiment data.

## 9. Safe Defaults and Failure Behavior

If flag evaluation fails:

- premium access is not granted;
- administrative capabilities remain unavailable;
- unsafe or experimental child experiences remain disabled;
- core playback should continue where the flag controls only an optional dependency;
- operational kill switches use the safest predefined fallback;
- the failure is observable through metrics and structured logs.

Examples:

| Capability | Safe fallback |
|---|---|
| New recommendation algorithm | Use editorial recommendations |
| Advertising provider | Skip the ad and continue playback |
| New payment verification path | Use established verification path or keep purchase pending |
| New admin bulk operation | Disable the action |
| New playback engine | Use stable player implementation |

## 10. Persistence and Data Model

A flag definition contains at minimum:

- `key`;
- `description`;
- `category`;
- `enabled`;
- `default_value`;
- `rules`;
- `environment`;
- `owner`;
- `created_at`;
- `updated_at`;
- `expires_at`;
- `version`.

Flag changes are versioned. The current value may be stored in PostgreSQL, while Redis may cache evaluated or compiled rules.

Redis is not the source of truth.

## 11. Caching and Propagation

Evaluated values may be cached briefly.

Rules:

- cache keys are environment- and context-aware;
- security-sensitive evaluations use short TTLs;
- operational kill switches require near-immediate invalidation;
- stale values are bounded by documented maximum age;
- cache failure falls back to authoritative storage or safe defaults;
- clients may retain only the last valid non-sensitive configuration;
- flag updates must not require application restart.

The platform should support explicit cache invalidation after a flag change.

## 12. Audit and Change Control

Every flag mutation records:

- actor;
- timestamp;
- old value;
- new value;
- targeting-rule change;
- reason;
- environment;
- correlation identifier.

High-risk changes require stronger controls, such as:

- confirmation dialog;
- production-only permission;
- two-person review for critical kill switches or migrations;
- linked incident or change request.

Flag mutation APIs are administrative and must be protected by dedicated permissions.

## 13. Observability

The platform records:

- evaluation count by flag and result;
- evaluation failures;
- fallback usage;
- stale-cache usage;
- flag-change events;
- percentage exposure;
- experiment allocation anomalies;
- expired flags still evaluated;
- operational kill-switch activations.

Metrics must avoid high-cardinality account or profile identifiers.

Logs include the flag key, result, environment, evaluation source, and correlation ID, but not sensitive targeting attributes.

## 14. Testing Requirements

Each flag-controlled capability requires tests for:

- flag enabled;
- flag disabled;
- evaluation unavailable;
- missing flag;
- stale client configuration;
- authorization denied while flag is enabled;
- deterministic targeting;
- rollout boundary values;
- removal of the obsolete branch.

Contract tests validate the client-visible flag response.

Critical flags require integration tests proving the safe fallback.

## 15. Mobile and Admin Rules

### Mobile

- flags influence presentation and optional behavior only after backend evaluation;
- cached values must expire;
- unsupported app versions ignore unknown flags safely;
- a hidden premium control does not replace entitlement validation;
- profile changes trigger reevaluation where profile context matters.

### Admin dashboard

- UI visibility never replaces backend authorization;
- production flag changes require explicit confirmation;
- dangerous flags display impact and rollback information;
- change history is visible to authorized operators.

## 16. Lifecycle and Removal Policy

The lifecycle is:

```text
PROPOSED -> ACTIVE -> ROLLING_OUT -> FULLY_ENABLED -> REMOVAL_DUE -> REMOVED
```

Operational flags may remain long-lived only when they are genuine permanent kill switches and have documented ownership.

Release, experiment, and migration flags must have removal dates.

A rollout is complete only when:

1. the target state is stable;
2. metrics confirm expected behavior;
3. rollback is no longer required;
4. obsolete code paths are removed;
5. tests are simplified;
6. the flag definition is deleted;
7. documentation is updated.

Expired flags are reported by CI or scheduled governance checks.

## 17. Alternatives Considered

### Compile-time-only switches

Rejected because they cannot support rapid production rollback and depend on new application releases.

### Client-only remote configuration

Rejected because client state cannot be trusted for security, entitlement, or administrative decisions.

### Environment variables for all flags

Rejected because environment variables are suitable for deployment configuration but not dynamic targeting, percentage rollout, or audited runtime changes.

### Permanent configuration through flags

Rejected because it creates hidden product rules and long-lived conditional complexity. Stable product settings belong in explicit configuration or domain models.

### External feature-management platform from day one

Deferred because it adds cost, vendor dependency, and operational complexity before the MVP demonstrates the need. The internal abstraction must allow later replacement.

## 18. Consequences

### Positive

- safer rollout and rollback;
- reduced dependency on app-store release timing;
- controlled experiments;
- faster incident mitigation;
- safer provider and data migrations;
- consistent backend authority;
- auditable production changes.

### Negative

- additional conditional complexity;
- risk of stale flags and dead branches;
- additional persistence, caching, testing, and monitoring requirements;
- operational responsibility for production changes;
- possibility of inconsistent behavior when flags are poorly scoped.

## 19. Follow-up Actions

- define the feature-flag module boundary;
- define flag-management permissions;
- add database migrations for flag definitions and audit history;
- add Redis cache and invalidation strategy;
- define the client evaluation endpoint;
- add CI checks for expired flags;
- add dashboards for evaluation errors and stale flags;
- document the first production flags in the implementation roadmap.

## 20. Compliance Criteria

A feature flag is compliant with this ADR only when:

- it has an owner and expiration policy;
- the backend remains authoritative;
- safe fallback behavior is documented;
- authorization is enforced independently;
- changes are audited;
- tests cover enabled, disabled, and failure states;
- observability exists;
- removal work is tracked.
