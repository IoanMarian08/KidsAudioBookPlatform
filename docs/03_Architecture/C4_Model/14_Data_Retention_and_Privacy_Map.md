# Data Retention and Privacy Map

Version: 1.0.0  
Status: Active Draft  
Owners: Architecture, Privacy, Security, Backend Engineering, Data Owners  
Last updated: 2026-07-15

## 1. Purpose

This document maps the major data categories in KidsAudioBookPlatform to their owning bounded context, purpose, sensitivity, storage location, retention posture, deletion behavior, access model, and audit requirements.

It supports privacy-by-design, account deletion, data export, incident response, backup policy, analytics governance, and future regulatory review. It does not replace legal advice or an approved jurisdiction-specific retention schedule. Exact production retention periods must be approved before launch and configured through documented policy.

## 2. Privacy Principles

1. Collect only data required for a documented product, security, billing, support, or legal purpose.
2. Child-related data receives the highest privacy protection.
3. Parent accounts are the primary authenticated identities; child profiles are subordinate product profiles, not independent unrestricted accounts.
4. Data ownership remains explicit by bounded context.
5. Operational logs, audit records, analytics data, and business records have different purposes and retention rules.
6. Deletion is a workflow across systems, not a single database statement.
7. Backups are not used as active application data and expire through the backup lifecycle.
8. Data exports must be authenticated, auditable, bounded, and delivered securely.
9. Sensitive data must not be copied into lower environments.
10. Retention exceptions require a documented reason, owner, and expiry or legal basis.

## 3. Sensitivity Classes

| Class | Description | Examples |
|---|---|---|
| Public | Intended for public distribution | published story titles, public cover images |
| Internal | Operational information with low privacy impact | service configuration identifiers, aggregate metrics |
| Confidential | Account or business information requiring controlled access | email, subscription state, support records |
| Restricted | High-impact security, child, credential, or payment-related data | refresh-token hashes, PIN hashes, child profile data, purchase proofs |

Restricted data requires explicit access control, encryption in transit, protected storage, audit where appropriate, and strict telemetry minimization.

## 4. Data Ownership Rules

- Every authoritative data set has one owning bounded context.
- Other contexts access data through APIs, events, read models, or approved exports.
- Cross-context copies must document purpose, freshness, retention, and deletion propagation.
- Analytics copies are non-authoritative and must use minimized or pseudonymous identifiers.
- Object storage owns binary assets; PostgreSQL owns asset metadata and lifecycle state.
- Redis never becomes the sole authoritative store for retained business information.

## 5. Identity and Account Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Account ID | Identity | Confidential | Stable account reference | PostgreSQL | Account lifetime plus approved tombstone period | Remove or pseudonymize according to deletion workflow |
| Email address | Identity | Confidential | Login, verification, recovery, communication | PostgreSQL | Account lifetime and approved legal/security period | Delete or irreversibly pseudonymize unless retention is required |
| Password hash | Identity | Restricted | Authentication | PostgreSQL | While credential is active | Delete with account or credential replacement |
| Email verification token hash | Identity | Restricted | Verify ownership | PostgreSQL/ephemeral store | Short expiry | Delete after use or expiry |
| Password reset token hash | Identity | Restricted | Account recovery | PostgreSQL/ephemeral store | Short expiry | Delete after use or expiry |
| Account status | Identity | Confidential | Security and lifecycle enforcement | PostgreSQL | Account lifetime; limited tombstone after deletion | Convert to deleted/tombstoned state as required |
| Locale and timezone | Identity | Confidential | Communication and display | PostgreSQL | Account lifetime | Delete with account |

Plaintext passwords, PINs, reset tokens, and verification tokens must never be retained.

## 6. Session and Device Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Refresh-token hash | Identity | Restricted | Session renewal and revocation | PostgreSQL | Until expiry/revocation plus short security review period | Delete through session cleanup |
| Token family ID | Identity | Restricted | Reuse detection | PostgreSQL | Session-family lifetime plus approved security window | Delete after retention window |
| Device ID hash | Identity | Confidential | Device session management | PostgreSQL | Active device lifetime plus limited history | Delete or pseudonymize with account |
| Device metadata | Identity | Confidential | Session visibility and risk analysis | PostgreSQL | Active session/device lifetime | Delete with account/session cleanup |
| Login IP/risk metadata | Identity/Security | Restricted | Fraud and security investigation | Security store/audit | Short, explicitly approved security period | Expire automatically |
| Parent elevation state | Identity | Restricted | Temporary Parent Zone authorization | Redis or server session store | Minutes | Expire automatically; revoke on logout/security event |

