# Blueprint 03 — Playback, Progress, Offline Grants and Sync

Version: 1.0  
Status: Implementation blueprint / unimplemented  
Owners: Playback, Offline, Mobile, QA

## 1. Outcome

An authorized child profile can stream published stories, resume accurately across devices and listen to valid downloaded media offline. The architecture remains safe when the app crashes, messages duplicate, a device is disconnected or a subscription expires.

**Normative references:** [API Specification](../03_Architecture/API_Specification.md) §§30–35, [Database Design](../03_Architecture/Database_Design.md) §§11–12, [ADR-0014](../00_Project/ADR/ADR-0014-offline-synchronization.md), [Event Catalog](../03_Architecture/Event_Catalog.md), [Mobile Architecture](../03_Architecture/Mobile_Architecture.md).

## 2. Inputs and authoritative checks

For POST /playback/sessions:
1. Authenticate parent account and identify active/explicit child profile.
2. Verify profile belongs to that account and is not archived.
3. Verify story/episode is published, supported for age/locale, and not blocked by parental controls.
4. Check server entitlement for premium access; cache may be used only with safe expiration/invalidation.
5. Create/reuse the playback session under an idempotency policy, then issue limited-scope signed URLs for CDN.
6. Return playback session ID, permitted media and resume position.

**Never** trust client-passed premium flags or a previously displayed catalog card as authorization.

## 3. API/data mapping

| API | Internal ownership | Details |
|---|---|---|
| POST /playback/sessions | playback.playback_sessions | session/account/profile/content/device reference |
| PUT /playback/sessions/{sessionId}/progress | playback.playback_progress | profile/content-position revision; idempotent by session+sequence |
| POST /playback/sessions/{sessionId}/complete | playback and advertising policy | completion determined server-side |
| POST /playback/sessions/{sessionId}/stop | playback | records safe stop state |
| GET /child-profiles/{id}/continue-listening | playback read model | filtered to current profile |
| POST /downloads/grants | playback.device_downloads; media.offline_manifests | premium + device-scoped grant |
| POST /downloads/{grantId}/confirm | offline grant registration | no duplicate confirmation effect |
| POST /sync/offline | playback sync | per-change result, dedupe and conflict resolution |

**Important unit boundary:** the public API currently uses positionSeconds/durationSeconds while the PostgreSQL model stores position_ms/duration_ms. Define conversion/rounding and constraints in one adapter; do not mix units in domain objects. Use whole seconds in existing API responses until an approved API change.

## 4. Playback state machine

~~~mermaid
stateDiagram-v2
  [*] --> Initial
  Initial --> Authorizing: Tap play
  Authorizing --> Buffering: Grant succeeds
  Authorizing --> Denied: Not eligible
  Buffering --> Playing: First bytes decoded
  Buffering --> RecoverableError: CDN or network error
  Playing --> Paused: Pause or audio focus lost
  Paused --> Playing: Resume
  Playing --> Completed: Accepted completion
  Playing --> Stopped: Exit / stop
  RecoverableError --> Buffering: Retry
~~~

Flutter stores local playback state; server remains authoritative for completion, entitlements and access. Audio file bytes should bypass backend API and use CDN/object storage range requests.

## 5. Progress conflict policy

- Every update is scoped to session, account, profile and playable item.
- Deduplicate by existing API sessionId + sequenceNumber and offline changeId.
- Reject negative position, zero/negative duration and impossible content mismatch.
- A confirmed completion cannot be undone by a stale partial update.
- For non-completed states, prefer trusted revision/client time within bounded clock skew; define explicit user restart semantics.
- Never silently let another device's older write reset progress.
- If server rejects an offline mutation, return a **per-change reason** and authoritative state so UI can resolve without losing local data prematurely.

**Example scenario:** device A reaches 310 seconds offline, device B completes the story online, then A reconnects. Sync records A's event but maintains server Completed status and does not rewind to 310 seconds.

## 6. Download grant lifecycle

~~~mermaid
stateDiagram-v2
  [*] --> Requested
  Requested --> Authorized: Premium and device verified
  Authorized --> Downloading: Fetch manifest
  Downloading --> Ready: All checksums valid
  Downloading --> Failed: Network, storage or integrity failure
  Failed --> Downloading: Retry before grant expiry
  Ready --> Expired: Offline time window ends
  Ready --> Revoked: Policy or entitlement change
  Ready --> Removed: Parent/device removes
~~~

Download URLs are short-lived; offline usage rights are **not** equivalent to URL lifetime. Store license/grant expiry and device binding locally using platform secure storage where feasible; do not rely on perpetual offline capability. Cache/rollback policies must be tested on both platforms.

## 7. Data, events and transactions

PostgreSQL owns playback sessions, one progress row per profile/playable item, optional progress event history and device downloads. Object storage owns media bytes; entitlement module owns subscription verification. Progress mutation + outbox event should be atomic where an integration event is required.

Use ListeningSessionStarted, ListeningProgressUpdated, StoryCompleted, ListeningSessionEnded and OfflineDownloadAuthorized/Completed/Removed/EntitlementRevoked from the [Event Catalog](../03_Architecture/Event_Catalog.md).

## 8. Failure scenarios

| Failure | Required behavior |
|---|---|
| CDN timeout during streaming | Player remains controllable, offer retry or valid local file |
| Redis unavailable | Authoritative DB fallback or safe refusal for privileges |
| Expired signed URL mid-session | Refresh via authorized API; do not leak private object key |
| Device loses network | Continue if valid downloaded asset, queue progress locally |
| Download checksum differs | Reject file and retry, never mark Ready |
| Premium refunded/expired | Deny future new download grants and follow documented offline expiry/revocation policy |
| Background app termination | Save local checkpoint and resume safely |
| Two simultaneous devices | Versioned merge; no stale rollback of Completed |

## 9. Tests and Done

Unit: completion threshold, position conversion, progress merging, entitlement policy. Integration: session ownership/If-Match where applicable, durable idempotency, download manifest. Mobile/E2E: headphones/audio focus, background mode, low storage, offline reconnection, seek and timed illustrations. Resilience: CDN/DB/broker outage without unsafe bypass.

**Still requiring decisions:** concrete offline grant TTL and policy, device limit, retained progress duration, conflict edge cases for explicit restart, and whether download encryption is technically/legally required. Record choices before launch and update API/DB contracts.
