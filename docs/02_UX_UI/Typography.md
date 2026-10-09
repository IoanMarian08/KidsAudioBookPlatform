# Typography

Version: 2.0.0  
Status: Design baseline  
Owner: UX/UI

## 1. Type direction

Per the Product Bible: **Nunito** for general UI, **Baloo 2** (or approved rounded alternative) for selected display titles, and **Atkinson Hyperlegible** (or approved accessibility-first alternative) when long reading warrants it. Font licensing, glyph availability and app-bundle impact must be reviewed before final selection.

## 2. Functional hierarchy

| Token | Proposed baseline (logical px / line-height) | Usage |
|---|---|---|
| display.large | 32 / 40, semibold | Child section entry, sparingly |
| heading.large | 26 / 34, bold | Screen titles |
| heading.medium | 22 / 30, semibold | Story detail headings |
| title.medium | 18 / 26, semibold | Cards and modal headings |
| body.large | 17 / 26, regular | Child guidance and controls |
| body.medium | 16 / 24, regular | Parent forms and descriptions |
| body.small | 14 / 21, regular | Supporting information |
| caption | 13 / 18, medium | Metadata with adequate contrast |

These are starting tokens; OS text scaling and accessibility overrides are mandatory.

## 3. Reading-specific typography

Synchronized story text should support:
- optional large readable layout for emerging readers;
- clear paragraph and sentence highlighting without flashing;
- text selection only when meaningful; no accidental navigation;
- semantic grouping for screen readers;
- predictable punctuation and locale-specific line breaks;
- playback sync based on audio timestamps, never CSS-like animation timing.

Avoid overusing all caps, tightly tracked characters, decorative fonts for paragraphs, or text embedded inside illustrations. For ages 0–2, text is primarily parent-supported rather than a child interaction requirement.

## 4. Parent Zone

Parent Zone uses explicit form labels, accessible field hints, visible validation errors and standard OS text behavior. Prices, dates, subscription conditions and privacy notices must remain legible at large text scales. Never compress critical legal text to fit one screen.

## 5. Localization and scripts

Localization tests must include long German-like expansion, Romanian diacritics, punctuation, mixed-digit formatting, unknown glyph fallback and RTL if supported. Store copy in translation catalogs, never flatten strings into raster images. VoiceOver/TalkBack should read meaningful labels independent of visual capitalization.

## 6. Flutter implementation guidance

Use TextTheme + ThemeExtensions; avoid creating TextStyle instances with arbitrary font sizes in every widget. Respect MediaQuery text scale / TextScaler. Test keyboard, navigation and bottom sheets at maximum supported sizes. Use consistent fallback fonts for unsupported scripts and offline assets.

## 7. Quality checks

- No truncation of child-facing primary action labels at large scale.
- Headings wrap without overlap.
- Contrast passes [Colors](Colors.md) requirements.
- Synchronized text stays readable during seek/pause.
- Correct diacritics and Unicode normalization.
- Parent form labels remain visible after input.
- Visual snapshots and accessibility audits pass on representative phones and tablets.

Related: [Design System](UI_Design_System.md), [Illustration Guide](Illustration_Guide.md).