Device identifiers used in metrics should be non-reversible and must not become uncontrolled metric labels.

## 7. Child Profile Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Profile ID | Profiles | Restricted | Stable child-profile reference | PostgreSQL | Profile lifetime plus deletion workflow | Delete or tombstone until downstream cleanup completes |
| Display name or nickname | Profiles | Restricted | Child experience personalization | PostgreSQL/local device | Profile lifetime | Delete with profile |
| Age band | Profiles | Restricted | Content suitability and recommendations | PostgreSQL | Profile lifetime | Delete with profile |
| Avatar selection | Profiles | Confidential | Personalization | PostgreSQL/local device | Profile lifetime | Delete with profile |
| Language preferences | Profiles | Confidential | Content and UI localization | PostgreSQL | Profile lifetime | Delete with profile |
| Accessibility preferences | Profiles | Restricted | Accessible experience | PostgreSQL/local device | Profile lifetime | Delete with profile |
| Parental settings | Profiles | Restricted | Safety and product controls | PostgreSQL | Profile/account lifetime | Delete with profile/account |

Exact birth dates should not be collected unless a documented requirement and privacy review justify them. Prefer age bands where sufficient.

## 8. Playback and Listening Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Playback progress | Listening | Restricted | Resume and synchronization | PostgreSQL/local device | While profile exists; optional limited history | Delete with profile |
| Listening history | Listening | Restricted | User experience and parent-visible history | PostgreSQL | Product-defined period or profile lifetime | Delete with profile/account |
| Favorites | Listening | Restricted | Personalization | PostgreSQL/local device | Profile lifetime | Delete with profile |
| Completion state | Listening | Restricted | Progress and recommendations | PostgreSQL | Profile lifetime | Delete with profile |
| Session event ID | Listening | Confidential | Idempotency and diagnostics | PostgreSQL/event store where approved | Limited operational period | Expire/pseudonymize |
| Raw fine-grained telemetry | Analytics | Restricted | Product diagnostics only when necessary | Analytics platform | Shortest practical approved period | Aggregate then delete raw records |

Listening data must not be exposed to unrelated administrators or used for unrestricted marketing profiling.

## 9. Catalog and Editorial Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Story metadata | Catalog | Public/Internal | Discovery and publication | PostgreSQL | Retain while content is active plus editorial history | Archive or delete according to rights/policy |
| Draft content metadata | Catalog | Internal/Confidential | Editorial workflow | PostgreSQL | Until publication, rejection, or approved archive expiry | Delete/archive through editorial process |
| Publication history | Catalog/Audit | Internal | Accountability and rollback | PostgreSQL/audit | Long-lived approved period | Retain independently from current draft where required |
| Moderation notes | Administration | Confidential | Editorial review | PostgreSQL | Limited business period | Delete/expire according to policy |
| Content rights metadata | Catalog/Legal | Confidential | Regional and temporal availability | PostgreSQL | Contract lifecycle plus approved legal period | Retain when required for rights evidence |

Published content intended for public distribution is not personal data by default, but contributor or contract metadata may be confidential.

## 10. Media Assets

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Original audio/image upload | Media | Internal/Confidential | Source of published derivatives | Object storage | Rights lifecycle plus rollback period | Asynchronous deletion after DB state change |
| Published derivative | Media | Public or Restricted | Delivery to eligible clients | Object storage/CDN | While content version is supported | Purge CDN then delete object after retention |
| Premium media | Media/Entitlements | Restricted | Premium playback/offline use | Private object storage | Availability period plus rollback window | Revoke access immediately; delete according to lifecycle |
| Upload checksum | Media | Internal | Integrity verification | PostgreSQL | Asset lifetime | Delete with asset metadata |
| Malware scan result | Media/Security | Confidential | Publication safety | PostgreSQL/security log | Approved security period | Retain summary; remove raw scan artifacts when no longer required |
| Processing logs | Media/Operations | Internal | Diagnose pipeline | Logging platform | Short operational period | Expire automatically |

