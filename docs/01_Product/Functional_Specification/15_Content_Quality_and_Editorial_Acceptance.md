# 15 — Story Content Quality, Safety and Editorial Acceptance

**Actors:** content team, narrators, editors, reviewers, product owner and QA.
**Dependencies:** [Product Bible](../../00_Project/Product_Bible.md), [Illustration Guide](../../02_UX_UI/Illustration_Guide.md), [Catalog/Media blueprint](../../07_Blueprints/02_Catalog_Media.md).
**Goal:** every published item offers a calm, intelligible, age-appropriate narrated experience, not only a valid database record.

## 1. Editorial content entry criteria

Every story submitted for publication must have a known title, locale/language, suitable age band, summary, series/episode placement if applicable, editorial classification, duration, author/narration rights status, approved text, media references and any content advisory relevant to parents. A work-in-progress can omit fields, but a publication-ready revision cannot.

**FS-CQ-001** Editorial review confirms the story is suitable for children ages 0–7 and the declared age band; review should consider frightening content, advertising pressure, discrimination, unsafe instructions and confusing intensity at bedtime.

**FS-CQ-002** The content must respect rights: soundtrack, voice, script, images, fonts and derivative media should have approved license/creator provenance and authorized distribution conditions by country/locale.

**FS-CQ-003** No AI-generated story/audio/image is auto-published; if AI assists editorial preparation, a human approves safety, factual content, rights and publication, consistent with product non-goals.

## 2. Audio acceptance

Narration should have consistent intelligibility, age-appropriate pace and safe sound levels. Loud jumps, startling effects, clipping, abrupt endings and background music masking spoken words are rejected before publication.

**FS-CQ-004** Audio file variants pass technical validation: permitted codec/container, duration consistency, no missing data, checksum, virus scan, no unauthorized embedded metadata, and readiness for signed CDN streaming.

**FS-CQ-005** Stories intended for bedtime should avoid surprising loudness and high-pressure transitions. Ambient mixes and fades must be previewed on representative mobile devices/headphones.

**FS-CQ-006** Changing an audio version after publication requires revalidation of text timing, illustration cues and already-downloaded manifest compatibility.

## 3. Text and illustration acceptance

**FS-CQ-007** Segment text matches the spoken narration sufficiently for meaningful synchronized highlighting; segment start/end times are valid, ordered and within audio duration.

**FS-CQ-008** Illustrations are reviewed for age suitability, consistency with watercolor/rabbit/calm brand direction, contrast with UI text, locale sensitivity and image rights. No unapproved user-submitted image appears in Child World.

**FS-CQ-009** Optional missing illustration never causes inappropriate or unapproved content to appear; the UI uses a safe approved fallback.

**FS-CQ-010** Localized story text, narration, artwork copy and synopsis remain coherent in one approved locale. Unsupported market languages require an explicit content fallback decision.

## 4. Editorial metadata checklist

- Stable story/series/episode ID and revision history.
- Title, description, age band, localization, duration, genre/category and tags.
- Correct Free/Premium classification without leaking source assets.
- Cover art and illustrations with rights and accessibility text as needed.
- Audio approved rendition(s), integrity and safe volume checks.
- Text timeline and image segment timing.
- Editorial author, reviewer and moderation reason.
- Approval, publish date, rights territory and optional rights expiry.
- Search/filter visibility and parent restriction compatibility.
- Content takedown and republication plan.

## 5. Publishing acceptance journey

A new audio story is authored in Draft; media is uploaded through a private short-lived grant; the media worker scans, verifies and transcodes; a reviewer validates text timing, image rights, age band, language and audio quality; a permitted approver accepts; catalog-service publishes an approved revision; child searches/feeds show it only for eligible profiles; an independent playback grant confirms publication and entitlements.

Suspension or rights expiry removes it from new discovery/playback authorizations. A stale CDN/cache or delayed event must not override the current authority.

## 6. Editorial exception matrix

| Exception | Release rule |
|---|---|
| Missing rights evidence | No publication |
| Media scan failed or pending | No publication |
| Text segments overlap incorrectly | Correct before release |
| Wrong audio language | Block incompatible locale rendition |
| Artwork not age-suitable | Replace and reapprove |
| Duration mismatch between audio and metadata | Fix/validate |
| Reviewer lacks permission | Approval denied/audited |
| Scheduled release after rights expiry | Remains unpublished |
| Previously published story suspended | No new grants |
| Processing callback duplicated | No duplicate public rendition |

## 7. Quality scenarios

- **CQ-AT-01:** Given a draft with valid text but unsafe audio scan, when Publish is requested, then no public record grants streaming.
- **CQ-AT-02:** Given a 180-second audio with a text segment ending at 220 seconds, then review rejects timing until corrected.
- **CQ-AT-03:** Given locale-specific narration missing, when story detail is requested in that locale, then fallback is explicit and consistent with approved policy.
- **CQ-AT-04:** Given content rights expire between approval and scheduled publication, then the schedule does not publish it.
- **CQ-AT-05:** Given published media is suspended, then new playback grants are denied even when an older card is cached.
- **CQ-AT-06:** Given editor submits the same asset event twice, then the media worker creates one logical processed version.
- **CQ-AT-07:** Given a story revision replaces audio, then synchronization and downloads are revalidated against correct version.
- **CQ-AT-08:** Given an unauthorized editor attempts approval, then permission is denied and an audit event is produced.

**OPEN:** exact initial story inventory, rights clearance process, accepted age-suitability rubric, languages/territories, approved audio loudness targets and external creator contracts. These require explicit Content/Product/Legal acceptance before first release.
