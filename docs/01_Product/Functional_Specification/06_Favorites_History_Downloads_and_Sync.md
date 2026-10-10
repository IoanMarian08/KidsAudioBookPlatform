# 06 — Favorites, Listening History, Continue Listening, Offline Downloads and Sync

**Actor:** selected child profile and supervising parent.
**Relevant:** PRD-05/09, FR-PL-003..005. **Owner:** playback-service; media-service provides approved assets and manifests, billing-service validates rights.
**Contract:** [API Specification](../../03_Architecture/API_Specification.md) sections 31–35, [Offline ADR](../../00_Project/ADR/ADR-0014-offline-synchronization.md).

## 1. Per-profile favorites

**FS-OF-001** Every story favorite belongs to the current child profile and authenticated parent household. PUT /child-profiles/{id}/favourites/{storyId} adds, DELETE removes and GET lists; repeated add/remove is idempotent.

**FS-OF-002** Favorite status is consistent on cards, story detail and favorites list, including when a user returns from the player. A failure to save shows a safe retry and must not pretend the server committed.

**FS-OF-003** A suspended/removed story can be absent or marked unavailable in Favorites according to approved policy, but the favorite flag cannot grant new playback to prohibited content.

**FS-OF-004** Switching sibling hides all former favorites immediately; server rejects guessed foreign profile IDs even when cached.

## 2. History and Continue Listening

**FS-OF-005** Each started playback session saves authorized progress with profile+story/episode identity. Continue Listening GET /child-profiles/{id}/continue-listening contains resumable eligible items, sorted according to approved business rules.

**FS-OF-006** History GET /child-profiles/{id}/history shows past eligible listening records and appropriate completed/resumable state; the child cannot see another profile's activity.

**FS-OF-007** DELETE /child-profiles/{id}/history/{entryId}, where offered as a parent-authorized or child-safe action, removes the specified history entry only for the owned profile. It must not blindly delete a story record or a sibling's progress.

**FS-OF-008** Repeated/stale progress updates may not rewind an already completed story. Explicit replay is a new intentional playback choice, not an accidental last-write-wins regression.

**FS-OF-009** If content becomes unavailable since last listen, Continue Listening must not give an unsafe play shortcut and should provide a calm explanation rather than silently failing.

## 3. Offline eligibility and download management

Product intent offers Premium offline listening to authorized devices. Free tier download eligibility is governed by an approved commercial policy; do not assume Free can always download.

**FS-OF-010** POST /downloads/grants is requested only for selected/owned child profile, eligible published asset, device, and valid entitlement. An expiring signed link grants download transport; it is distinct from the offline listening license window.

**FS-OF-011** Download screen shows not downloaded, queued, downloading, paused/retryable, verifying, ready, expired/revoked, failed and removing states. A downloaded entry becomes Ready only after checksum/integrity and required metadata verification.

**FS-OF-012** POST /downloads/{grantId}/confirm records a validated completion when ready; GET /downloads lists only grants owned by the account/device as allowed; DELETE /downloads/{grantId} removes a granted download in an idempotent manner.

**FS-OF-013** Download actions account for insufficient disk space, storage permission changes, app background termination, unstable network, resume/range support, cancellation and cleanup of partial bytes. Cancel must not become a complete grant.

**FS-OF-014** Local story metadata remains tied to correct profile, audio version and protected media rights. Shared devices cannot accidentally expose sibling/private downloaded assets through profile switching or adult logout.

**FS-OF-015** Offline grace period, maximum devices, license TTL, entitlement downgrade handling and DRM/encryption strategy need explicit product/security/legal decisions. They are not arbitrary constants [OPEN: DEC-005/008 and additional offline policy sign-off].

## 4. Offline use and reconnection

When offline, the app may play only a previously authorized, verified, unexpired locally stored item permitted by stored constraints and approved grace policy. A missing network is not permission to unlock new Premium content or foreign child profiles.

**FS-OF-016** Offline playback records bounded local progress operations with unique change IDs and immutable profile/content identity; no duplicate mutation when reconnected.

**FS-OF-017** POST /sync/offline uploads queued operations and returns per-change accepted/rejected/conflict resolution per API contract. A failed batch does not cause loss of all local work; retries are bounded and idempotent.

**FS-OF-018** The server is authoritative for completion, entitlement and profile ownership. Stale offline partial progress cannot override a later server Completed state; legitimate resume conflicts follow documented revision and merge rules.

**FS-OF-019** Sync errors are reported without alarming children; adult diagnostics can distinguish expired entitlement, missing content, revoked profile, conflict and temporary network problem. The app keeps unsynced items until confirmed or explicitly discarded by policy.

**FS-OF-020** Profile switching and account logout isolate queues by account and profile. Uploading profile A's changes while signed into parent B is prohibited.

## 5. Example conflict resolution

Example: device A plays a story offline to position 310 seconds. Device B, for the same authorized profile, finishes the story online. A later reconnects and sends progress 310 seconds. The backend records/deduplicates the offline change but keeps the Completed state; the stale event does not rewind the story. If the user intentionally starts a replay, this is represented by a new explicit playback session and does not erase prior completion audit/history.

Another example: an offline download expires during a flight. The app must follow the approved offline license policy rather than a fabricated "always works forever" promise. It may display a neutral expired message and make retry available when internet returns.

## 6. Failure matrix

| Event | Expected behavior |
|---|---|
| Network drop during download | Pause/resume or retry; never label incomplete bytes Ready |
| Checksum mismatch | Quarantine/retry; do not play corrupt file |
| Purchase refunded | New download grants denied; offline policy governs outstanding grants |
| Parent restriction tightened | New online authorization denied; pre-existing offline policy must be explicitly safe |
| Duplicate offline change | One logical mutation; no double history/ad impression |
| Profile archived | Sync and new grants denied or handled by deletion policy |
| App uninstalled | Backend progress persists; device files removed by OS |
| Local cache/storage lost | Re-download only with current entitlement; server history remains |
| Offline sync conflicts | Per-item result and transparent reconciliation |
| Provider offline during reconciliation | Never convert uncertain rights into permanent Premium |

## 7. Given / When / Then

- **OF-AT-01:** Given two sibling profiles, when child A favorites a story, then child B does not see that favorite.
- **OF-AT-02:** Given a download fails checksum, when transfer ends, then it is not Ready and cannot be played as verified offline media.
- **OF-AT-03:** Given two devices and a stale offline position, when syncing after another device completed the story, then completion is preserved.
- **OF-AT-04:** Given a revoked/expired entitlement, when asking for a new download grant, then it is denied; existing local license follows explicit policy.
- **OF-AT-05:** Given a failed sync response, when retrying identical change IDs, then progress/history are not duplicated.
- **OF-AT-06:** Given profile A has queued offline changes and the parent logs out, then A's changes are not submitted under a different account.
- **OF-AT-07:** Given a story is suspended, when it appears on a stale Continue Listening card, then a new playback grant is denied.
- **OF-AT-08:** Given limited storage, when requesting a large download, then the user gets a clear recovery option and no corrupt Ready state.

## 8. Open questions and dependencies

Agree download device limits, license expiry and revocation timing, per-device encryption policy, explicit replay/completion merge semantics, progress retention period and handling of a partially downloaded updated rendition. Document approved decisions before releasing offline capability. Implementation uses playback-service, media-service and billing-service with isolated owned databases and authenticated internal REST/event contracts.