Temporary uploads, failed multipart uploads, and abandoned upload intents require automatic cleanup.

## 11. Subscription and Billing Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Subscription state | Billing | Confidential | Entitlement calculation and support | PostgreSQL | Contract/account lifecycle plus approved financial period | Retain or pseudonymize as legally required |
| Provider transaction ID | Billing | Restricted | Idempotency and reconciliation | PostgreSQL | Financial/legal period | Retain when required, detach from active profile where possible |
| Purchase proof/receipt | Billing | Restricted | Provider verification | Encrypted persistence where necessary | Minimum necessary verification/legal period | Delete raw proof as early as policy permits |
| Entitlement history | Entitlements | Confidential | Access decisions and support | PostgreSQL | Approved operational/financial period | Pseudonymize after account deletion if retention required |
| Refund/revocation reason | Billing | Confidential | Reconciliation and support | PostgreSQL | Financial/legal period | Retain under restricted access |
| Manual override record | Administration/Audit | Restricted | Accountability | Audit store | Long-lived approved audit period | Not deleted through normal user flow when legally justified |

The platform must not store full payment-card details. App-store or payment providers remain the system of record for payment instruments.

## 12. Notification Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| In-app notification | Notifications | Confidential | Durable user communication | PostgreSQL | Category-specific period | Delete/expire with account and policy |
| Push token | Notifications | Restricted | Device delivery | Encrypted PostgreSQL | Until revoked/invalid/unused beyond policy | Delete immediately when invalid or account deleted |
| Delivery attempt | Notifications | Confidential | Retry and diagnostics | PostgreSQL | Short operational period | Aggregate/expire |
| Email delivery reference | Notifications | Confidential | Delivery support | PostgreSQL/provider | Short operational period | Expire according to provider and platform policy |
| Notification preference | Notifications | Confidential | Consent and channel control | PostgreSQL | Account lifetime plus preference audit where required | Delete with account except retained consent evidence if required |
| Template version | Notifications | Internal | Reproducibility and audit | PostgreSQL/config repository | Retain while referenced | Archive after dependency ends |

Rendered message bodies should not contain unnecessary child data. Provider payloads must be minimized.

## 13. Advertising Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Eligibility state | Advertising | Confidential | Enforce free/premium policy | PostgreSQL/Redis | Short operational period | Delete with account/profile |
| Session count for ad frequency | Advertising | Confidential | Two-session rule | PostgreSQL/Redis | Minimum operational period | Reset/expire according to rule |
| Ad decision record | Advertising/Analytics | Confidential | Policy verification and aggregate reporting | PostgreSQL/analytics | Short approved period | Pseudonymize/aggregate then expire |
| Provider impression/click ID | Advertising | Restricted | Reconciliation where used | Provider/platform | Minimum necessary period | Delete/pseudonymize according to consent and policy |

Child profiles must not be used for unrestricted behavioral advertising. Advertising data requires explicit product, privacy, and provider review.

## 14. Administration and Support Data

| Data | Owner | Sensitivity | Purpose | Storage | Retention posture | Deletion behavior |
|---|---|---|---|---|---|---|
| Admin identity and role | Identity/Administration | Restricted | Access control | PostgreSQL | Employment/role lifecycle plus audit period | Disable then retain limited audit reference |
| Support case | Administration | Confidential/Restricted | User support | PostgreSQL/ticket system | Case-specific approved period | Redact or delete personal content when no longer required |
| Admin action reason | Audit | Restricted | Accountability | Audit store | Long-lived approved period | Retain under restricted access |
| Export job | Administration | Restricted | Data delivery | PostgreSQL/object storage | Very short availability window | Delete export object automatically |
| Bulk-operation result | Administration | Confidential | Operational accountability | PostgreSQL | Limited operational/audit period | Expire detail, retain aggregate audit where needed |

Support interfaces should display the minimum information necessary for the assigned role and task.

## 15. Audit Records

