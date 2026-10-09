# Security Control Matrix

Version: 1.0.0  
Status: Active Draft  
Owners: Architecture, Security, Backend Engineering, Mobile Engineering  
Last updated: 2026-07-15

## 1. Purpose

This document maps the major security risks of KidsAudioBookPlatform to concrete preventive, detective, and corrective controls. It complements `Security_Architecture.md`, `07_Security_Trust_Boundaries.md`, the ADR set, and the implementation-specific security rules in backend, mobile, admin, data, and operations documentation.

The matrix is intended to support:

- architecture and pull-request reviews;
- threat modelling;
- implementation planning;
- security testing;
- incident response;
- audit preparation;
- future service extraction.

A control is not considered implemented merely because it appears in this document. Implementation requires code, configuration, tests, telemetry, ownership, and operational validation.

## 2. Security Objectives

The platform protects the following outcomes, in priority order:

1. child safety and privacy;
2. parent-account integrity;
3. subscription and entitlement correctness;
4. protection of premium media;
5. administrative accountability;
6. service availability;
7. trustworthy content publication;
8. recoverable and auditable operations.

## 3. Control Types

| Type | Purpose |
|---|---|
| Preventive | Stops or reduces the probability of an incident |
| Detective | Identifies suspicious, unsafe, or incorrect behavior |
| Corrective | Limits impact and restores safe operation |
| Compensating | Reduces risk when the preferred control is temporarily unavailable |

## 4. Identity and Session Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Credential stuffing | Password hashing with Argon2id, rate limiting, progressive backoff, generic login errors | Failed-login metrics, IP/device anomaly signals, authentication alerts | Temporary lock, forced reset, session revocation | Identity |
| Stolen access token | Short access-token lifetime, audience and issuer validation, secure client storage | Invalid-token metrics, unusual session activity | Session-family revocation, emergency deny list where justified | Identity |
| Stolen refresh token | Opaque refresh tokens, persisted hash only, rotation on every use, device binding | Refresh-token reuse detection | Revoke token family and require login | Identity |
| Disabled account remains active | Session-status validation for sensitive operations, short access-token lifetime | Requests from disabled accounts | Revoke all sessions and deny refresh | Identity |
| Session fixation | Server-generated session identifiers, token rotation after authentication state changes | Duplicate or inconsistent session identifiers | Invalidate affected sessions | Identity |
| Weak password recovery | Single-use expiring reset tokens, verified delivery channel, rate limiting | Reset-request spikes, repeated failures | Revoke reset tokens and sessions after recovery | Identity |

## 5. Parent Zone Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Child accesses parent capabilities | Separate parent elevation, PIN or local biometric verification, guarded routes | Failed PIN attempts, unexpected elevation frequency | Cooldown, revoke elevation, require account re-authentication | Identity / Mobile |
| Parent elevation reused too long | Short expiry, inactivity timeout, background grace limit | Elevation age and usage telemetry | Revoke elevation state | Identity |
| PIN disclosure | Argon2id hash only, never log or return PIN, secure input handling | Secret-scanning and log review | Reset PIN and revoke elevation sessions | Identity |
| Deep-link bypass | Server authorization for every protected action, route guards | Denied deep-link attempts | Block route and clear elevation state | Mobile / Backend |
| Sensitive action performed with stale elevation | Recent-authentication requirement for account deletion, billing changes, exports, PIN reset | Audit events include authentication age and method | Reject request and require re-authentication | Backend |

## 6. Authorization and Ownership Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Horizontal privilege escalation | Server-side ownership checks on account, profile, device, download, and notification resources | Repeated authorization failures by actor/resource | Revoke suspicious sessions, investigate account | Owning domain |
| Admin privilege escalation | Role and permission checks, least privilege, protected role-management flow | Audit all role and permission changes | Remove role, revoke sessions, incident review | Administration / Identity |
| Client-forged entitlement | Backend-authoritative entitlement evaluation | Mismatch between client claims and server state | Deny operation and refresh client state | Entitlements |
| Cross-module data access | Explicit module APIs, architecture tests, no repository access across boundaries | CI dependency checks | Block merge and refactor dependency | Architecture |
| Insecure direct object reference | Opaque identifiers plus ownership checks | Access-denied metrics by route and actor | Rate limit, revoke session where abuse is suspected | Backend |

