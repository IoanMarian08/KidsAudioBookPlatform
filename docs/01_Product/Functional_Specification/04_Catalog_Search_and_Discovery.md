# 04 — Catalog, Series, Collections, Search and Discovery

**Primary actor:** selected child profile; adult restricts availability; editorial team publishes.
**Requirements:** PRD-03, FR-CA-001..007. **Owner:** catalog-service.
**Contracts:** [API Specification](../../03_Architecture/API_Specification.md) sections 24–29; [Catalog/Media blueprint](../../07_Blueprints/02_Catalog_Media.md).

## 1. Content that a child may discover

Catalog entities include story, series, episode, category, collection and ambient sound. Story cards carry approved localized title, cover, duration, suitability band, access tier and enough description for the child/parent to choose intentionally. Curated lists can be seasonal, age-specific, bedtime or interest-based.

**FS-CA-001** GET /stories, /series, /episodes/{episodeId}, /categories and /collections expose only published, age-permitted and parent-authorized metadata. Drafts, embargoed/suspended content, unreviewed media assets and unsupported locales never become public through guessed IDs.

**FS-CA-002** Locale and language are clearly visible when relevant; a textual fallback must not silently display audio from the wrong language. Initial supported locale set, legal copy and fallback policy require approval [DEC-007].

**FS-CA-003** Free/Premium badges are informational only. A cached badge never authorizes stream/download; billing-service entitlement checks still govern paid content.

**FS-CA-004** Editorial safety review and content rights override recommendation rank and personalized relevance, even when a story was previously favorited.

## 2. Home content sections

A healthy curated Child Room can show: Continue Listening, bedtime selections, approved featured stories, age/category suggestions, series continuation, collections and new stories. The order may change through reviewed configuration, but never through a manipulative endless engagement objective.

**FS-CA-005** The home feed GET /child-profiles/{profileId}/home is filtered for that profile's restrictions, locale and approved content set. When a filter leaves no item, omit the section or present a calm empty explanation; never expand to disallowed stories.

**FS-CA-006** MVP recommendations may use clear editorial criteria and limited profile preferences. No child behavior-based advertising, sensitive profiling or opaque high-pressure engagement scoring.

**FS-CA-007** Tapping a story tile opens details, not automatically purchases or external URLs. Repeated tapping cannot create duplicate playback sessions without the session API's idempotent semantics.

## 3. Search, category and collection interactions

A child or assisting adult can navigate categories/collections/series or search approved metadata. Search input remains simple, with accessibly labeled text field, optional suggested categories and easy clear action. Voice search is not assumed in MVP.

**FS-CA-008** GET /search validates query length/type and server-side publication, locale, age and parental restrictions; no raw editorial notes or database query errors may appear.

**FS-CA-009** Filtering changes the result set and visible selected filters. Resetting filters restores the eligible set, never unblocks parental restrictions.

**FS-CA-010** No matches, insufficient network and no approved catalog in an age band are distinct states with different actions: clear filter, retry or ask parent for preferences.

**FS-CA-011** List pagination follows the public API; the mobile list avoids duplicate story cards by stable ID if publication changes while paging. Sorting must not reveal internal moderation/approval timestamps.

**FS-CA-012** Search strings and analytics are minimized per child privacy policies; do not retain personally identifying search content unnecessarily.

## 4. Story and series details

A story detail shows approved cover, title, synopsis, age suitability, duration, language, tags, series membership, Free/Premium indicator, Play, Favorite, and optional Download if eligible. Illustrations may be previewed only if editorially approved.

**FS-CA-013** If a story is unavailable or its approved locale rendition is missing, its Play action is denied or disabled with a neutral explanation; the UI never fabricates a signed media URL.

**FS-CA-014** Series details list episodes with stable ordering and current eligibility. Missing, unpublished and suspended episodes never become indirectly accessible through a neighboring episode.

**FS-CA-015** Premium detail presentation in Child World is gentle and non-transactional. The child is never taken directly to the app store or a checkout screen; any upgrade action requires Parent Zone.

**FS-CA-016** If a story was taken down while details were cached, new playback authorization must fail safely; the catalog UI refreshes to correct the visible state.

## 5. Empty, partial and failure behavior

| Situation | User experience | Business outcome |
|---|---|---|
| No search match | Friendly empty illustration; clear query | Only eligible set considered |
| Search service timeout | Retry; retain query where safe | Do not falsely imply no catalog |
| Premium item on Free plan | Locked/informational; parent-directed path | No unauthorized media |
| Story cover unavailable | Approved neutral placeholder | Avoid leaking private media key |
| New episode added mid-list | Stable dedup/refresh | Correct published ordering |
| Age restriction tightened | Refresh lists and cards | Never grant restricted playback |
| Story suspended | Unavailable and safe alternative | Stop new grants |
| Language unavailable | Clear locale state | No misleading mixed audio/text |

## 6. Publication-to-discovery contract

Stories move through editorial draft, review, approval, publishing and optional takedown. The child catalog is read-only. An editor cannot publish media that has not cleared scanning, rights and completeness checks. Details of states and staff roles belong to [Admin/Editorial](11_Admin_Editorial_and_Content_Operations.md). The catalog service remains authoritative regardless of distributed event timing.

## 7. Acceptance tests

- **CA-AT-01:** Given a suspended story, when using a direct ID or deep link, then neither catalog nor playback returns authorized media.
- **CA-AT-02:** Given a child age band excludes a story, when searching and browsing related stories, then the story never appears.
- **CA-AT-03:** Given a Premium episode on Free, when opening details, then no purchase UI or playable Premium URL is exposed.
- **CA-AT-04:** Given empty search, when clearing filters, then safe catalog entries are restored without lifting adult controls.
- **CA-AT-05:** Given a series with one unpublished episode, when listing episodes, then only eligible published episodes are playable.
- **CA-AT-06:** Given stale cached metadata and a takedown, when a new playback request occurs, then it is denied.
- **CA-AT-07:** Given page results overlap after new publication, when merging pages, then the same story card is not duplicated.

**Pending:** ~50 Free stories at launch, licensed catalog and rights [DEC-001], languages [DEC-007], reviewed catalog merchandising and accessible story metadata. No feature here creates a new public API silently.