Audit data is distinct from operational logs.

Audit records may include:

- actor ID and actor type;
- action;
- target type and ID;
- timestamp;
- reason;
- outcome;
- correlation ID;
- before/after summary for approved high-risk changes.

Audit records are append-only from normal application flows. Retention is longer than ordinary logs where accountability, security, financial, or legal requirements justify it. Access to audit records must itself be authorized and auditable.

Audit records must still minimize personal data. They should reference internal identifiers rather than copy complete user records.

## 16. Operational Logs and Traces

| Data | Sensitivity | Retention posture |
|---|---|---|
| Application logs | Internal/Confidential | Short operational period based on incident needs |
| Security logs | Restricted | Approved security period |
| Distributed traces | Internal/Confidential | Shorter than logs unless sampled for incidents |
| Infrastructure logs | Internal | Operational period |
| Crash reports | Confidential/Restricted | Minimum diagnostic period |

Logs and traces must exclude passwords, PINs, tokens, authorization headers, raw purchase proofs, signed URLs, child names, and arbitrary request/response bodies.

When an incident requires temporary extended retention or increased logging, the change must be scoped, approved, monitored, and reverted.

## 17. Analytics Data

Analytics must use privacy-safe events and purpose-specific schemas.

Required practices:

- use pseudonymous identifiers where user-level analysis is necessary;
- aggregate as early as practical;
- avoid sending child display names, emails, tokens, raw text, or exact sensitive attributes;
- define event owner and purpose;
- define retention for raw and aggregated forms;
- prevent analytics outages from blocking product flows;
- support deletion or disassociation where technically and legally required;
- review third-party analytics providers before adoption.

Event collection not linked to a documented product or operational question should be removed.

## 18. Local Mobile Data

| Data | Sensitivity | Storage | Retention/deletion behavior |
|---|---|---|---|
| Access/refresh credentials | Restricted | Platform secure storage | Clear on logout, revocation, or account deletion |
| Download manifests | Restricted | Local database | Remove when entitlement expires or content is revoked |
| Downloaded premium media | Restricted | Protected app storage | Remove on revocation/expiry according to offline policy |
| Playback progress queue | Restricted | Local database | Remove after acknowledged sync or profile deletion |
| Catalog cache | Internal/Confidential | Local database/cache | Expire or replace by version |
| Notification cache | Confidential | Local database | Remove with account or notification expiry |
| Crash diagnostics | Confidential | Local temporary storage/provider SDK | Upload minimally and expire |

Local database migrations must preserve deletion semantics. Logout and account switching must not expose one account's data to another.

## 19. Data Export

A parent-account data export must:

1. require recent authentication and Parent Zone authorization where applicable;
2. create an auditable export request;
3. gather data from each owning context;
4. exclude secrets, hashes, internal security controls, and third-party credentials;
5. produce a documented machine-readable or human-readable package;
6. encrypt or securely protect the generated object;
7. use a short-lived delivery link;
8. expire and delete the export automatically;
9. record completion, access where appropriate, and deletion.

The export process must be asynchronous, resumable, idempotent, and observable.

## 20. Account Deletion Workflow

Account deletion is a stateful workflow:

1. authenticate and confirm the request;
2. record the deletion request and effective date;
3. revoke sessions and parent elevation;
4. disable account access;
5. delete or pseudonymize child profiles and listening data;
6. revoke push tokens and offline packages;
7. suppress future marketing and non-required notifications;
8. delete export objects and temporary files;
9. instruct each owning context to delete or retain according to policy;
10. reconcile failed cleanup operations;
11. preserve only approved legal, financial, security, or audit records;
12. mark completion and notify the parent through an approved channel.

Deletion events and commands must be idempotent. A failed downstream deletion must remain visible in a retryable backlog and must not be silently marked complete.

## 21. Child Profile Deletion

Deleting a child profile must remove or disassociate:

- profile attributes;
- playback progress and listening history;
- favorites;
- recommendation state;
- offline operations and packages;
- profile-scoped notifications;
- analytics identifiers and raw profile-linked events where required;
- local device state after synchronization.

Account-level billing, parent identity, and legally retained audit records are not automatically deleted when one profile is removed.

