# 16 — Input Validation, Confirmations and Error Copy Contract

**Applies to:** registration, recovery, profile forms, Parent Zone, search, purchase/restore, notification preferences, support, staff CMS and privacy actions.
**Behavioral authorities:** [Error Catalog](../../03_Architecture/Error_Catalog.md), [API Specification](../../03_Architecture/API_Specification.md), [UI Design System](../../02_UX_UI/UI_Design_System.md).
**Status:** UX/business contract; numeric validation limits come from canonical API/security policy, not from unapproved guesses.

## 1. Shared form standards

**FS-FM-001** Every editable form must show a meaningful label, mandatory/optional indication, user-friendly validation and a clear Save/Submit action. Placeholder text does not replace a visible accessible label.

**FS-FM-002** Client validation prevents common mistakes but backend validation and authorization remain authoritative. Server errors map to the relevant field or a general form message; unknown codes use a safe fallback.

**FS-FM-003** Inputs preserve safe unsaved content after a recoverable network error, but never retain plain passwords, PINs, verification codes or private store receipts in inappropriate persistence, screenshots or logs.

**FS-FM-004** Each submitted mutation has one active pending state. Additional button taps cannot create duplicate user-visible side effects; the backend owns idempotent or conflict-controlled behavior.

**FS-FM-005** A success banner appears only after confirmed server outcome. A timeout with unknown result is distinct from a validated failure and must offer an idempotent recovery path.

**FS-FM-006** Save/Cancel is unambiguous. Closing a dirty form may request confirmation to discard non-sensitive unsaved edits; navigation never inadvertently submits.

**FS-FM-007** On validation errors focus should move to a clear error summary or the relevant first invalid field. Screen-reader announcements must not be repeated endlessly on every keystroke.

## 2. Input-level validation inventory

| Context | Input | Required behavior | Negative case |
|---|---|---|---|
| Adult registration | Email | Normalize and validate according to accepted identity policy | Invalid format; duplicate-safe response |
| Adult registration | Password | Enforce approved strength, confirmation where shown | Too weak; mismatch; credential leakage |
| Verification | Code or link | Expiring one-use challenge, limited attempts | Expired/replayed/locked |
| Password recovery | Email and new password | Enumeration-safe request and policy-consistent new secret | Unknown account not revealed |
| Child creation | Nickname | Nonempty, safe length/characters and allowed content | HTML/unsafe text injection |
| Child creation | Age band | Approved set, minimal age data | Unapproved age or unsupported locale |
| Profile preferences | Category IDs/themes | Only approved choices; ownership checked | Foreign profile, inactive theme |
| Parent settings | Limits/restrictions | Clear units, bounds and affected child | Impossible duration or unapproved default |
| Parent PIN | Proof input | Secure entry, retry controls and expiry | Brute force, reused proof |
| Search | Query | Trim/encode, bounded length, approved scope | Oversized, malformed, unsafe request |
| Story text timeline | Segment start/end | Ordered positions within audio duration | Overlap, negative time, end > duration |
| Editorial upload | Media type/size, rights | Approved constraints, scan and integrity checks | Spoofed MIME, malicious bytes |
| Schedule publication | Date/time | Valid timestamp/timezone, current approved state | Past/invalid time, suspended rights |
| Subscription | Plan/store product | Render provider-confirmed configured offer | Unknown currency/product, stale trial |
| Support | Category/description | Minimal necessary data, length, safe attachments if supported | Personal secrets or malicious input |
| Notification preference | Channel/category | Parent authorized and schema-compatible | Unsupported type, foreign device |
| Deletion | Confirmation | Recent adult proof and approved impact text | Child/deep-link bypass |

Limits and regular expressions belong in executable API/validation contracts; this table states the interaction contract, not invented values.

## 3. Parent and child copy patterns

Draft examples are [ILLUSTRATIVE], not final localized copy.

| Situation | Child World style | Adult Parent Zone / Admin style |
|---|---|---|
| Network unavailable | “We can't connect right now. Try again.” | “Connection unavailable. Your change has not been confirmed.” |
| Story withdrawn | “This story isn't available right now.” | “This story is unavailable under current content settings.” |
| Premium-only story | “Ask a grown-up about more stories.” | “Premium access is required. View eligible plans.” |
| Invalid credentials | Never shown in Child World | “We couldn't sign you in. Check your details or recover access.” |
| Session expired | Ask adult to help | “Your session ended. Sign in again.” |
| PIN incorrect | No reveal of partial match | “Could not verify. Try again later or use approved recovery.” |
| Download corrupted | “Let's try this download again.” | “File integrity verification failed. Remove/retry.” |
| Purchase pending | No claim of success | “Your purchase is being verified. Access has not changed yet.” |
| Content upload scan failed | Not visible | “Asset processing did not pass checks; publication is blocked.” |
| Account deletion processing | Child cannot initiate | “Your deletion request is being processed; completion is not yet confirmed.” |

