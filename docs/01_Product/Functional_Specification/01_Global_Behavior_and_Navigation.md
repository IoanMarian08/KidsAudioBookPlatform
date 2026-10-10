# 01 — Global Behavior, Navigation and Shared Experience

**Actors:** adult account holder, selected child profile, authorized editorial/support staff.
**Relevant source:** Product Bible sections 5–11, 21–25; [UX Guidelines](../../02_UX_UI/UX_Guidelines.md), [User Flows](../User_Flows.md).

## 1. Two worlds, never two kinds of purchasing account

Child World includes Child Room, safe discovery/search, story details, player, favorites, continue listening and eligible downloads. Parent Zone includes profile management, security, restrictions, subscription, notification preferences, privacy and support. The parent is the authenticated principal in both; the child profile selects context only.

**FS-GL-001** Child World MUST never expose billing actions, payment links, invoices, deletion of family accounts, unrestricted messaging, external unapproved URLs or staff tools. Hiding UI is insufficient; direct API/deep-link attempts must fail.

**FS-GL-002** Every profile-specific request is checked against the authenticated adult account, regardless of locally selected profile. Every sensitive parent mutation requires valid Parent Zone proof.

**FS-GL-003** On app start the client determines session validity, saved profile context, connectivity, approved local media rights and pending changes. It must not show data belonging to a previously logged-in account while restoring state.

## 2. Navigation and entry points

Main path: Splash/session restoration -> Adult register/login (when needed) -> Child profile selection -> Child Room -> browsing, search, details, player, favorite or download. The dedicated Parent Zone entrance always begins a new verification decision unless the existing elevated proof is still valid. The protected zone has an explicit safe exit to Child World.

**FS-GL-004** After navigating back from a story, the app returns to the same profile-specific list or collection when feasible; repeated taps cannot generate duplicate mutations.

**FS-GL-005** Switching child profile invalidates or reauthorizes an active playback session and clears former sibling's private lists and overlays before showing the new profile.

**FS-GL-006** Deep links from notifications, series, favorites or bookmarks require fresh authentication and eligibility checks. Expired or foreign profile links lead to safe neutral navigation, not sensitive data.

**FS-GL-007** On adult logout or account change, clear access tokens, parent proof, selected profile, private imagery/list state and unapproved offline access. Never reuse private screens for another parent.

## 3. Common screen behavior

| State | What the user sees | Allowed action and invariant |
|---|---|---|
| Loading | Calm progress indicator or skeleton; controls avoid duplicate writes | Wait/cancel/back safely |
| Empty favorites/history | Gentle illustration and route to browse | Never fill with sibling data |
| No matching search | Clear filters / browse categories | Do not broaden to blocked content |
| Offline | Persistent but nonintrusive connectivity signal | Locally licensed downloads may function |
| Network failure | Retry with preserved non-sensitive input and player position | Never say an operation succeeded before confirmation |
| Authorization required | Parent challenge; child-safe route | Server must deny unauthenticated writes |
| Expired login | Adult sign-in; private content hidden | Revoke/clear stale local authority |
| Unavailable/suspended story | Calm explanatory screen; suggested safe alternative | No new media grant |
| Storage full | Download resolution and cleanup options | Server progress remains intact |
| Unknown failure | Safe Back / Help | No stack trace, tokens or raw database IDs |

**FS-GL-008** Errors MUST be understandable without blame or fear, never imply that Premium or deletion succeeded when the server outcome is unknown, and never expose internal credentials.

**FS-GL-009** Buttons and screen-reader semantics MUST be usable with scalable text and reduced motion. No animation, flashing, or mascot performance may block navigation, reading or playback.

**FS-GL-010** The UI respects approved language/locale and accessible contrast. Language sets, legal translations and fallback rules are pending [DEC-007]; no automatic translation of legally meaningful paid/consent copy without approval.

## 4. Device and session interruptions

**FS-GL-011** Incoming call, OS audio focus change, headphone disconnection and background transition follow documented player behavior. The app saves a recoverable position without making duplicate completion claims.

**FS-GL-012** Rapid repeated taps, retries and foreground/background switches cannot duplicate purchase, parental control, media upload or deletion side effects; backend idempotency governs committed changes.

**FS-GL-013** Device time determines optional local background atmosphere only. It does not authorize age, content, trial, advertisement, entitlements or legal jurisdiction.

**FS-GL-014** Local notification previews and logs contain no child name, listening transcript, raw receipt, PIN or privileged URL. Product analytics are purpose-bound and privacy-minimized.

## 5. Child-safe copy and visual intent

Child World copy SHOULD be short, friendly, clear and non-transactional. Examples [ILLUSTRATIVE]: “Choose a story,” “This story isn't available right now,” “Let's try again.” Parent Zone may use explanatory forms, but must identify irreversible or paid operations before confirmation. The rabbit mascot never pressures the child through time-limited rewards, losing streaks or purchase urgency.

Motion should be calm and reduce automatically when operating-system reduced-motion preferences are enabled. No app function should depend on color alone or precise gestures.

## 6. Quality scenarios

- **GL-AT-01:** Given parent A has profile A1 selected, when parent B signs in on the same device, then the app never shows A1's progress or profile imagery under B.
- **GL-AT-02:** Given a child opens a notification deep link to Parent Zone, when no valid elevation exists, then the adult challenge is required and direct mutation is denied.
- **GL-AT-03:** Given the app is offline, when opening search, then it distinguishes unavailable online search from an actually empty catalog.
- **GL-AT-04:** Given reduced motion and screen reader enabled, when opening and leaving the player, then all main controls have names and remain usable.
- **GL-AT-05:** Given an unavailable story was cached before takedown, when Play is tapped, then no new media grant is issued.
- **GL-AT-06:** Given a pending action times out, when Retry is offered, then it cannot accidentally repeat an irreversible operation.

**Implementation ownership:** Flutter owns navigation and device state; identity-service, profiles-service, catalog-service, playback-service and billing-service own their respective decisions. API Gateway does not replace downstream authorization.