## 22. Backup and Restore

Backups must be:

- encrypted;
- access-controlled;
- separated from production credentials;
- monitored for successful completion;
- tested through restoration exercises;
- retained according to an approved rotation schedule;
- deleted automatically at the end of their lifecycle.

Deletion from active systems does not require editing immutable historical backups individually when the approved policy relies on backup expiry and prevents deleted data from being restored into active use without reapplying deletion records.

Restore procedures must replay deletion tombstones or reconciliation processes before restored data becomes available to users.

## 23. Non-Production Environments

Production personal data must not be copied into local, test, demo, or staging environments.

Use:

- synthetic accounts;
- deterministic test fixtures;
- generated child profiles;
- fake purchase proofs;
- sanitized media;
- provider sandboxes.

Any exceptional production-derived diagnostic data requires approval, minimization, masking, restricted access, and automatic expiry.

## 24. Third-Party Providers

Before a provider receives platform data, document:

- data fields transferred;
- purpose;
- controller/processor responsibility as applicable;
- storage region where relevant;
- encryption;
- provider retention;
- deletion capability;
- breach notification process;
- sub-processors;
- exit and migration procedure.

Provider SDKs must not collect undocumented device or child data. Mobile permissions must be limited to features that need them.

## 25. Retention Configuration

Retention periods should be configuration or policy-driven where practical, but must not be changeable without authorization and audit.

Each retention rule requires:

- data category;
- owner;
- purpose;
- sensitivity;
- active retention period;
- archive period if any;
- deletion method;
- legal/security exception;
- verification metric;
- responsible approver.

Placeholder values must not silently become production policy.

## 26. Deletion Methods

Approved methods include:

- hard deletion;
- irreversible pseudonymization;
- cryptographic erasure where architecture supports it;
- lifecycle expiry for temporary object storage;
- TTL expiry for ephemeral records;
- aggregate-only retention after raw-data deletion.

Soft deletion alone is not sufficient for a completed privacy deletion unless a documented retention reason requires the record to remain.

## 27. Observability and Evidence

Track at minimum:

- account-deletion requests by status and age;
- child-profile deletion failures;
- data-export generation duration and failures;
- expired export objects awaiting cleanup;
- invalid or stale push tokens;
- orphaned media objects;
- retention jobs by category;
- deletion retries and exhausted retries;
- analytics events rejected for schema/privacy violations;
- backup creation, restore tests, and expiry;
- access to restricted audit/export data.

Metrics must not expose personal data through labels.

## 28. Testing Requirements

Tests must cover:

- account deletion across all bounded contexts;
- child-profile deletion;
- session and token revocation;
- push-token cleanup;
- offline-package revocation;
- export authorization and expiry;
- retention-job idempotency;
- backup restore followed by deletion reconciliation;
- removal of personal data from logs and events;
- analytics pseudonymization;
- cross-account isolation on mobile devices;
- provider deletion integration where supported.

## 29. Review Checklist

- Is the data necessary for a documented purpose?
- Who owns the authoritative record?
- What sensitivity class applies?
- Where is the data copied?
- How long is each copy retained?
- How does account/profile deletion propagate?
- Is the data present in logs, traces, events, analytics, backups, or local storage?
- Can access be revoked?
- Is export behavior defined?
- Are retention and cleanup observable?
- Has the relevant privacy/security review occurred?

## 30. Related Documents

- `Database_Design.md`
- `Security_Architecture.md`
- `Logging_Monitoring.md`
- `Mobile_Architecture.md`
- `Notifications.md`
- `Event_Catalog.md`
- `C4_Model/07_Security_Trust_Boundaries.md`
- `C4_Model/09_Data_Ownership_Matrix.md`
- `C4_Model/12_Security_Control_Matrix.md`
- `C4_Model/13_Resilience_and_Failure_Mode_Catalog.md`

## 31. Ownership and Maintenance

Privacy and Architecture jointly own this map. Each bounded context owner is responsible for the accuracy of its data inventory, retention behavior, deletion implementation, export behavior, and telemetry. The document must be reviewed before production launch and whenever a new data field, provider, analytics event, storage system, export capability, or retention exception is introduced.