**FS-FM-008** No wording shames a child, invokes artificial fear/scarcity, threatens lost rewards, or pressures purchasing. A child should always be able to return to safe browsing.

**FS-FM-009** Do not display raw backend error codes, stack traces, session IDs, secret URLs or private editorial moderation notes to a child. Codes can be mapped to parent-safe messages and correlated to internal telemetry through a non-secret correlation ID.

## 4. Confirmations and irreversible actions

| Action | Adult confirmation | Server authority |
|---|---|---|
| Delete/archive child profile | Identify affected child, progress/download implications, approved reversibility | Verified Parent Zone + ownership |
| Request family deletion | Explain account, profile, data and store subscription consequences | Verified adult; saga status |
| Remove parent PIN | Reauthentication and clear effect on future Parent Zone | identity-service |
| Logout all sessions | Explain all devices will require login | identity-service |
| Restore/manage subscription | Explain actual store effect, not a fake local cancellation | billing-service/provider |
| Suspend or publish a story | Staff role, content version, effective timing and audit reason | catalog/admin authority |
| Entitlement override | Restricted staff approval and expiration reason | billing-service |

**FS-FM-010** A secondary/destructive action has a clearly differentiated label and safe Cancel. A processing spinner is not enough to prove completion.

**FS-FM-011** Device Back/gesture and accessibility Escape must not bypass confirmation or accidentally accept a purchase, deletion or admin publication.

## 5. Failure-to-action guidance

- **Validation (400/422):** show field messages; keep allowed content; do not automatic retry until corrected.
- **Unauthenticated (401):** clear or refresh according to documented session policy; adult authentication is necessary.
- **Forbidden (403):** do not retry indefinitely; explain protected action or unavailable content without leaking resources.
- **Not found (404):** distinguish missing content from network failure; avoid suggesting an unpublished item.
- **Conflict (409/412):** show current/reload or conflict resolution; never overwrite an unseen edit silently.
- **Rate limit (429):** respect Retry-After where supplied, show cooldown and stop repeated actions.
- **Server temporary (5xx):** preserve safe work, offer retry and use idempotency.
- **Store/provider unknown:** leave plan state Pending/Reconcile; do not simulate a paid result.
- **Offline:** queue only documented safe local changes; protected authority changes cannot be invented locally.

Actual status mappings/codes come exclusively from the [Error Catalog](../../03_Architecture/Error_Catalog.md); this is UI disposition guidance.

## 6. Recovery state tables

### Account registration

Draft -> validating -> submitting -> verification pending -> verified. Invalid draft stays editable; rejected registration shows safe correction; lost response checks server status instead of blindly duplicating identity.

### Profile restriction update

Current server settings -> draft edits -> submit with parent proof -> server committed -> refresh selected profile eligibility. If proof expires or version conflicts, do not silently apply the desired value locally; show explicit retry/reload.

### Subscription purchase

Plan selected -> store interaction -> provider pending -> server verified -> entitlement active or verified denial. Cancelled native store UI is not a purchase error; a received receipt is not entitlement success; provider outage is not Premium activation.

### Content upload

Editor selects asset -> upload grant -> bytes transfer -> scan/processing -> asset ready -> editorial review -> publish. A transfer completed without scan never means published.

## 7. QA acceptance cases

- **FM-AT-01:** Given validation fails, when screen reader is active, then the first invalid field/error is announced and focus can recover.
- **FM-AT-02:** Given a Save request times out after server success, then retry/resolution does not create duplicate business objects.
- **FM-AT-03:** Given a forbidden Parent Zone action, then no sensitive data is changed even when the client bypasses UI validation.
- **FM-AT-04:** Given a malformed search query, then a safe validation response appears without stack trace or blocked-content leakage.
- **FM-AT-05:** Given an edited admin record has a new revision, when a stale editor saves, then conflict is explicit and no silent overwrite occurs.
- **FM-AT-06:** Given an unknown store result, then the screen communicates Pending rather than “Premium active.”
- **FM-AT-07:** Given profile delete confirmation opens, when device back is used, then no deletion is submitted.
- **FM-AT-08:** Given a mobile app language change, then commercial/legal UI remains in an approved translation or blocks release as required.

## 8. Handoff and approved source

Every form uses [Screen Inventory](13_Screen_Inventory_and_UX_Handoff.md) for screen ID and [State Matrices](14_State_Matrices_and_Behavioral_Edge_Cases.md) for allowed transitions. Exact security values (password length, PIN lockouts), consent copy and deletion reversal windows remain approved owner decisions. Do not create an undocumented endpoint to make a form easier.