## 7. API and Input Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Injection | Parameterized persistence, validation, safe query construction, no dynamic SQL from user input | WAF/application anomalies, validation-failure metrics | Block input, patch query path, rotate exposed credentials if needed | Backend |
| Mass assignment | Explicit request DTOs and allow-listed field mapping | Unexpected-field validation metrics | Reject request and patch mapper | Backend |
| Broken object validation | Bean validation plus domain validation | Structured `VAL_*` error metrics | Reject safely, add regression test | Backend |
| Oversized payload | Route-specific body limits, upload intents for media | 413 metrics and gateway alerts | Reject before business processing | Edge / Backend |
| Replay of write requests | Idempotency keys, operation identifiers, timestamps where appropriate | Duplicate-key and conflict metrics | Return original result or reject conflicting reuse | Backend |
| Unsafe error disclosure | Stable error catalog, generic external messages, correlation IDs | Log scanning and security tests | Remove disclosure, rotate exposed secret, incident review | Backend |

## 8. Media and File Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Malicious upload | Upload intent, size/type limits, signature validation, malware scanning, quarantine | Scan failures and suspicious file metrics | Delete/quarantine object and disable related workflow | Media |
| MIME spoofing | File-signature inspection and codec validation | Validation mismatch metrics | Reject upload | Media |
| Public exposure of premium content | Private buckets, signed short-lived URLs, entitlement checks | Unauthorized URL generation attempts, CDN access anomalies | Revoke URL policy, rotate signing keys, invalidate CDN cache | Media / Entitlements |
| Corrupted media | Checksums, immutable object versions, manifest validation | Checksum failures and playback errors | Remove corrupted rendition and regenerate | Media |
| Orphaned objects | Database-backed lifecycle state and cleanup jobs | Orphan-scan reports | Quarantine then delete under retention policy | Media / Operations |
| Unsafe derivative processing | Isolated workers, bounded resources, no implicit trust in source media | Worker failure and resource-saturation metrics | Quarantine asset and restart worker safely | Media / Operations |

## 9. Subscription and Billing Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Forged purchase proof | Provider-side verification, signed callback validation, idempotent processing | Verification failures and provider mismatch metrics | Reject proof and flag account for review when suspicious | Billing |
| Duplicate purchase processing | Provider transaction uniqueness and idempotency keys | Duplicate-transaction metrics | Return existing result, reconcile provider state | Billing |
| Stale premium access | Short entitlement cache TTL, revocation events, periodic reconciliation | Provider-versus-local state mismatch | Recompute entitlement and revoke offline access | Entitlements / Billing |
| Webhook spoofing | Signature verification, source controls where supported, replay protection | Invalid signature and timestamp metrics | Reject webhook and alert on sustained attacks | Billing |
| Manual override abuse | Restricted permission, mandatory reason, immutable audit | Override frequency and actor reports | Remove override and suspend permission | Administration |

## 10. Messaging and Background Processing Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Lost domain event | Transactional outbox | Outbox age and unpublished-row metrics | Replay publisher safely | Producing domain |
| Duplicate delivery | Globally unique event ID, consumer inbox/idempotency | Duplicate-consumption metrics | Ignore duplicate and preserve audit context | Consumer |
| Poison message | Schema validation, bounded retry, dead-letter routing | DLQ depth and failure classification | Fix cause, authorize replay, quarantine invalid messages | Consumer / Operations |
| Message tampering | Broker TLS, credentials, vhost permissions, controlled producers | Authentication and authorization failures | Revoke broker credential and investigate | Operations |
| Sensitive data in events | Event minimization, schema review, contract tests | Payload scanning and review | Remove field through versioned change and apply retention response | Producer |

## 11. Data Protection Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Excessive personal data collection | Purpose limitation, minimal schemas, privacy review | Data inventory review | Remove field and migrate/delete historical values | Data owners |
| Sensitive data in logs | Structured allow-listed fields, masking, no arbitrary bodies | Automated scanning and periodic review | Remove data, shorten retention, rotate secrets | All teams |
| Unauthorized database access | Least-privilege credentials, network controls, separate environments | Database audit and anomalous-query alerts | Revoke credential and investigate access | Operations |
| Backup exposure | Encryption, restricted storage, tested access process | Backup access logs | Revoke access, rotate encryption material where required | Operations |
| Incomplete deletion | Deletion workflow across owning contexts, tombstones, reconciliation | Deletion backlog and orphan reports | Replay deletion and escalate failed dependencies | Privacy / Data owners |
| Unsafe analytics | Pseudonymous identifiers, aggregation, no child-sensitive raw payloads | Analytics-schema review | Remove event/field and purge affected data | Analytics |

## 12. Mobile Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Token exposure | Platform secure storage, no tokens in logs or local content DB | Mobile security tests and crash-log review | Revoke session and patch storage path | Mobile / Identity |
| Local database extraction | Minimize sensitive data, platform protection, encrypted storage where justified | Device-risk telemetry where lawful | Revoke offline data and require re-authentication | Mobile |
| Offline entitlement bypass | Signed manifest, expiry, server reconciliation, limited grace | Offline-use anomalies and stale-manifest metrics | Revoke package and clear access | Mobile / Entitlements |
| Tampered client | Server-authoritative security decisions, optional integrity signals as risk input only | Integrity-failure metrics | Step-up authentication or deny sensitive operation | Backend / Mobile |
| Unsafe deep links | Allow-listed routes, authenticated resolution, no embedded secrets | Invalid-link metrics | Reject and clear navigation state | Mobile |

