# 03 — Child Profiles, Selection and Child Room

**Actors:** parent creates/manages, child uses selected profile.
**Traceability:** PRD-02/03; FR-PR-001..005.
**Owner:** profiles-service; catalog-service and playback-service supply home content.

## 1. Child profile creation and ownership

**FS-PR-001** After login the adult sees existing child profiles or guided creation. Children cannot create unrestricted identities.

**FS-PR-002** Editable profile attributes include an approved nickname, age band, avatar, room theme, optional favorite color/animal and interests/preferences consistent with Product Bible. Collect minimum necessary child data; exact birth dates are not required by default [OPEN: DEC-008].

**FS-PR-003** Every profile is owned by exactly one authenticated parent account. The owner checks GET/POST/PATCH/DELETE /child-profiles and preferences server-side; a guessed foreign UUID cannot grant access.

**FS-PR-004** Account profile limits and Premium upgrades are evaluated via actual entitlements. The exact free/Premium counts and downgrade behavior are [OPEN: DEC-005]; do not hardcode a guessed number.

**FS-PR-005** An edited age band or blocked category immediately affects eligible catalog/playback decisions; UI refreshes in-flight cards and does not let a stale favorite bypass parental controls.

**FS-PR-006** Archive or delete requires Parent Zone proof, impact explanation and confirmation. Profile progress/downloads and data retention follow an approved deletion policy; no silently destructive downgrade.

## 2. Profile selection

The selection screen presents large avatars, readable names, clear parent entry and an Add profile option protected by adult verification. No account billing details appear.

**FS-PR-007** POST /child-profiles/{profileId}/select chooses the current context after verifying ownership. Before showing a new profile, clear the previous profile's favorites, history, player overlay, search/home recommendations and private download labels.

**FS-PR-008** A failed/expired selection never displays a partial sibling profile. Show safe neutral recovery and allow adult login if session expired.

**FS-PR-009** On relaunch, a saved selected profile can be proposed only if the adult session is still the same and the profile is active/owned. Otherwise the app returns to selection.

## 3. Child Room content

The child-facing home is a calm personal listening space. Typical visible elements: avatar/nickname; rabbit mascot; gentle time-of-day background; Continue Listening (when present); curated story cards; categories/collections; Favorites; and eligible Downloads. Screen layout and token decisions belong to UX/UI documents.

**FS-PR-010** GET /child-profiles/{profileId}/home yields a safe feed filtered by profile age, language, restrictions, publication and catalog eligibility. Stale feed data cannot grant playback itself.

**FS-PR-011** Time-of-day atmosphere may adjust visuals and suggested bedtime stories from local device time. Do not infer geography, collect location or restrict content solely from the clock.

**FS-PR-012** Mascot interactions must be positive and non-manipulative, with no punishment for inactivity, frightening imagery, gambling-style rewards or pressure to subscribe.

**FS-PR-013** A pre-reader must be able to recognize core navigation via visual/audio cues; screen reader, reduced motion and large controls remain supported.

## 4. Parent-managed personalization and restrictions

Parent Zone accesses GET/PUT /child-profiles/{profileId}/preferences and /parental-settings. It may group content age range, blocked categories, safe bedtime preferences and playback restrictions.

**FS-PR-014** An edit supports Save, Cancel, invalid-field feedback and confirmed server state. Unsuccessful saves must not appear committed. Never overwrite another simultaneous edit silently.

**FS-PR-015** The service validates restrictions on the backend, and downstream catalog/playback decisions respect them. Direct story links and offline state must not bypass active parental restrictions.

**FS-PR-016** Each profile has independent settings, favorite stories, listened items, resume progress and appropriate local state. Parent-global preferences are labeled separately.

**FS-PR-017** On account plan downgrade with excessive profiles, explain the policy in Parent Zone and preserve child data; exact active/inactive behavior needs owner approval [DEC-005].

## 5. Key states

| Situation | Behavior |
|---|---|
| Empty household | Adult setup / create first profile |
| Network unavailable | Do not open a foreign/stale profile; authorized local story rights handled separately |
| Profile not owned or archived | Neutral unavailable response and adult recovery |
| Too many profiles for entitlement | Parent-facing policy explanation, no destructive automatic cleanup |
| Restricted story on home | Remove/disable, never make it playable |
| Profile switch during play | Stop/re-authorize according to active-profile context |
| Theme artwork unavailable | Use an accessible approved static placeholder |

## 6. Acceptance scenarios

- **PR-AT-01:** Given siblings A and B, when switching to B, then A's progress, favorites and search/home personalization are not shown.
- **PR-AT-02:** Given parent A, when requesting profile B owned by parent B, then the request is denied.
- **PR-AT-03:** Given a blocked age/category change, when opening a cached story deep link, then playback authorization rejects it.
- **PR-AT-04:** Given creation timed out, when retrying, then an identical profile is not duplicated unexpectedly.
- **PR-AT-05:** Given a downgrade with excess profiles, then personal child records are not silently deleted.
- **PR-AT-06:** Given Parent Zone proof expires during an edit, when saving, then server denies the update and UI offers fresh challenge.

**Open:** precise age representation, profile quotas, default room themes, first languages [DEC-005/007/008/010]. Related: [Catalog](04_Catalog_Search_and_Discovery.md), [Parent Zone](07_Parent_Zone_and_Controls.md).
