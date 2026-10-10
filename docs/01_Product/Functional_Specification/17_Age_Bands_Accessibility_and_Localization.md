# 17 — Age-Band Behavior, Accessibility and Localization

**Product audience:** children from infancy through age seven and their adult caregivers.
**Status:** Inclusion and content interaction requirements; specific country/language and accessibility audit criteria need Product/Design approval.
**References:** [Product Bible](../../00_Project/Product_Bible.md) audience and accessibility sections; [UX Guidelines](../../02_UX_UI/UX_Guidelines.md), [Typography](../../02_UX_UI/Typography.md) and [Illustration Guide](../../02_UX_UI/Illustration_Guide.md).

## 1. Age bands are content-suitability guidance, not identity verification

The age-band experience is a way to curate and present content appropriate to developmental abilities, not a substitute for adult supervision or legal consent. In particular, the youngest children should never be expected to read, navigate alone or manage settings.

**FS-AG-001** Every child profile uses approved age-band representation and avoids collecting exact date of birth unless necessary and legally approved [DEC-008]. Changing the band re-evaluates catalog eligibility and parent settings.

**FS-AG-002** Age classification is enforced in the backend and includes both content-level metadata and profile-specific parental restrictions. A child cannot turn age filters off through search, deep links or local cache modification.

## 2. Age-band experience guidance

| Audience | Expected interaction | Content/presentation guidance | Parent role |
|---|---|---|---|
| 0–2 | Primarily adult-mediated playback; visual recognition more relevant than independent tasks | Gentle pacing, strong simple shapes, calm narration and predictable endings | Parent chooses content, volume, device and listening duration |
| 3–4 | Large tap targets, recognizable category images, minimal reading | Simple stories, limited choices per screen, short labels, clear cause/effect | Parent establishes profiles, settings and transitions |
| 5–7 | More independent browse, beginning-reading support, accessible synchronized text | Editorial story sequences, series, age-suitable exploration without algorithmic pressure | Parent retains all commerce, privacy and content authority |

These groupings are *design guidance*, not claims about an individual child's abilities. Allow parental oversight and accessibility settings regardless of age.

**FS-AG-003** Navigation MUST be possible without reading every word. Approved artwork, voice hints (if supported), labels and simple buttons guide pre-readers without turning the product into a toy-like maze.

**FS-AG-004** Content descriptions and images avoid startling imagery, intense unexpected audio and manipulative engagement mechanics. The bedtime context is particularly sensitive to sudden brightness or volume changes.

**FS-AG-005** The rabbit mascot encourages calm exploration; it does not shame inactivity, advertise subscriptions or act as an unsupervised conversational companion.

## 3. Screen readers and semantics

**FS-AC-001** All interactive controls have stable accessible names, actionable roles and meaningful state (selected, loading, disabled, expanded). Decorative drawings/animations must not steal screen-reader focus.

**FS-AC-002** Logical focus order follows the screen's primary task, not arbitrary view-tree order. Closing a dialog returns focus to its opener unless the action navigates deliberately.

**FS-AC-003** Dynamic updates such as progress errors, purchase pending/verified, file download Ready and profile switch should announce status nonintrusively; do not repeat announcements every second of the player clock.

**FS-AC-004** Playback must be controllable from accessibility services as well as visible buttons. Seeking, pause, narration speed if supported and synchronized text must expose a usable alternative to precise drag gestures.

**FS-AC-005** Contrast, scalable fonts, platform display size and portrait/landscape behavior are tested against the selected design system and target device range. Large text must not hide essential Parent Zone confirm/cancel buttons.

**FS-AC-006** Color alone never communicates Premium eligibility, progress completion, error, selection or content age-band. Icons/text/accessible announcements must accompany semantic colors.

## 4. Motion, sensory and audio accommodations

**FS-AC-007** Respect OS reduce-motion settings: static backgrounds and controlled transitions must preserve the same task flow as animated themes.

**FS-AC-008** Avoid flashing effects, unexpected audio stingers and simultaneous narration/ambience levels that mask speech or produce uncomfortable jumps.

**FS-AC-009** Background/lock-screen playback and headphone controls must continue to support OS media accessibility, including paused state after interruptions.

**FS-AC-010** Optional text highlighting and image changes must remain understandable when animation is off or illustrations are unavailable. Spoken narration stays the central story experience.

## 5. Localization model

Localization encompasses child-facing prompts, adult settings, subscription disclosures, legal text, content title/description, story narration/text segments, image text and notification templates.

**FS-LO-001** Each localized story must have an explicit language/locale identity. Mismatched narration and text cannot be silently offered as a fully localized experience.

**FS-LO-002** Missing translation may use a Product-approved fallback with clear language labeling. Legally meaningful pricing/consent/cancellation language must not silently fall back to an inaccurate translation.

**FS-LO-003** Date/time display and editorial schedule respect chosen timezone rules; subscription price/currency comes from authoritative storefront data, never calculated from the device's text locale.

**FS-LO-004** Right-to-left support, pluralization, decimal separators, age-range formatting and text expansion must be evaluated for actual launch locales [DEC-007], not assumed solved by swapping strings.

**FS-LO-005** Search matches approved localized metadata; do not display a story title in one language and stream a different unsupported-language asset without an explicit choice.

**FS-LO-006** Notification copy, email verification and support links use an approved locale/policy; a deep link still enforces current authorization and profile ownership.

## 6. Device and content matrix for QA

| Scenario | Expected outcome |
|---|---|
| Screen reader + profile selection | Every avatar and name read with correct select action |
| Large font + Parent Zone billing | Price and terms visible without clipping crucial confirm controls |
| Reduced motion + Child Room | Static version supports all browsing and player routes |
| Offline + selected locale | Valid downloaded localized rendition remains correctly labeled |
| Child profile age change | Catalog re-filtered; cached disallowed content not playable |
| Story locale missing text segment | No false synchronized reading claim; approved fallback or unavailable |
| Device locale changes | Adult legal/store copy remains accurate and approved |
| High contrast + progress | Position/state not represented only by a colored line |
| Headset/media controls | Pause/seek states remain synchronized with playback |
| Admin language variant | Publishing rejects mismatched required rights/audio/text |

## 7. Acceptance tests

- **AG-AT-01:** Given an age band change, when story permissions are refreshed, then disallowed direct links cannot start playback.
- **AG-AT-02:** Given a pre-reading child, then common browse/Play/Back tasks remain recognizable without requiring fluent reading.
- **AC-AT-01:** Given reduced motion, when entering Child Room, then all navigation and player actions remain accessible.
- **AC-AT-02:** Given large dynamic type, when opening protected Parent Zone forms, then no mandatory control is lost or clipped.
- **AC-AT-03:** Given screen reader, when a request fails validation, then field error and recovery action are announced.
- **AC-AT-04:** Given playback interrupted, when an accessibility control resumes it, then displayed status matches actual audio.
- **LO-AT-01:** Given story narration exists only in locale A, when user requests locale B, then the app does not falsely identify that narration as B.
- **LO-AT-02:** Given a legal purchase disclosure in an unsupported language, then the purchase journey follows approved store requirements rather than silently inventing translated terms.
- **LO-AT-03:** Given a localized series with one missing episode, then visible episode list does not offer an unapproved rendition.

## 8. Product and delivery decisions

DEC-007 decides launch countries, languages and consent requirements; DEC-008 decides age-data minimization; DEC-010 finalizes licensed brand assets and fonts; DEC-012 supported OS versions; DEC-018 editorial age-quality rubric. UI/design review must confirm objective platform accessibility evidence before launch.
