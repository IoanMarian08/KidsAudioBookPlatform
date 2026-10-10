# 02 — Adult Onboarding, Identity and Account Lifecycle

**Primary actor:** adult account holder; no child self-registration.
**Traceability:** PRD-01; FR-ID-001..005.
**Service:** identity-service.
**Contract authority:** [API Specification](../../03_Architecture/API_Specification.md) sections 14–21 and [Error Catalog](../../03_Architecture/Error_Catalog.md).

## 1. First-run experience

The initial screen explains safe, curated narrated stories and protected parent controls. Adults can Sign up or Sign in, open legal notices, and skip nonessential introduction slides. It does not encourage a child to supply email, real name or date of birth.

**FS-ID-001** Session restoration distinguishes signed-out, verification pending, authenticated, expired, suspended and deletion-pending account states. An expired state hides previously private information before requesting reauthentication.

**FS-ID-002** Consent, legally required parental information, allowed market and adult eligibility are set by approved launch-country policies [OPEN: DEC-007/008]. A consent checkbox is never pre-checked.

## 2. Registration and email verification

Elements: email field, password with show/hide, approved terms/privacy links, submit, sign-in route, meaningful per-field errors and progress feedback.

**FS-ID-003** Validate mandatory fields, email formatting, password policy and cooldown in the client for convenience, but enforce independently in backend with safe throttling.

**FS-ID-004** POST /auth/register starts adult identity registration; verification state is explicit. Duplicate or unknown-email responses follow an account-enumeration-safe policy, not an error that reveals credentials or identity.

**FS-ID-005** POST /auth/email-verification/confirm accepts only a valid unexpired, single-use code or link. Resend uses /auth/email-verification/resend with cooldown/rate limits. A token must not verify twice.

**FS-ID-006** On verification success the adult is routed to household setup; on failure show a neutral retry or resend path. Losing a network response must not create duplicate accounts on replay.

## 3. Sign in, sessions and logout

**FS-ID-007** POST /auth/login accepts adult credentials and yields an authenticated session; the client stores tokens only through secure OS-supported storage. Do not use plain user preferences or log credentials.

**FS-ID-008** Invalid login returns neutral feedback; do not disclose whether the email or password was wrong. Repeated failures are throttled while preserving accessible recovery paths.

**FS-ID-009** POST /auth/refresh rotates the refresh credential; stale/reused credentials are refused per [JWT/refresh strategy](../../00_Project/ADR/ADR-0005-jwt-refresh-token-strategy.md). A valid access token is not a valid Parent Zone proof.

**FS-ID-010** POST /auth/logout revokes the current session; POST /auth/logout-all revokes relevant adult sessions. GET /sessions and DELETE /sessions/{sessionId} allow viewing/revocation of the parent's own sessions, never another account's devices.

**FS-ID-011** A resumed app can skip normal sign in for a valid account session, but MUST still require separately scoped recent elevation before sensitive settings or purchases.

## 4. Password recovery

A Forgot Password entry invokes POST /auth/password-reset/request, then /confirm.

**FS-ID-012** Recovery-request response MUST not reveal whether an email belongs to an account. Requests are throttled; single-use reset tokens expire and replay attempts fail.

**FS-ID-013** Reset links must resolve to trusted app/web routes, never arbitrary redirects; new password validation is identical to registration policy. Other sessions are revoked per security decision.

**FS-ID-014** A timed-out reset confirmation shows an unconfirmed state rather than claiming success. A safe sign-in/verification step resolves ambiguity.

## 5. Adult profile and account settings

The authenticated parent can view account information (GET /me), update supported fields (PATCH /me), view sessions, change credentials and request deletion. Email change or other sensitive edits require security policies approved in [Security Architecture](../../03_Architecture/Security_Architecture.md).

**FS-ID-015** Adult account identity and child profile personalization are distinct; editing a child nickname cannot change the adult's account email.

**FS-ID-016** Password, PIN, account deletion and similarly sensitive changes require a valid adult verification challenge and a confirmation screen describing consequences.

**FS-ID-017** POST /me/deletion-request and /cancel track a real deletion request, not a pretend immediate erase. Display Requested, In progress, Canceled or Completed only as confirmed by server policy. Exact cancellation/grace period is [OPEN: DEC-008].

**FS-ID-018** A data-export ability is part of the privacy product intent, but an executable export API is NOT established by the current API Specification. Update the contract separately before implementation.

## 6. Error resolution by scenario

| Case | Visible behavior | Required invariant |
|---|---|---|
| Invalid account form | Per-field accessible message | No account created |
| Duplicate registration | Safe explanatory response | No second identity |
| Verification expired | Request fresh code | Token replay denied |
| Too many login attempts | Cooldown/support route | No account existence leak |
| Session revoked elsewhere | Clear private screens | No write succeeds with stale auth |
| Password reset token reused | Expired/unusable response | No reset |
| Network timeout after update | Show uncertain/pending and retry safely | Do not double-apply |
| Foreign account/session ID | Forbidden/not found per Error Catalog | Zero private data exposure |

## 7. Given / When / Then acceptance

- **ID-AT-01:** Given a pending account, when the correct verification code is used once and then reused, then only the first is accepted.
- **ID-AT-02:** Given an unknown email, when password recovery is requested, then public response does not reveal registration status.
- **ID-AT-03:** Given a rotated refresh token, when the previous token is replayed, then session reuse protection denies it.
- **ID-AT-04:** Given session A is revoked, when its client requests Parent Zone or changes a profile, then the server refuses.
- **ID-AT-05:** Given another parent's session identifier, when a user tries to revoke/view it, then the API does not reveal or change it.
- **ID-AT-06:** Given a rate-limited resend flow, when the user taps repeatedly, then backend challenge issuance remains bounded and UI reflects waiting.
- **ID-AT-07:** Given password reset confirmation has unknown network outcome, when the parent retries, then app does not falsely report a completed change.

**Outstanding approvals:** market/legal text and consent [DEC-007], child data/retention [DEC-008], approved password/session durations per security review. Cross-link: [Parent Zone](07_Parent_Zone_and_Controls.md), [Privacy](10_Notifications_Support_and_Privacy.md).
