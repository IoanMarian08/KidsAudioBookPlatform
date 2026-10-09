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
