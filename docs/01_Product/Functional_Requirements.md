# Functional Requirements

Version: 2.0.0  
Status: Baseline, pending product/legal validation  
Owner: Product & Engineering

## 1. Requirement format

Every requirement has a stable **FR-ID**, priority (P0/P1/P2), responsible bounded context and verifiable result. Backend is authoritative for ownership, entitlement, publication and safety. Contract details: [API Specification](../03_Architecture/API_Specification.md).

## 2. Accounts and Identity

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| FR-ID-001 | P0 | Adult can register and verify email/account contact | Verification token expires and is single use |
| FR-ID-002 | P0 | Adult can authenticate, refresh and revoke sessions | Rotation/revocation stops reuse |
| FR-ID-003 | P0 | Account recovery is secure and rate-limited | Enumeration-resistant responses |
| FR-ID-004 | P0 | Parent can update own preferences and request deletion/export | Ownership + audit |
| FR-ID-005 | P0 | Sensitive changes require recent authentication | Re-auth enforced on API |

## 3. Child Profiles and Parent Zone

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| FR-PR-001 | P0 | Parent creates, edits and archives child profiles | No cross-account access |
| FR-PR-002 | P0 | Child profile stores minimum necessary personalization | Optional fields, clear retention |
| FR-PR-003 | P0 | Switching profile changes favorites/progress/history context | Child A cannot see Child B data |
| FR-PR-004 | P0 | Parent Zone is PIN/challenge protected; optional biometrics | Expiry and brute-force protections |
| FR-PR-005 | P1 | Parent configures age/content preferences and playback limits | Server-side enforcement; safe default |

## 4. Catalog and Editorial

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| FR-CA-001 | P0 | Browse published stories, series, episodes, categories, collections | Hidden/suspended drafts excluded |
| FR-CA-002 | P0 | Filter by locale, age range, category, availability | Stable pagination |
| FR-CA-003 | P0 | Story detail shows suitable metadata and media information | No private editorial fields leaked |
| FR-CA-004 | P0 | Admin manages draft/review/publish/suspend/archive lifecycle | Role control and audit on every transition |
| FR-CA-005 | P0 | Audio/image upload uses controlled direct-to-storage flow | Scan and metadata validation before publish |
| FR-CA-006 | P1 | Search by approved title/metadata | Safe results and bounded queries |
| FR-CA-007 | P1 | Text and illustrations follow versioned timing cues | Playback seeking keeps synchronization |

## 5. Playback and Progress

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| FR-PL-001 | P0 | Eligible child can start/stream a story | Authorization then signed URL |
| FR-PL-002 | P0 | Player supports pause/resume/seek and background audio | Lifecycle integration test |
| FR-PL-003 | P0 | Per-profile progress is saved and restored | No sibling/account leakage |
| FR-PL-004 | P0 | Progress sync tolerates retries, duplicates and offline writes | Revision/conflict tests |
| FR-PL-005 | P1 | Offline downloads have device/entitlement policy | Expired rights deny new access |
| FR-PL-006 | P1 | Ambient audio can mix at safe default levels | Predictable stop/volume behavior |
| FR-PL-007 | P1 | Playback can show synchronized text and artwork | Timing tested at seeks and speed changes |

## 6. Subscription and Entitlements

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| FR-SU-001 | P0 | Show available plans/eligible offer information in Parent Zone | No purchase UI in child area |
| FR-SU-002 | P0 | Validate Apple/Google store purchase server-side | Forged receipt rejected |
| FR-SU-003 | P0 | Process provider notifications idempotently | Duplicates and out-of-order covered |
| FR-SU-004 | P0 | Central entitlement policy controls premium content | Expiry/refund/revocation enforced |
| FR-SU-005 | P1 | Reconcile subscriptions after webhook outages | Converges to provider truth |
| FR-SU-006 | P1 | Support trial if eligibility/rules are approved | Prevent multiple unauthorized trials |

## 7. Notifications, Admin, Support

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| FR-NO-001 | P1 | Parent registers devices and chooses notification preferences | Opt-out takes effect |
| FR-NO-002 | P1 | Transactional messages sent through audited templates | No sensitive payload in push preview |
| FR-NO-003 | P1 | Retry transient sends and dead-letter persistent failures | Bounded attempts + replay |
| FR-AD-001 | P0 | Admin RBAC for catalog, moderation and support | Least privilege test |
| FR-AD-002 | P0 | Admin edits create immutable audit entries | Who/what/when captured |
| FR-AD-003 | P1 | Administrative exports are asynchronous and access controlled | Expiring download grant |
| FR-SP-001 | P1 | Parent can send a support request | Minimal data collection + tracking |

## 8. Advertisement gate (optional)

Ads are **not** an unconditional MVP feature. If commercial policy approves free-tier ads, eligibility must be evaluated server-side; disable behavioral targeting of children, enforce age-appropriate creatives, provide clear parent controls, and pass applicable regulation/platform-policy review before activation. Ads must not interrupt bedtime playback or block essential controls.

## 9. Negative and boundary scenarios

- Expired session cannot renew after revoked refresh token.
- Another parent's child profile ID is rejected regardless of its existence.
- Draft or suspended story ID returns a safe not-found/forbidden response.
- Duplicate progress writes or purchase webhooks do not duplicate effects.
- Offline playback obeys an explicit grant expiry and device policy.
- Deleted accounts remove/anonymize information according to retention policy.
- Provider outage degrades safely and never treats unverified purchase as premium.

## 10. Ready-to-implement checklist

Every FR requires named owner, story link, request/response/API contract where relevant, data migration impact, access-control matrix, error behavior, analytics/privacy review, observability and automated tests. A P0 FR is not complete until these checks pass in staging.

Related: [PRD](Product_Requirements_Document.md), [User Stories](User_Stories.md), [Testing Strategy](../06_Testing/Testing_Strategy.md).
