# External Integration Register

Version: 1.0.0  
Status: Active  
Owners: Architecture, Backend Engineering, Mobile Engineering, DevOps  
Last reviewed: 2026-07-15

## 1. Purpose

This document records the external systems used by KidsAudioBookPlatform and defines the minimum architectural, security, resilience, observability, and ownership requirements for every integration. It prevents undocumented vendor dependencies and inconsistent failure handling.

## 2. Integration Principles

1. Every external dependency has a business owner and technical owner.
2. Provider-specific models remain behind adapters.
3. Business state is not inferred from an unverified client response.
4. Timeouts, retries, idempotency, and circuit breaking are defined explicitly.
5. Provider outages must degrade predictably.
6. Credentials are managed through approved secret stores.
7. Personal and child-related data is minimized.
8. Webhooks are authenticated, deduplicated, persisted, and auditable.
9. Every provider has monitoring, reconciliation, and an exit strategy.
10. New integrations require architecture and privacy review.

## 3. Integration Register

| Integration | Purpose | Direction | Criticality | Authoritative state | Primary owner |
|---|---|---|---|---|---|
| Apple App Store | iOS subscriptions and purchase verification | Bidirectional | Critical | Verified provider transaction plus platform subscription model | Subscriptions |
| Google Play | Android subscriptions and purchase verification | Bidirectional | Critical | Verified provider transaction plus platform subscription model | Subscriptions |
| APNs | iOS push delivery | Outbound | Medium | Notification database | Notifications |
| Firebase Cloud Messaging | Android push delivery | Outbound | Medium | Notification database | Notifications |
| Email provider | Verification, recovery, account communication | Outbound | High | Identity and notification records | Identity / Notifications |
| Object storage | Media asset persistence | Bidirectional | Critical | Object storage for binaries, PostgreSQL for metadata | Media |
| CDN | Media and image delivery | Outbound delivery | High | Origin object storage and media metadata | Media / DevOps |
| Malware scanner | Uploaded-file safety validation | Bidirectional | High | Media validation state | Media / Security |
| Analytics platform | Privacy-safe product analytics | Outbound | Low | Internal transactional systems | Analytics |
| Crash reporting | Mobile and admin crash diagnostics | Outbound | Medium | Application operational telemetry | Mobile / Admin |
| Observability backends | Metrics, logs, and traces | Outbound | High | Source applications and infrastructure | DevOps |

Specific vendors may change without changing the contracts and controls described here.

## 4. Standard Adapter Boundary

External SDKs and schemas must not leak into domain code.

```text
Domain / Application
        ↓
Provider-neutral port
        ↓
Integration adapter
        ↓
External SDK or HTTP API
```

Each adapter owns:

- authentication with the provider;
- request and response mapping;
- timeout and retry policy;
- provider error classification;
- telemetry;
- idempotency and deduplication support;
- contract-version compatibility.

## 5. Required Integration Metadata

Every integration must document:

- provider and product name;
- business purpose;
- owner and escalation contact;
- data exchanged and classification;
- regions where data is processed or stored;
- authentication method;
- API or SDK version;
- request timeout;
- retry and backoff rules;
- idempotency behavior;
- rate limits and quotas;
- webhook verification method;
- degraded-mode behavior;
- reconciliation process;
- monitoring and alert thresholds;
- retention and deletion behavior;
- contractual or compliance constraints;
- replacement and exit plan.

## 6. Timeout and Retry Policy

Retries are allowed only for operations that are safe or protected by idempotency.

| Operation type | Retry behavior |
|---|---|
| Read-only request | Bounded retry with jitter for transient failures |
| Idempotent write | Bounded retry using stable idempotency key |
| Non-idempotent write | No automatic retry unless provider guarantees deduplication |
| Webhook processing | Persist first, then retry internal handling |
| Bulk asynchronous delivery | Retry through queue with dead-letter handling |

Timeouts must be lower than the caller's remaining deadline. Unbounded retries are prohibited.

## 7. Provider Error Classification

Adapters translate provider errors into stable internal categories:

- `INVALID_REQUEST`;
- `AUTHENTICATION_FAILED`;
- `AUTHORIZATION_FAILED`;
- `NOT_FOUND`;
- `CONFLICT_OR_DUPLICATE`;
- `RATE_LIMITED`;
- `TEMPORARILY_UNAVAILABLE`;
- `PERMANENT_REJECTION`;
- `UNKNOWN_PROVIDER_ERROR`.

Raw provider errors may be retained in restricted diagnostics but are not exposed directly to clients.

## 8. Webhook Security

Inbound webhooks must:

- use TLS;
- verify signatures or provider-issued credentials;
- validate timestamp and replay windows where supported;
- preserve the raw body only when required for signature verification;
- enforce size and content-type limits;
- persist provider event identifiers;
- deduplicate repeated delivery;
- acknowledge only after durable acceptance;
- process business effects asynchronously where practical;
- log privacy-safe verification outcomes;
- support replay from retained event records.

