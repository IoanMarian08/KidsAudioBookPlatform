# 13 — Complete Screen Inventory and UX Handoff

**Status:** User-visible screen requirements; exact visual placement and copy remain subject to design approval.
**Use:** Figma/Flutter/Admin handoff, QA screen checklist and route planning.
**Source:** Product Bible, [Design System](../../02_UX_UI/UI_Design_System.md), chapters 01–12 of this specification.

## 1. Screen definition contract

Every screen handoff MUST identify (a) ID and user role, (b) route/entry and safe exit, (c) visible data and required controls, (d) valid and invalid actions, (e) loading/empty/offline/error/forbidden state, (f) accessibility/localization requirements, (g) existing API owner and (h) acceptance scenarios. Do not invent public API methods from screen names.

Screens may be combined into one Flutter route only if the resulting experience retains all controls and access restrictions. A modal is still a user-visible state and needs error/keyboard/escape behavior.

## 2. Onboarding / adult identity screens

| ID | Screen | Fields and primary actions | Special states |
|---|---|---|---|
| SCR-ID-01 | Welcome/first launch | App value, continue, sign in/create account, legal links | Offline intro, screen-reader reading order |
| SCR-ID-02 | Register | Email, password, reveal toggle, notices, submit | Invalid input, duplicate-safe response, submission pending |
| SCR-ID-03 | Verify contact | Verification code/link progress, resend | Expired, replayed code, resend cooldown |
| SCR-ID-04 | Sign in | Email, password, show/hide, Forgot Password | Rate limit, bad credentials, suspended session |
| SCR-ID-05 | Request password reset | Contact input and submit | Enumeration-safe response, delivery pending |
| SCR-ID-06 | Set new password | Reset proof, new password, confirm | Expired token, policy failure, already used |
| SCR-ID-07 | Account settings | Current verified identity, edit supported fields | Elevation for sensitive changes; conflict |
| SCR-ID-08 | Sessions | Active/recent sessions, revoke one/all | Device not found, current session revoked |
| SCR-ID-09 | Logout confirm | Sign out / cancel | Clear private state and cached proof |

**Handoff notes:** Registration and recovery do not use child illustrations to solicit child data. Keyboard navigation must work with a screen reader, autofill must not expose password in logs, and a pending server action must not be falsely marked complete.

## 3. Profile and Child Room screens

| ID | Screen | Primary content/actions | Special states |
|---|---|---|---|
| SCR-PR-01 | Select child | Profile avatars, name, choose, protected add/settings entry | No profiles, stale/archived profile, offline |
| SCR-PR-02 | Create/edit profile | Nickname, approved age band, avatar, preferences | Quota, required field, ownership, unsaved changes |
| SCR-PR-03 | Profile archive/delete | Impact summary, confirm/cancel | Requires adult proof, retention notice |
| SCR-PR-04 | Child Room | Personal background, mascot, Continue, recommended collections | Empty recommendations, connectivity, restrictions |
| SCR-PR-05 | Customize room | Approved theme/animal/color choices | Missing asset, preview vs saved |
| SCR-PR-06 | Profile parental settings | Age/category/audio restrictions, save/cancel | Validation, proof expiry, conflict |

**Handoff notes:** Profile selection is not a credential request. Switching siblings is an atomic visual privacy event; no transient old-avatar and new-progress mixture is acceptable. The room has a static equivalent for reduced motion.

## 4. Catalog and storytelling screens

| ID | Screen | Primary content/actions | Special states |
|---|---|---|---|
| SCR-CA-01 | Story catalog | Published story cards, categories, selected filters | Loading, no content, pagination, unavailable |
| SCR-CA-02 | Search | Search box, results, clear query, approved filters | Empty match, network offline, invalid query |
| SCR-CA-03 | Category/collection | Title, approved ordered story cards, back | No eligible cards, filtered age results |
| SCR-CA-04 | Series detail | Series metadata, ordered eligible episodes | Missing/archived episode, localized availability |
| SCR-CA-05 | Story/episode detail | Art, description, age/duration/locale, Play, Favorite, Download | Premium item, pending media, suspended story |
| SCR-PL-01 | Story player | Play/Pause/Seek/Exit, audio title, text/illustration, ambience | Buffering, expired grant, completion, background |
| SCR-PL-02 | Synchronized reading | Current segment, accessible text, approved illustration | Missing image, seek, speed change |
| SCR-PL-03 | Ambient sounds | Approved sounds, start/stop/loop/safe level | Track unavailable, audio focus, timer |
| SCR-PL-04 | Player completion | Confirmed completion, replay, next eligible story, back | Pending server sync, next unavailable |

**Handoff notes:** All player controls are finger-friendly, screen-reader labeled and workable without animation. Any “next” action must verify age/locale/entitlement. Sound level never jumps because two media tracks start together.

## 5. Personal library and offline screens

