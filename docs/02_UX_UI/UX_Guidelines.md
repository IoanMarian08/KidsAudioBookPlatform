# UX Guidelines

Version: 2.0.0  
Status: Active baseline  
Owner: Product Design and Mobile

## 1. Experience principles

The target product is a safe, calm, predictable listening world for children ages 0–7 and a transparent control panel for adults. Successful UX minimizes instruction, reduces cognitive load, preserves trust and avoids monetization pressure directed at children.

## 2. Child World

- Large recognizable story cards and controls, minimal nested navigation.
- Support parent-led 0–2 usage; simpler choices for 3–4; broader discovery and optional text for 5–7.
- Content is curated and age/locale filtered before display.
- Resume and recently enjoyed content appear without exposing another sibling's history.
- Bedtime mode favors muted colors, gentle visuals and no autoplay surprises.
- Pause/stop/play are always discoverable, including during buffering or offline.
- Errors explain what to do next in neutral, reassuring language.

## 3. Parent Zone

Account, billing, consent, analytics/privacy, downloads, age controls and notifications belong behind parent verification. The screen uses predictable adult conventions: persistent labels, human-readable pricing and dates, confirmation for destructive actions, accessible error summaries and no manipulative upselling.

A deep link, external notification, hardware back button or reused widget state must never bypass the parental gate. Server remains authoritative.

## 4. UX state matrix

| Situation | Child view | Parent view |
|---|---|---|
| Slow connection | Story cards skeleton or familiar cached content | Status and retry |
| Offline, download exists | Available downloads shown | Clear storage/expiry information |
| Offline, no content | Calm offline explanation | Troubleshooting path |
| Premium story | Simple label; no direct payment | Transparent plans/restore |
| Unpublished/removed | Content not accessible | Help text if previously purchased |
| Profile switch | Replace personalized state immediately | Management requires parent rights |
| Error while playing | Keep controls, offer retry or downloaded option | Support reference/correlation ID |
| Failed purchase | No premium false-success | Verify/reconcile/cancel status |

## 5. Navigation

Maintain clear Child World <-> Parent Zone boundary. Child experience should not accumulate multi-step forms. Preserve current story/player state where reasonable on route changes. Navigating back should never reveal a different profile's cached material. Use short-lived confirmations for irreversible operations (delete profile/account).

## 6. Content and language

Child copy: short, warm, concrete, non-alarming. Parent copy: direct, transparent, precise; especially for trials, recurring billing, renewals and cancellations. Avoid guilt, countdown manipulation, deceptive scarcity and pressure. Translate meaning, not literal English phrasing.

## 7. Accessibility and inclusion

- Test text scaling, semantics, contrast, reduced motion, high contrast and keyboard/screen-reader operation in Parent Zone.
- Large touch areas for child play controls; avoid drag-only essentials.
- Provide textual alternatives for meaningful images and synchronized transcripts where available.
- Support diverse family situations, names and appearances without assumptions.
- Respect night mode preferences and interruptions by other audio apps.

## 8. Privacy-centered analytics

Measure feature health through privacy-minimized, aggregated events: first-play success, buffering, retry, session crash, download failure and navigation friction. Avoid behavioral profiling of individual children for advertising or manipulative engagement.

## 9. Design acceptance tests

Each core screen is reviewed on representative Android/iOS devices for: initial state, empty state, errors, offline, interrupted audio, large text, screen reader, night mode, reduced motion, profile isolation and Parent Zone authorization. No P0 release without a child-safety route audit.

Related: [User Flows](../01_Product/User_Flows.md), [UI Design System](UI_Design_System.md), [Product Bible](../00_Project/Product_Bible.md).