A successful HTTP response means the event was durably accepted, not necessarily fully processed.

## 9. Subscription Provider Rules

- Mobile purchase responses are never authoritative by themselves.
- Receipts or purchase tokens are verified server-side.
- Provider notifications and periodic reconciliation update subscription state.
- Duplicate transactions are protected by provider transaction identifiers and unique constraints.
- Entitlement is granted only after verification succeeds.
- Refunds, revocations, grace periods, billing retry, and expiry are modeled explicitly.
- Provider and internal state divergence creates an alert and reconciliation task.

## 10. Notification Provider Rules

- Business transactions do not wait for push or email delivery.
- Notifications are persisted before provider calls.
- Invalid device tokens are disabled.
- Provider acceptance is distinguished from user delivery or read state.
- Marketing preferences are checked separately from transactional eligibility.
- Template content uses approved variables and locale fallbacks.

## 11. Media and CDN Rules

- Buckets remain private unless an explicit public-content policy applies.
- Clients receive short-lived signed access or CDN authorization.
- Upload type, signature, size, checksum, dimensions, duration, and codec are validated.
- Malware or safety scanning completes before publication.
- Origin and CDN failures have documented fallback and user messaging.
- Cache invalidation uses immutable versioned asset keys whenever possible.

## 12. Data Protection

For every provider:

- send only required fields;
- avoid child names and unnecessary profile attributes;
- use pseudonymous identifiers where possible;
- prohibit secrets, refresh tokens, PINs, and payment credentials in telemetry;
- document subprocessors and processing regions;
- support deletion and retention obligations;
- encrypt data in transit and at rest where the provider supports it;
- review provider terms before expanding data usage.

## 13. Credential Management

- Credentials are stored in approved secret-management systems.
- Separate credentials are used per environment.
- Least privilege is required.
- Rotation procedures are documented and rehearsed.
- Secrets are never embedded in source code, mobile binaries, logs, or documentation.
- Provider access is removed promptly when no longer needed.

## 14. Resilience and Degraded Modes

| Dependency failure | Expected behavior |
|---|---|
| Subscription verification unavailable | Do not grant new entitlement; preserve verified existing state according to grace policy |
| Push provider unavailable | Persist and retry; in-app inbox remains available |
| Email provider unavailable | Queue retry; security-sensitive flows show clear status and support recovery |
| CDN degraded | Retry alternate edge/origin path if configured; never expose storage credentials |
| Object storage unavailable | Prevent new upload publication; retain metadata and retry processing |
| Analytics unavailable | Drop or buffer within limits; never block core journeys |
| Crash reporting unavailable | Application remains functional; local rate-limited diagnostics continue |

## 15. Reconciliation

Critical integrations require scheduled reconciliation:

- app-store transactions versus internal subscription state;
- notification delivery attempts versus provider responses;
- media metadata versus stored objects;
- object manifests versus checksums;
- device registrations versus invalid-token responses;
- webhook sequence or gap checks where supported.

Reconciliation jobs are idempotent, resumable, observable, and audited when they change business state.

## 16. Observability

Track per provider:

- request count and latency;
- success and error rates;
- timeout and retry count;
- circuit-breaker state;
- rate-limit responses and quota consumption;
- webhook verification and processing failures;
- queue depth and oldest pending delivery;
- reconciliation divergence;
- credential-expiry warnings;
- provider-specific business outcomes.

Metric labels must not include uncontrolled user, transaction, token, or URL values.

## 17. Provider Change Management

Before upgrading an API or SDK:

1. review release and security notes;
2. identify contract and permission changes;
3. update test doubles and contract tests;
4. validate sandbox behavior;
5. perform staged rollout;
6. monitor provider-specific metrics;
7. retain rollback compatibility where practical.

Deprecated provider versions must have an owner and migration deadline.

## 18. Exit Strategy

Each critical provider requires:

- exportable data and documented formats;
- provider-neutral domain contracts;
- an adapter replacement path;
- credential and DNS cutover steps where applicable;
- dual-run or shadow-validation capability for high-risk replacement;
- data deletion confirmation after termination;
- documented contractual notice periods and costs.

## 19. Onboarding Checklist

A new integration cannot reach production until:

- ownership is assigned;
- architecture, security, and privacy review is complete;
- credentials and environment separation are configured;
- timeouts, retries, idempotency, and quotas are defined;
- provider errors are mapped;
- contract and failure tests pass;
- dashboards and alerts exist;
- webhook replay and reconciliation are tested where relevant;
- data retention and deletion are documented;
- degraded behavior and support runbook are approved;
- exit strategy is recorded.

## 20. Review Cadence

- Critical providers: quarterly review.
- Other production providers: at least twice yearly.
- Immediate review after a severe outage, security event, major contract change, or vendor acquisition that changes risk.