| ID | Screen | Primary content/actions | Special states |
|---|---|---|---|
| SCR-OF-01 | Favorites | Selected profile's approved saved stories, remove, open | Empty, story suspended, pending favorite |
| SCR-OF-02 | Continue Listening | Partial stories, current position, resume | Empty, stale progress, content unavailable |
| SCR-OF-03 | Listening history | Completed/listened items, approved removal | Empty, remove pending, profile ownership |
| SCR-OF-04 | Download library | Device-authorized items, transfer status, remove | Storage full, expired, unavailable, offline |
| SCR-OF-05 | Download progress | Progress, cancel, retry, integrity verification | Failed checksum, interrupted background |
| SCR-OF-06 | Offline sync status | Simple synchronization status and recovery | Conflicts, retry queue, no connectivity |

**Handoff notes:** A downloaded item is Ready only after integrity and valid offline rights, not after a progress bar reaches 100%. Never display profile A's local downloaded media title to profile B without approved ownership.

## 6. Protected parent screens

| ID | Screen | Primary content/actions | Special states |
|---|---|---|---|
| SCR-PZ-01 | Parent Zone challenge | PIN/adult proof, verify, cancel | Invalid, locked, proof expired |
| SCR-PZ-02 | Parent home | Children, listening, subscriptions, notices, account, privacy | Session/elevation expired |
| SCR-PZ-03 | Child control details | Age/content/bedtime limits, save/cancel | Unsaved change, conflict, restriction revalidation |
| SCR-PZ-04 | Security/PIN | Set/change/remove PIN, OS biometric option | Existing proof, lockout, unavailable biometric |
| SCR-PZ-05 | Plan comparison | Available Free/Premium plans, period/price/terms | Unsupported storefront, trial unavailable |
| SCR-PZ-06 | Store purchase result | Native purchase outcome, server verification | Pending, denied, timeout, active |
| SCR-PZ-07 | Subscription management | Current verified plan, expiration/renewal, restore/manage | Refund, grace, canceled renewal |
| SCR-PZ-08 | Notification preferences | Categories, channels, quiet hours where approved | Pending save, provider unavailable |
| SCR-PZ-09 | Device/download controls | Current devices, remove/revoke controls | Old device, unknown grant |
| SCR-PZ-10 | Help/support | FAQ, contact form, safe diagnostics | Failure, timeout, ticket queued |
| SCR-PZ-11 | Privacy and notices | Data categories, rights explanation, approved links | Unsupported locale, consent update |
| SCR-PZ-12 | Deletion confirmation/status | Request, consequence, cancel when allowed, state | Partial saga, completed, legal exceptions |

**Handoff notes:** Parent Zone must be recognizable and protected in navigation and API, with appropriate terms for app-store changes. A plain user token does not authorize elevated writes. No sensitive destructive action is one accidental tap.

## 7. Administrative web screens

| ID | Screen | Data and actions | Security/error cases |
|---|---|---|---|
| SCR-AM-01 | Admin sign in / shell | Scoped navigation, staff account, roles | Denied role, session expiry |
| SCR-AM-02 | Content index | Filter story/review status, create/open | Paged data, permission denial |
| SCR-AM-03 | Story editor | Draft fields, locale, age/category, preview, save | Field errors, optimistic conflict |
| SCR-AM-04 | Series/collection editor | Episode ordering and membership | Missing/unauthorized content |
| SCR-AM-05 | Asset upload/processing | Request grant, upload, scan/transcode status | MIME reject, malware, failed job |
| SCR-AM-06 | Review queue | Submitted revisions, approve/reject reasons | Role separation, revision changed |
| SCR-AM-07 | Scheduling/publishing | Approved readiness, date, publish, suspend | Timezone, rights expiry, takedown |
| SCR-AM-08 | Accounts and support | Authorized accounts, suspend, force logout, notes | Least-privilege and audit |
| SCR-AM-09 | Subscriptions | Provider truth, reconcile, tightly scoped override | Pending, refund, no authorization |
| SCR-AM-10 | Notifications/campaigns | Create, preview, schedule, cancel | Consent mismatch, unauthorized send |
| SCR-AM-11 | Audit and exports | Filtered access-controlled records | Pagination, retention, access denial |
| SCR-AM-12 | Operational exceptions | Processing, publication or delivery failures | Retry/DLQ under owning service policy |

## 8. Unified layout behavior

Every screen specifies safe Back/Close, focus return after modal close, keyboard escape on desktop, cancel/pending mutation and a persistent explanation of unexpected failures. Empty states should allow a meaningful next action; endless loading spinners are not acceptable without timeout/retry.

For parent fields, accessible validation can identify a problematic field without revealing whether an email exists or whether a PIN guess was close. Sensitive values must not remain visible behind OS app switcher if security policy requires shielding.

## 9. Implementation handoff record template

For each screen use a lightweight record:

- Screen ID / approved Figma link / UX owner.
- Actor, entry/exit and Parent Zone requirement.
- Data shown, empty/loading/error variants, control list.
- Validation, destructive confirmations, accessibility and localization.
- Related FS/FR/PRD IDs and Given/When/Then cases.
- Existing API operation + owning microservice or explicit contract gap.
- Event/analytics data minimization and QA completion evidence.

**Release rule:** Screens are approved based on user tasks and security coverage, not pixel count. Labels/copy must be reviewed per intended market and age band.
