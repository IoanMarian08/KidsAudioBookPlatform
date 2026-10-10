# 07 — Protected Parent Zone and Family Controls

**Actor:** authenticated adult with recent valid Parent Zone verification.
**Requirements:** PRD-06; FR-PR-004/005 and FR-ID-005.
**Service owners:** identity-service for adult security proofs; profiles-service for child restrictions; billing-service for plan management.
**Contracts:** [API Specification](../../03_Architecture/API_Specification.md) sections 21–23; [Security Architecture](../../03_Architecture/Security_Architecture.md).

## 1. Entry, protection and exit

Parent Zone is visually and functionally distinct from the Child World. The entry is recognizable yet not attractive as a game or reward. Its challenge is not a math question a child can easily guess; it uses adult-held PIN or approved security proof with optional OS biometrics. A normal account login is **not** elevated authorization.

**FS-PZ-001** Every sensitive adult route verifies that a recent parent proof is valid for the account, device/session, scope and expiry. A direct API request without this proof must be denied even if a client screen appears unlocked.

**FS-PZ-002** POST /parent-zone/verify checks entered proof with attempt limits, throttling and abuse detection. Error copy does not tell a child how close a guess was. The PIN never appears in logs, analytics or backend error fields.

**FS-PZ-003** PUT /parent-zone/pin and DELETE /parent-zone/pin require the existing authorized parent security flow, with reauthentication as specified by the API. Optional biometric entry depends on secure OS enrollment and must have an approved fallback.

**FS-PZ-004** Exiting Parent Zone discards transient sensitive forms and navigates safely to the selected profile. Parent proof must expire according to security policy; no “keep unlocked forever” option.

**FS-PZ-005** A parent session locked, expired or revoked on another device cannot keep editing protected settings via cached mobile proof.

## 2. Parent Zone navigation

Suggested sections (labels are [ILLUSTRATIVE], final IA belongs to UX):
- Children: create/edit/archive profiles, select age band and avatars, manage eligible categories.
- Listening: bedtime/audio limits, ambient choices, activity/history and downloads.
- Premium: plan comparisons, purchase, restore and current entitlements.
- Account & security: email, password, PIN, active sessions and sign out.
- Notifications: channels, reminders, quiet hours/opt-out.
- Help & privacy: support, notices, data rights and account deletion.

**FS-PZ-006** Every section has clear ownership, save/cancel state, current persisted value and feedback after submission. Navigation away with unsaved changes prompts save/discard as appropriate.

**FS-PZ-007** Parent-only operations cannot be initiated from Child World by manipulating deep links, local storage, backend payloads or stale elevated tokens.

## 3. Child restrictions and listening limits

Available categories may include age range, blocked categories, recommended bedtime material and approved time/listening controls. These are features described in the product intent; exact thresholds and behavior require design/business review.

**FS-PZ-008** For every per-child rule, parent sees a comprehensible control, affected profile, current value and what changing it will impact. Settings cannot be silently applied to all siblings if a single profile was selected.

**FS-PZ-009** PUT /child-profiles/{profileId}/parental-settings persists only for the owned profile. A failed save must revert or clearly indicate pending/unsaved state; no false confirmation.

**FS-PZ-010** Server-side playback/catalog eligibility checks respect current restrictions, and a cached UI view or bookmarked story cannot override a denial.

**FS-PZ-011** Where the app exposes “time limit,” a parent must know whether it counts total listening, time-of-day window, or a session duration; **do not implement an ambiguous universal timer**. Choose exact semantics, timezone behavior, offline enforcement and grace rules before activation.

**FS-PZ-012** For a shared family device, the parent may inspect profile-specific history and download status where privacy policy permits, without confusing activity across siblings.

## 4. Premium and adult-only commercial controls

**FS-PZ-013** Subscription plans, trial eligibility and purchase controls are accessible only in Parent Zone. Billing-service entitlement validation is required after store operations.

**FS-PZ-014** Cancel, manage or restore subscription are explained in adult-friendly language, including the fact that subscription cancellation may be performed through the Apple/Google store and does not necessarily mean immediate loss of already-paid access.

**FS-PZ-015** The parent never sees a child-initiated external checkout or unauthorized subscription-change deep link; all monetary controls respect platform/app store policies.

## 5. Account/privacy and critical confirmations

**FS-PZ-016** Password/PIN updates, account deletion, profile archival and session revocation have explicit adult confirmation and clear result status.

**FS-PZ-017** Account data export/deletion should identify data categories and statutory retention exceptions where required; actual export endpoint and retention window require confirmed policy before implementation. See [Privacy](10_Notifications_Support_and_Privacy.md).

**FS-PZ-018** Parent support requests use approved channels and minimal context; no child can send messages to staff directly from Child World.

## 6. Failure behavior

| Trigger | Safe behavior |
|---|---|
| Invalid or expired PIN | Generic error, retry limit and cooldown |
| Session expires mid-form | Do not save; request sign-in/elevation and preserve safe input only |
| Parent changes restriction during playing story | New authorization follows updated policy; existing-session policy made explicit |
| Another adult account on device | Clear prior proof and data |
| Quota changed after Premium refund | Explain parent-facing impact without deleting child data |
| Offline Parent Zone | Read locally safe state only if policy permits; no claimed writes |
| Store purchase pending | Explain pending; do not grant Premium from client success |
| Account deletion requested | Present confirmed workflow state, not instant deletion |

## 7. Acceptance scenarios

- **PZ-AT-01:** Given a valid normal access token but no parent elevation, when updating parental settings, then API denies it.
- **PZ-AT-02:** Given five wrong PIN guesses (example threshold is NOT specified), when hitting configured limit, then brute-force protection is enforced without leaking the correct PIN.
- **PZ-AT-03:** Given profile A selected, when parent edits only A's age restrictions, then B retains its own independent settings.
- **PZ-AT-04:** Given parent proof expires mid-edit, when Save is pressed, then no setting changes without fresh proof.
- **PZ-AT-05:** Given a child opens a payment deep link, then an adult challenge is required before any transaction screen.
- **PZ-AT-06:** Given profile quota reduced after downgrade, then no data is silently removed and the adult receives a policy-based explanation.
- **PZ-AT-07:** Given the parent exits protected area, then private account values are hidden and the child returns to the selected Child Room.

**OPEN:** parental limit semantics and offline behavior, PIN challenge duration, supported biometrics, profile quotas, paid plan policy, privacy notice/retention. Authoritative details in security and Decision Register.
