# UI Design System

Version: 2.0.0  
Status: Implementation baseline; final visual tokens require approved design review  
Owner: UX/UI and Mobile Engineering

## 1. Purpose and principles

KidsAudioBookPlatform combines a calm **Child World** and a clear, protected **Parent Zone**. Both use the same token infrastructure but distinct layout density, navigation, wording and interaction affordances. Do not make purchasing or security flows look like child games.

Primary principles: calm by default, recognizable actions, predictable navigation, touch-first controls, accessibility, offline-aware feedback, lightweight media, and consistent empty/loading/error states.

## 2. Token hierarchy

Theme tokens use semantic names, never hardcoded widget-level colors. Source of truth is [Colors](Colors.md) and [Typography](Typography.md). Preferred layering:

~~~text
primitive: color.midnight.900, spacing.4, radius.3
semantic: surface.primary, text.primary, action.primary
component: storyCard.surface, parentZone.action
context: child.day, child.night, parent
~~~

Create matching Flutter ThemeExtensions and design-tool variables. UI widgets consume semantic tokens only; theme switches must not require asset rewrites.

## 3. Responsive foundations

Use logical pixels and platform text scaling. Layouts must handle compact phones, tablets, portrait and landscape as supported. Safe areas, notches, keyboards, screen readers and OS navigation bars require tests. Do not position essential controls using raw screen percentages.

Spacing scale proposal: 4, 8, 12, 16, 24, 32, 40, 48 logical pixels. Radius scale proposal: 8, 12, 16, 24. These are design tokens, not global requirements to override platform accessibility.

## 4. Component catalog

| Component | States | Requirements |
|---|---|---|
| Story card | loading, ready, premium, offline, disabled | Cover, age/locale cues and an obvious play action |
| Series card | empty, episodic, completed | Episode count/status without clutter |
| Playback transport | paused, playing, buffering, error | Large play/pause, accessible seek, non-blocking audio |
| Download badge | queued, running, ready, failed, expired | Explicit state and retry guidance |
| Profile switcher | current, selectable, locked | No cross-profile information leakage |
| Child bottom navigation | active, inactive | Few clear destinations; avoid hiding Parent Zone entry |
| Parent form | untouched, invalid, pending, success | Labels persist; errors adjacent; safe keyboard behavior |
| Parent challenge | prompted, locked, expired, verified | Accessible explanation, rate limits and session expiry |
| Toast/banner | info, warning, error, success | Non-alarming copy, accessible announcements |

## 5. Screen states

Every data screen MUST define: initial loading, slow connection, empty valid result, recoverable error, permission denied, expired session and offline with/without cached content. Skeletons should match final layout dimensions to minimize jumps.

During buffering, audio controls remain visible. A failed story artwork request must never make playback inaccessible.

## 6. Child home and Parent Zone

Child home prioritizes continue listening, recommended curated collections, appropriate categories and time-of-day backgrounds. Avoid endless feeds and engagement loops. Parent Zone uses standard form/navigation conventions and clear pricing, consent, safety and privacy disclosures.

Time-of-day backgrounds may use morning/afternoon/evening/night palettes but respect device reduced-motion and low-power settings. Child preferences may override time-driven changes where supported.

## 7. Accessibility and localization

- Screen-reader semantic names for interactive elements; visual ornamentation is excluded from reading order.
- Touch targets should meet a platform-appropriate accessibility minimum; target 48 logical pixels for prominent child actions.
- Do not encode premium/disabled/error state only by color.
- Text must scale without clipping; support right-to-left layout if a locale is approved.
- Honor reduced-motion and high-contrast settings.
- Text strings come from localization resources, not widget constants.

## 8. Engineering handoff and design QA

Each component spec includes token names, constraints, states, interactions, accessibility annotations, analytics/privacy notes and golden screenshots. Changes to shared tokens trigger visual regression checks of child and parent screens.

Related: [UX Guidelines](UX_Guidelines.md), [Animations](Animations.md), [Product Bible](../00_Project/Product_Bible.md), [Mobile Architecture](../03_Architecture/Mobile_Architecture.md).
