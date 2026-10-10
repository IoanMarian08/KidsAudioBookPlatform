# User Flows

Version: 2.0.0  
Status: Implementation baseline  
Owner: Product & UX

## 1. Rules shared by all flows

- Parent identity and child profile are different authorization contexts.
- Sensitive settings, purchases and account operations require Parent Zone elevation.
- Every transition must define loading, empty, offline, cancelled, expired-session and error states.
- Child-facing screens must remain calm, age-appropriate, and free from transactional prompts.
- Analytic events use non-identifying child references where possible.
- Never use back navigation, deep links or notification routes to bypass a parental gate.

## 2. Onboarding and first playback

~~~mermaid
flowchart TD
    A[Install and launch] --> B[Parent welcome and privacy notices]
    B --> C{Existing parent?}
    C -->|Yes| D[Sign in]
    C -->|No| E[Register and verify]
    D --> F[Create/select child profile]
    E --> F
    F --> G[Curated child home]
    G --> H[Story detail]
    H --> I{Published and entitled?}
    I -->|Yes| J[Authorize and start playback]
    I -->|No| K[Safe locked-content state]
    K --> L[Parent Zone entry]
    J --> M[Save progress and resume later]
~~~

**Acceptance:** interrupted verification can resume safely; anonymous child does not reach account creation; failed stream authorization never exposes raw object storage keys; no purchase entry point from a child-facing modal.

## 3. Parent Zone access and settings

~~~mermaid
sequenceDiagram
    actor Parent
    participant App as Flutter
    participant API as Backend
    Parent->>App: Open Parent Zone
    App->>API: Request challenge / validate existing elevation
    API-->>App: Challenge or protected scope
    Parent->>App: Complete PIN/biometric-backed local step
    App->>API: Confirm parent authentication
    API-->>App: Short-lived elevated authorization
    Parent->>App: Edit child controls
    App->>API: Save settings with account ownership check
    API-->>App: Updated settings
~~~

Biometrics alone must not grant backend authorization unless backed by an approved server-verifiable session flow. Expired elevation returns to the challenge without losing unsaved child-safe UI state.

## 4. Playback and progress

1. Child selects a story/episode.
2. App requests playback authorization for active child profile.
3. Backend enforces publication, locale, age and entitlement.
4. Client receives signed URL and streaming metadata; media flows from CDN.
5. Player handles interruptions, headphones, pause, seek and background mode.
6. Progress saves locally immediately; network sync is throttled and idempotent.
7. A completion event is recorded once per meaningful completion.
8. On next device, server returns the accepted progress revision; conflict policy prevents stale overwrites.

**Failure branch:** offline + authorized download -> play locally; offline without grant -> friendly offline screen, not an endless spinner.

## 5. Offline downloads

~~~mermaid
flowchart LR
    A[Parent permits downloads] --> B[Child selects story]
    B --> C[Backend entitlement + device grant]
    C --> D[Download manifest and media]
    D --> E[Verify integrity / local encrypted storage]
    E --> F[Offline playback]
    F --> G[Reconnect and sync progress]
    G --> H[Grant refresh / expiry enforcement]
~~~

Provide cancel/retry/resume, storage quota, missing files, revoked grant and deleted profile states. The UI never promises indefinite access if the subscription has lapsed.

## 6. Subscription purchase/restore

Parent Zone -> Plans and pricing disclosures -> OS-native store purchase -> provider outcome -> server verification -> entitlement refresh -> protected confirmation. Cancelled purchase leaves entitlements unchanged. A purchase timeout triggers reconciliation, never optimistic permanent premium access. Restore purchases always runs verification.

## 7. Admin editorial publication

Draft -> Upload using scoped URL -> Scan/transcode -> Metadata validation -> Editorial review -> Approved -> Publish/schedule -> CDN availability -> Audit. Failed scanning, rights verification, asset mismatch or reviewer rejection routes back to draft/rework. Suspend/takedown invalidates serving and search/caches.

## 8. Notification interaction

A parent opts in and registers a device; notification deep links reopen a validated session and the correct account context. Marketing notifications respect preferences and local legal conditions. Never place sensitive child data in push previews.

## 9. Account export/deletion

Parent Zone elevation -> Explain data consequences -> Confirm -> Queue export/delete process -> Audit -> Retention exceptions reviewed -> Confirmation. A request cannot delete someone else's account; erasure workflows must remove child downloads and revoke credentials.

## 10. Flow-level QA matrix

| Flow | Happy path | Required negative paths |
|---|---|---|
| Sign in | Verified adult logs in | Bad password, lockout, expired refresh |
| Profile | Parent selects child | Foreign profile, archived profile |
| Catalog | Eligible story appears | Draft, wrong age, wrong locale |
| Play | Media starts and progress saves | CDN timeout, revoked entitlement |
| Parent Zone | Elevation works | Child attempt, expired challenge |
| Purchase | Verified store update | Cancel, duplicate webhook, refund |
| Download | Authorized offline playback | Space exhaustion, corrupt file, grant expiry |

Linked: [PRD](Product_Requirements_Document.md), [UX Guidelines](../02_UX_UI/UX_Guidelines.md), [System Flows](../03_Architecture/System_Flows.md).


## 11. Expanded cross-feature flows and failure branches

