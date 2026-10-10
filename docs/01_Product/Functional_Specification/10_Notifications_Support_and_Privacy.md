# 10 — Parent Notifications, Support, Account Privacy and Data Rights

**Actors:** adult parent, authorized support staff; Child World cannot send support messages or manage marketing.
**Requirements:** PRD-12, FR-NO-001..003, FR-SP-001, FR-ID-004.
**Owners:** notifications-service, identity-service, supporting data-owner microservices.
**Contracts:** [API Specification](../../03_Architecture/API_Specification.md) sections 20, 41–44; [Notifications blueprint](../../07_Blueprints/05_Notifications.md); [Privacy/Deletion blueprint](../../07_Blueprints/06_Privacy_Deletion.md).

## 1. Notification taxonomy

Parent-directed notifications include important account/security activity, billing and subscription state, new content, bedtime reminders, download status, service messages and support updates. Optional marketing is treated separately from required transactional notices.

**FS-NO-001** Each delivered/inbox notification has an approved category, parent-safe title/body, timestamp, read/unread state and safe destination or no link. A push preview must not expose child personal identifiers, detailed listening history, purchase credentials or signed private URLs.

**FS-NO-002** GET /notifications is account-scoped and paginated. POST /notifications/{notificationId}/read, /notifications/read-all and DELETE /notifications/{notificationId} mutate only the current adult's inbox, idempotently. No arbitrary foreign notification ID is accepted.

**FS-NO-003** A child never sees marketing preference forms or notifications addressed to the parent; opening a parent notification from the lock screen must not bypass authentication and Parent Zone challenge where necessary.

**FS-NO-004** Push is an optional delivery channel. The in-app inbox stays usable when push/email providers fail, and failures do not block eligible audio playback.

## 2. Device enrollment and preferences

Device registration PUT /devices/{deviceId} and DELETE /devices/{deviceId} are scoped to the current adult account. GET/PUT /notification-preferences control approved categories/channels.

**FS-NO-005** Reinstall, sign out, device ownership transfer and token rotation must revoke/replace provider device tokens to avoid notifying the previous parent account.

**FS-NO-006** Optional reminders/marketing respect parent opt-out, allowed quiet hours, locale, country and channel policies. Mandatory security notices follow reviewed compliance rules. Exact quiet hours, reminder cadence and channels need product/market approval.

**FS-NO-007** A server event must not produce unlimited duplicate sends. Retried event delivery uses idempotency and capped attempts with DLQ handling, never repeated child pressure.

**FS-NO-008** Parent can tell the difference between delivery preference saved and an actually delivered message; no false “notification sent” after provider failure.

## 3. Support contact and help

The Parent Zone has Help/FAQ and Contact Support. The existing public contract is POST /support/requests; a full interactive chat or ticket-status API is not established by that contract.

**FS-SP-001** Only authenticated/elevated adult as appropriate can submit a request. The screen collects a category, concise description, optional contact preference and approved diagnostics without automatically attaching child PII or tokens.

**FS-SP-002** Sending shows pending, submitted reference (only if safely returned), and retry on failure. An uncertain network outcome must not silently send unlimited duplicates.

**FS-SP-003** Children cannot contact strangers or staff from Child World. Support replies must use parent-approved private channels, and staff identity/access is auditable.

**FS-SP-004** FAQs cover account access, offline troubleshooting, app behavior, billing store links, privacy rights and reporting inappropriate content; content must be reviewed and localized before launch.

## 4. Data minimization and privacy

The adult owns the account; child profile contains only required or voluntarily approved preferences. Catalog listening telemetry must avoid identifying child data wherever aggregated metrics suffice.

**FS-PV-001** Never display account information of a different household, even if a device previously cached it. Logging, crash reporting, push and analytics avoid passwords, PINs, exact child birth dates, personal stories/transcripts or raw payment receipts.

**FS-PV-002** Parent can review available privacy notices and data categories in understandable language. Legal text, consent purpose, country-specific handling and retention durations require reviewed policy [OPEN: DEC-007/008].

**FS-PV-003** Account data export is product intent but currently lacks a canonical public export endpoint. A future contract must define adult authorization, export formats, categories, redactions, link expiry, status and verification before it can be coded.

## 5. Deletion lifecycle

The current API provides POST /me/deletion-request and POST /me/deletion-request/cancel. An account deletion request initiates a **distributed microservice workflow**, not instantaneous erasure of every record.

**FS-PV-004** A verified parent initiates deletion in Parent Zone after a meaningful confirmation explaining session revocation, profile/progress consequences, downloaded media removal and any policy-based cancellation window.

**FS-PV-005** UI distinguishes Requested, In Progress, Completed, Canceled and Failed/Needs Review only based on trustworthy server status. A mere queued message is not a completed deletion.

**FS-PV-006** Each owning service handles its account/profile data (profiles, playback, media grants, notifications/devices, identity), with retries, idempotent acknowledgements and audit. Billing/audit retention exceptions require a legal reason and eventual purge policy.

**FS-PV-007** Deleting an account must not imply that Apple/Google store subscription billing is automatically canceled; provide verified platform guidance and policy-compliant communication.

**FS-PV-008** Previously offline devices cannot reconnect and resurrect a deleted account's private records or obtain new media grants.

## 6. Failure matrix

| Condition | Visible behavior | Data/permission invariant |
|---|---|---|
| Push permission denied | In-app inbox remains | No deceptive re-prompt loop |
| Device token invalid | Registration refresh/revoke | No delivery to prior owner |
| Optional marketing opted out | No optional sends | Security notices per policy |
| Duplicate event | One logical notification | Inbox dedup |
| Parent opens child-specific deep link from push | Authenticate/recheck owner | No bypass |
| Support submission times out | Unconfirmed/retry | Avoid duplicate ticket |
| Export preparation fails | Adult sees retry/status | No unlocked public file |
| Account deletion partially fails | Pending/retry with support | No false Complete |
| Required financial retention | Explain only approved notice | Minimized/access restricted |
| Device reconnects after deletion | Session/access denied | No data resurrection |

## 7. Acceptance scenarios

- **NO-AT-01:** Given an optional notification category is opted out, when a trigger event occurs, then no optional push/email is sent.
- **NO-AT-02:** Given account A, when requesting B's notification ID, then it is denied and no metadata leaks.
- **NO-AT-03:** Given duplicate source event, when notification worker retries, then at most one logical inbox entry is created.
- **NO-AT-04:** Given push provider failure, when an event is processed, then an inbox record remains and playback still works.
- **NO-AT-05:** Given device token was associated with a signed-out parent, then future messages for that parent are not sent to the reused device.
- **PV-AT-01:** Given a child attempts a deletion route directly, then it is denied.
- **PV-AT-02:** Given deletion is queued but playback data remains, then UI does not show Completed.
- **PV-AT-03:** Given an offline device reconnects after confirmed deletion, then its cached profile requests are rejected.
- **SP-AT-01:** Given a support request timeout, then the UI offers safe retry and does not claim success without confirmation.

**OPEN:** supported notification languages, legally mandated notice categories, exact retention/deletion windows, export contract, approved support response channel. See Decision Register.
