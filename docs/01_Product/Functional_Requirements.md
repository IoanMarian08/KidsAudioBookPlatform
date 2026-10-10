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


## 11. Functional specification rule families

The [Complete Functional Specification](Functional_Specification/README.md) is the detailed source for each rule, user-visible state and Given/When/Then test. The following is a traceability index, **not a replacement** for the acceptance evidence defined there.

| Functional rules | Product area | FR coverage | Owning implementation |
|---|---|---|---|
| FS-GL-001..014 | World navigation, accessibility, safe errors and device interruptions | All FRs | Flutter plus owning services |
| FS-ID-001..018 | Adult registration, verification, login, recovery, sessions and deletion request | FR-ID-001..005 | identity-service |
| FS-PR-001..017 | Profile creation, ownership, Child Room and switching | FR-PR-001..005 | profiles-service + catalog/playback |
| FS-CA-001..016 | Curated discovery, categories, series and safe search | FR-CA-001..007 | catalog-service |
| FS-PL-001..023 | Playback, synchronized text/images, ambient sound and completion | FR-PL-001..004/006/007 | playback-service + media-service |
| FS-OF-001..020 | Favorites, history, progress, downloads, offline sync | FR-PL-003..005 | playback-service + media-service |
| FS-PZ-001..018 | Parent Zone elevation and adult controls | FR-PR-004/005, FR-ID-005 | identity-service + profiles-service |
| FS-SU-001..016 | Store purchases, trials, billing status and verified rights | FR-SU-001..006 | billing-service |
| FS-AD-001..010 | Optional ad eligibility and child-safety safeguards | GATED; PRD-13 | advertising-policy-service only after approval |
| FS-NO-001..008 | Parent notification inbox/preferences/devices | FR-NO-001..003 | notifications-service |
| FS-SP-001..004 | Adult support request | FR-SP-001 | admin-service or approved support adapter |
| FS-PV-001..008 | Child data minimization, export design and deletion saga | FR-ID-004 plus privacy controls | owning services / identity coordination |
| FS-AM-001..022 | Restricted staff editorial, media workflows and support audit | FR-CA-004/005, FR-AD-001..003 | admin/catalog/media/billing |
| FS-CQ-001..010 | Rights, age review, audio quality and sync media acceptance | FR-CA-004/005/007 | content staff + catalog/media |

## 12. Mandatory negative requirements

All capabilities implement the following security and behavior constraints:

| Boundary | Negative requirement |
|---|---|
| Adult authentication | Expired/revoked token, reset replay or foreign session ID never grants authority |
| Parent Zone | Missing/expired elevated proof never permits PIN, profile restrictions, subscription or account deletion |
| Profiles | Sibling/other-parent IDs never expose favorites/history/progress |
| Catalog | Draft, suspended, blocked-age or rights-expired content never gets new playable grants |
| Playback | Seeking to end or repeated completion never creates unearned duplicate completion |
| Billing | Client success or delayed provider event never grants unverified Premium |
| Offline | Corrupt/partial bytes never appear Ready; stale progress never rewinds Completed |
| Notifications | Opted-out optional messages are not sent; push provider outage does not block audio |
| Administration | Editor without permissions cannot approve/publish; unscanned asset never becomes public |
| Privacy | Deletion is not declared complete before each required owning service confirms |
| Monetization | Child-targeted ads remain disabled until approved; no child behavioral targeting |

## 13. Feature handoff record

Every implementation PR references: FR ID, FS IDs, screens from [Screen Inventory](Functional_Specification/13_Screen_Inventory_and_UX_Handoff.md), positive/negative acceptance cases, API path(s), owning microservice, data migration/outbox impact, privacy review, observable outcome and deployment gate. If an API operation is missing or undecided, create an explicit contract task; do not introduce a public endpoint silently.

## 14. Decisions that block hardcoding

[Decision Register](../00_Project/DECISION_REGISTER.md) governs exact pricing/trials, age/locale/retention, profile quotas, ad eligibility, offline rights, completion threshold, Parent Zone security windows, notification cadence, data export and editorial roles. Implement safe foundations and configuration interfaces where justified, but mark dependent user behavior gated until approval.