## 13. Administrative Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Unauthorized publication | Permission checks, workflow state validation, dual approval where configured | Publication audit and anomaly reports | Unpublish/rollback version and suspend permission | Catalog / Administration |
| Account support abuse | Least privilege, masked data, reason required, no password/PIN visibility | Support-action audit review | Revoke role and investigate | Administration |
| Bulk-operation damage | Preview, bounded batch size, explicit confirmation, idempotent job | Job progress and unusual-volume alerts | Pause job and restore from authoritative state | Administration |
| Audit deletion or modification | Append-only records and restricted DB permissions | Integrity checks | Restore from backup/export and investigate | Audit / Operations |

## 14. Infrastructure and Deployment Controls

| Risk | Preventive controls | Detective controls | Corrective controls | Owner |
|---|---|---|---|---|
| Secret committed to repository | Secret scanning, environment injection, no credentials in examples | CI scanning | Revoke and rotate immediately | All teams |
| Vulnerable dependency | Dependency scanning, supported versions, controlled upgrades | CI alerts and vulnerability feed | Patch, mitigate, or disable affected component | Engineering |
| Unsafe deployment | Protected branch, CI gates, immutable artifact, migration validation | Deployment health checks | Roll back application or apply corrective migration | DevOps |
| Environment crossover | Separate credentials, buckets, databases, queues, and namespaces | Resource-tag and traffic review | Revoke credentials and isolate environment | DevOps |
| Excessive container privilege | Non-root runtime, minimal images, read-only filesystem where practical | Runtime policy alerts | Stop workload and redeploy securely | DevOps |

## 15. Security Verification Requirements

Every security-sensitive change must include the relevant subset of:

- unit tests for authorization and domain rules;
- integration tests using real security configuration;
- negative API tests;
- contract tests for error behavior;
- dependency and secret scanning;
- architecture tests for module boundaries;
- mobile secure-storage tests;
- upload-validation tests;
- event-schema tests;
- audit-record assertions;
- incident and rollback considerations.

Critical flows requiring explicit security test coverage include:

- login and token refresh;
- refresh-token reuse;
- Parent Zone elevation;
- profile ownership;
- subscription verification;
- offline-download authorization;
- signed media access;
- content publication;
- account deletion and export;
- administrator role changes.

## 16. Security Telemetry Minimums

The platform must expose actionable metrics for:

- authentication failures and lockouts;
- refresh-token reuse;
- authorization denials;
- Parent Zone failures and cooldowns;
- invalid webhook signatures;
- purchase-verification failures;
- rejected uploads and malware detections;
- signed-URL authorization failures;
- DLQ growth;
- administrative privilege changes;
- data-export and deletion failures.

Metrics must not contain uncontrolled account IDs, profile IDs, emails, tokens, filenames, or other high-cardinality sensitive values as labels.

## 17. Exception Process

A security control may be deferred only when all of the following are documented:

1. affected risk;
2. reason the preferred control cannot yet be implemented;
3. compensating control;
4. accountable owner;
5. expiry date;
6. monitoring requirement;
7. remediation plan.

Material exceptions require an ADR or formally tracked security decision. Expired exceptions block release until renewed or resolved.

## 18. Review Checklist

- Is the security principal clear?
- Is resource ownership validated server-side?
- Are entitlement decisions server-authoritative?
- Are secrets and personal data excluded from telemetry?
- Are retries and idempotency safe?
- Is every sensitive action auditable?
- Is failure behavior fail-safe?
- Can credentials or sessions be revoked?
- Is the control covered by tests?
- Does an operational owner receive actionable alerts?

## 19. Related Documents

- `Security_Architecture.md`
- `C4_Model/07_Security_Trust_Boundaries.md`
- `C4_Model/09_Data_Ownership_Matrix.md`
- `C4_Model/11_Integration_Contract_Map.md`
- `Error_Catalog.md`
- `Event_Catalog.md`
- `Logging_Monitoring.md`
- `Database_Design.md`
- `ADR/ADR-0005-jwt-refresh-token-strategy.md`
- `ADR/ADR-0006-parent-zone-security.md`

## 20. Ownership and Maintenance

Architecture and Security own this matrix. Every team owns implementation and verification of controls inside its bounded context. The matrix must be reviewed when authentication, authorization, payments, media access, data retention, administrative permissions, infrastructure boundaries, or external integrations change.