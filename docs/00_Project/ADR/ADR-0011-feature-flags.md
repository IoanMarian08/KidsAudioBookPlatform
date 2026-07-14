# ADR-0011: Feature Flags

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture and Product Engineering

## Context

The platform will release features gradually across backend, mobile, and admin surfaces. Some capabilities, including advertisements, premium trials, recommendation experiments, new playback behavior, and moderation tools, may require controlled rollout or emergency disablement without a full application release.

## Decision

Introduce a centralized feature-flag capability with server-side evaluation as the source of truth. Mobile and admin clients may receive evaluated flags and configuration, but they must not independently decide entitlement or security-sensitive behavior.

## Flag Categories

- Release flags for incomplete features.
- Operational flags for emergency disablement.
- Experiment flags for controlled product tests.
- Permission flags for internal or administrator-only features.

## Rules

1. Every flag has an owner, purpose, creation date, default value, rollout scope, and removal date.
2. Flags default to the safest behavior when evaluation fails.
3. Security and subscription enforcement remain backend responsibilities.
4. Long-lived configuration is not stored as a temporary feature flag.
5. Flags must be evaluated consistently by account, device, child profile, app version, country, or percentage cohort where applicable.
6. Flag changes must be audited.

## Data Model

A feature flag contains a stable key, description, state, targeting rules, fallback value, environment, owner, created date, and expiry date. Evaluation responses should include only flags relevant to the requesting client.

## Caching

Evaluated values may be cached briefly. Operational kill switches require short cache lifetimes or explicit invalidation. Mobile clients may retain the last valid non-sensitive configuration for degraded offline behavior.

## Consequences

### Positive

- Safer rollout and rollback.
- Reduced dependency on app-store release timing.
- Controlled experiments.
- Faster incident mitigation.

### Negative

- Conditional complexity in code.
- Risk of stale flags and dead branches.
- Additional observability and governance requirements.

## Rejected Alternatives

- Compile-time-only switches: too slow for operational response.
- Client-only remote configuration: unsuitable for security and entitlement decisions.
- Permanent configuration through flags: creates unmaintainable hidden behavior.

## Removal Policy

A completed rollout must result in removal of both the flag and the obsolete branch. Expired flags are reported in CI or scheduled governance checks.