### UF-11 — Device changes account while Child World is active

1. Adult A's selected child has story progress and favorites shown.
2. Adult logs out, or session becomes revoked from another device.
3. App removes private profile context and clears elevated Parent Zone proof before showing sign in.
4. Adult B signs in and chooses one of B's own profiles.
5. UI loads only B's authorized home/progress/favorites; direct requests for A's profile/session IDs are rejected.
6. If offline while A logs out, client enters a safe signed-out state; it does not send queued A mutations under B's credentials.

**Alternative failures:** session-expiry during a pending save; account suspended; device reused by another household. Reference GL-AT-01, ID-AT-04, PR-AT-01.

### UF-12 — Parent restricts story already cached by child

1. Parent enters protected zone using a valid challenge.
2. Parent selects the intended child and changes allowed age/category settings.
3. profiles-service validates owner/proof and commits the change.
4. Child World refreshes catalog/home and hides now-ineligible story.
5. Child taps an old cached deep link or favorite.
6. catalog/playback authorization revalidates current restrictions and refuses new media grant.
7. Parent sees saved status and can reverse the change through the same protected path.

**Alternative failures:** save timed out; another profile was accidentally selected; catalog projection stale; proof expires during save. Reference PZ-AT-01/03/04, CA-AT-02/06.

### UF-13 — Parent purchases while provider is slow

1. Parent enters Parent Zone and opens configured subscription plans.
2. Approved storefront/localized price and terms are displayed.
3. Parent confirms native store sheet; mobile receives pending/success transaction reference.
4. billing-service verifies the transaction with Apple/Google and updates authoritative entitlements.
5. Only verified active/grace/trial rights, where policy permits, allow Premium access.
6. Parent receives correct outcome and can use Restore/Reconcile if delayed.

**Alternative failures:** purchase canceled; unsupported product; provider outage; duplicate callback; refund; another account tries restore. Reference SU-AT-01..09.

### UF-14 — Offline story sync after second device completion

1. Authorized device A downloads eligible story and verifies checksum.
2. Device A goes offline and listens to part of the story, writing local operations with unique IDs.
3. Device B (same authorized profile) finishes the story online.
4. Device A reconnects and sends queued operations to /sync/offline.
5. Server deduplicates, resolves against current authoritative completion and returns per-change result.
6. UI keeps Completed and only clears confirmed queued operations.

**Alternative failures:** batch response lost; entitlement expired; account/profile deleted; item suspended; device A attempts update under new account. Reference OF-AT-02..08.

### UF-15 — Editorial content urgent takedown

1. Staff with correct permission selects published story and records a suspension reason.
2. catalog-service commits current state and outbox event.
3. Consumer projections/cache/search update asynchronously.
4. Device still showing old cover attempts Play.
5. playback/media authority checks current publication and denies a new grant.
6. Staff audits status and uses reviewed operational procedure for previously issued URL exposure.

**Alternative failures:** event delayed/duplicated; media-service unavailable; scheduled publish runs later; content revision conflicts. Reference AM-AT-04/05, CA-AT-06.

### UF-16 — Parent requests deletion across microservices

1. Parent verifies identity/Parent Zone proof and reads consequence explanation.
2. Adult confirms deletion request; identity-service records durable workflow state.
3. Owning services revoke sessions/devices, profiles, playback data, offline grants, notifications and retained data as authorized.
4. Each owning service returns an idempotent outcome; financial/audit retention exceptions follow approved policy.
5. Only after all required acknowledgements is Completed visible to parent.
6. Offline devices reconnecting after deletion cannot use stale private data to regain access.

**Alternative failures:** canceled within an approved window, one service down, late event, legal retention, store billing still active. Reference PV-AT-01..03; DEC-008/017.

### UF-17 — Optional advertising remains gated

1. The default feature flag is disabled for all child journeys.
2. Story playback and completion proceed without ad SDK interaction.
3. If product/legal/store later approve a launch policy, eligibility is evaluated server-side only after qualified completion.
4. Verified Premium, missing consent, unsupported market and denied creative all result in no ad.
5. Playback never depends on provider readiness.

**Alternative failures:** duplicate completion; repeated ad token; provider failure. Reference AD-AT-01..07; DEC-004.

## 12. Flow testing matrix

| Flow | Happy path | Negative must test | Offline/partial failure |
|---|---|---|---|
| UF-11 Account switch | B owns new context | No A profile data | B cannot receive A offline queue |
| UF-12 Parent restrictions | Authorized save | Blocked link denied | Stale cache cannot override |
| UF-13 Purchase | Verified Premium | Forged/reused receipt denied | Provider timeout -> pending |
| UF-14 Offline progress | Successful sync | Duplicate change dedup | Lost response retry safe |
| UF-15 Takedown | Unpublish removes content | Unauthorized staff denied | Delayed events do not republish |
| UF-16 Deletion | Verified all services complete | Child route denied | Stalled saga not Completed |
| UF-17 Ads | Disabled by default | Child tracking disallowed | Provider outage does not block audio |

The detailed functional outcomes and screen IDs are maintained in [Complete Functional Specification](Functional_Specification/README.md) and [Screen Inventory](Functional_Specification/13_Screen_Inventory_and_UX_Handoff.md), not redefined independently here.
