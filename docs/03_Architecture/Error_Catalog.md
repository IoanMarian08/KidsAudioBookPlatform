# Error Catalog

Version: 1.1.0  
Status: Active Draft  
Owner: Project Architecture  
Last updated: 2026-07-15

## 1. Purpose

This document defines the stable, machine-readable error contract shared by the KidsAudioBookPlatform backend, Flutter mobile application, administrative dashboard, background workers, and integration adapters.

Human-readable messages may be localized and improved over time. Error codes, semantic meaning, retry behavior, and client handling expectations remain stable for all supported client versions.

This catalog is the source of truth for:

- public API error codes;
- asynchronous processing failure categories;
- client retry and recovery behavior;
- observability severity;
- support and incident correlation;
- compatibility rules for evolving errors.

API payload schemas belong in `API_Specification.md`. Runtime flows belong in `System_Flows.md`. Event failures belong in `Event_Catalog.md`. Logging and alerting rules belong in `Logging_Monitoring.md`.

## 2. Design Principles

1. **Codes are contracts.** Clients branch on stable codes, never on message text.
2. **Errors are safe by default.** Public responses never expose stack traces, SQL, secrets, internal hostnames, provider credentials, or sensitive child data.
3. **The server remains authoritative.** A client may suggest recovery, but it may not reinterpret authorization, entitlement, publication, or account state.
4. **Retry behavior is explicit.** Every error is classified as non-retryable, retryable after state refresh, retryable after delay, or retryable only through reconciliation.
5. **Expected business outcomes are not incidents.** A locked premium story is different from a failed database transaction.
6. **Correlation is mandatory.** Every error response and failed asynchronous operation includes a correlation identifier.
7. **Compatibility beats convenience.** Existing codes are never reused for a different meaning.
8. **Sensitive context stays internal.** Support details belong in structured logs and audit records, not public messages.

## 3. Standard Error Response

```json
{
  "timestamp": "2026-07-15T18:20:31Z",
  "status": 403,
  "code": "SUB_004",
  "message": "Premium subscription required.",
  "correlationId": "01J4K8Y8Q2DP4S8M4A5Q7V6T9X",
  "path": "/v1/downloads/authorize",
  "retryable": false,
  "details": []
}
```

### 3.1 Required fields

| Field | Type | Meaning |
|---|---|---|
| `timestamp` | ISO-8601 UTC string | Time when the platform created the response |
| `status` | integer | HTTP response status |
| `code` | string | Stable machine-readable catalog code |
| `message` | string | Safe, localizable user-facing message |
| `correlationId` | string | Identifier used for logs, traces, support, and incidents |
| `path` | string | Normalized request path without sensitive query values |
| `retryable` | boolean | Whether the same logical operation may be attempted again |
| `details` | array | Optional structured, safe details |

### 3.2 Optional fields

The API may additionally return:

- `retryAfterSeconds` for bounded delayed retries;
- `operationId` for asynchronous operations;
- `resourceVersion` for optimistic locking conflicts;
- `supportReference` for severe customer-facing failures;
- `documentationKey` for linking a client to help content.

Optional fields must not change the meaning of the stable error code.

## 4. Validation Detail Format

Validation failures may contain field-level details:

```json
{
  "timestamp": "2026-07-15T18:22:00Z",
  "status": 400,
  "code": "VAL_001",
  "message": "Request validation failed.",
  "correlationId": "01J4K90H81YJ45C6S2B4Z1W8QF",
  "path": "/v1/profiles",
  "retryable": false,
  "details": [
    {
      "field": "name",
      "reason": "SIZE",
      "message": "Profile name must contain between 1 and 30 characters."
    }
  ]
}
```

Rules:

- field names use public API names, never Java property or database column names;
- reasons are stable uppercase identifiers;
- rejected passwords, tokens, PINs, email verification values, purchase receipts, and raw uploaded content are never echoed;
- nested field paths use dot notation, for example `episodes.0.title`;
- clients may highlight a field by `field`, but must still handle unknown reasons safely.

## 5. Error Code Naming

Codes use the format:

```text
<DOMAIN>_<NUMBER>
```

Examples:

- `AUTH_001`
- `PROFILE_003`
- `DOWNLOAD_007`
- `SYS_001`

Rules:

- prefixes identify bounded context or cross-cutting category;
- numeric identifiers are zero-padded to three digits;
- removed codes remain reserved permanently;
- codes are not reordered;
- a new semantic meaning receives a new code even when the HTTP status is unchanged.

## 6. Severity Model

| Severity | Meaning | Default operational action |
|---|---|---|
| `INFO` | Expected business outcome | No alert; product metric when useful |
| `WARN` | Suspicious, invalid, abusive, or degraded behavior | Aggregate and monitor |
| `ERROR` | Unexpected operation or dependency failure | Create error metric and investigate trend |
| `CRITICAL` | Security, data-integrity, or major availability incident | Immediate alert and incident workflow |

Severity is an observability classification. It is not returned as a public API field unless an internal administrative API explicitly requires it.

## 7. Retry Classification

| Classification | Meaning | Client behavior |
|---|---|---|
| `NO_RETRY` | Same request cannot succeed without user or state change | Show explanation or corrective action |
| `REFRESH_THEN_RETRY` | Client state may be stale | Reload authoritative state, then retry once |
| `DELAYED_RETRY` | Temporary condition | Respect `Retry-After` or bounded exponential backoff |
| `RECONCILIATION_ONLY` | Provider or asynchronous state must settle | Poll operation status or wait for reconciliation |
| `SAFE_REAUTH` | Authentication context may be recoverable | Refresh token once, otherwise sign in again |

Clients must never retry non-idempotent writes automatically unless an idempotency key is present and the API explicitly permits retry.

## 8. Authentication and Session

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `AUTH_001` | 401 | Invalid email or password. | INFO | NO_RETRY |
| `AUTH_002` | 401 | Your session has expired. Please sign in again. | INFO | SAFE_REAUTH |
| `AUTH_003` | 401 | Invalid refresh token. | WARN | NO_RETRY |
| `AUTH_004` | 423 | Account temporarily locked. Try again later. | WARN | DELAYED_RETRY |
| `AUTH_005` | 403 | Email verification is required. | INFO | NO_RETRY |
| `AUTH_006` | 403 | Account is disabled. | WARN | NO_RETRY |
| `AUTH_007` | 429 | Too many authentication attempts. | WARN | DELAYED_RETRY |
| `AUTH_008` | 409 | This email address is already registered. | INFO | NO_RETRY |
| `AUTH_009` | 400 | Verification token is invalid or expired. | INFO | NO_RETRY |
| `AUTH_010` | 401 | Session was revoked. | WARN | NO_RETRY |
| `AUTH_011` | 409 | Session refresh is already in progress. | INFO | DELAYED_RETRY |
| `AUTH_012` | 403 | This device session requires additional verification. | WARN | NO_RETRY |
| `AUTH_013` | 409 | Password reset request has already been used. | INFO | NO_RETRY |
| `AUTH_014` | 400 | Password does not meet security requirements. | INFO | NO_RETRY |

Authentication responses must not reveal whether an unknown email address exists, except in authenticated account-management flows where ownership is already established.

## 9. Parent Zone

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `PARENT_001` | 401 | Parent verification is required. | INFO | NO_RETRY |
| `PARENT_002` | 401 | Incorrect PIN. | INFO | NO_RETRY |
| `PARENT_003` | 423 | Parent Zone is temporarily locked. | WARN | DELAYED_RETRY |
| `PARENT_004` | 400 | Parent Zone grant is invalid or expired. | INFO | NO_RETRY |
| `PARENT_005` | 409 | A Parent Zone PIN is already configured. | INFO | REFRESH_THEN_RETRY |
| `PARENT_006` | 400 | Parent Zone PIN does not meet requirements. | INFO | NO_RETRY |
| `PARENT_007` | 403 | Biometric verification is not accepted for this operation. | INFO | NO_RETRY |
| `PARENT_008` | 409 | Parent verification policy changed. Verify again. | WARN | NO_RETRY |

## 10. Profiles

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `PROFILE_001` | 404 | Child profile was not found. | INFO | NO_RETRY |
| `PROFILE_002` | 403 | You cannot access this profile. | WARN | NO_RETRY |
| `PROFILE_003` | 409 | Maximum number of profiles reached. | INFO | NO_RETRY |
| `PROFILE_004` | 400 | Profile name is invalid. | INFO | NO_RETRY |
| `PROFILE_005` | 400 | Unsupported age range. | INFO | NO_RETRY |
| `PROFILE_006` | 409 | Profile cannot be deleted while an operation is in progress. | INFO | DELAYED_RETRY |
| `PROFILE_007` | 409 | Profile was modified on another device. Refresh and try again. | INFO | REFRESH_THEN_RETRY |
| `PROFILE_008` | 400 | Profile preferences are invalid. | INFO | NO_RETRY |
| `PROFILE_009` | 409 | Profile is archived. | INFO | NO_RETRY |
| `PROFILE_010` | 403 | This feature is not available for the selected profile. | INFO | NO_RETRY |

## 11. Catalog, Search, and Content

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `STORY_001` | 404 | Story was not found. | INFO | NO_RETRY |
| `STORY_002` | 409 | Story is not published. | INFO | REFRESH_THEN_RETRY |
| `STORY_003` | 403 | Story is not available for this profile. | INFO | NO_RETRY |
| `STORY_004` | 409 | Story version has changed. Refresh and try again. | INFO | REFRESH_THEN_RETRY |
| `STORY_005` | 409 | Story cannot be published in its current state. | INFO | NO_RETRY |
| `STORY_006` | 400 | Story metadata is invalid. | INFO | NO_RETRY |
| `STORY_007` | 404 | Episode was not found. | INFO | NO_RETRY |
| `STORY_008` | 409 | Transcript timing is invalid. | INFO | NO_RETRY |
| `STORY_009` | 409 | Required media assets are missing. | INFO | REFRESH_THEN_RETRY |
| `STORY_010` | 451 | Story is unavailable in your region. | INFO | NO_RETRY |
| `STORY_011` | 409 | Story is scheduled for publication. | INFO | NO_RETRY |
| `STORY_012` | 409 | Story is suspended. | WARN | NO_RETRY |
| `STORY_013` | 400 | Unsupported story language. | INFO | NO_RETRY |
| `SEARCH_001` | 400 | Search query is invalid. | INFO | NO_RETRY |
| `SEARCH_002` | 503 | Search is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `SEARCH_003` | 400 | Search filters are not supported. | INFO | NO_RETRY |

## 12. Playback and Progress

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `PLAY_001` | 403 | Playback is not allowed. | INFO | NO_RETRY |
| `PLAY_002` | 404 | Listening session was not found. | INFO | NO_RETRY |
| `PLAY_003` | 409 | Listening session is already closed. | INFO | REFRESH_THEN_RETRY |
| `PLAY_004` | 400 | Playback position is invalid. | INFO | NO_RETRY |
| `PLAY_005` | 409 | Progress update is older than the current state. | INFO | REFRESH_THEN_RETRY |
| `PLAY_006` | 410 | Media authorization has expired. | INFO | REFRESH_THEN_RETRY |
| `PLAY_007` | 503 | Audio is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `PLAY_008` | 409 | Episode duration changed. Refresh playback metadata. | INFO | REFRESH_THEN_RETRY |
| `PLAY_009` | 400 | Progress operation identifier is invalid. | WARN | NO_RETRY |
| `PLAY_010` | 409 | Playback session belongs to another profile. | WARN | NO_RETRY |
| `PLAY_011` | 503 | Progress synchronization is temporarily unavailable. | ERROR | DELAYED_RETRY |

## 13. Downloads and Offline Access

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `DOWNLOAD_001` | 403 | Offline downloads require Premium. | INFO | NO_RETRY |
| `DOWNLOAD_002` | 409 | Offline download limit reached. | INFO | NO_RETRY |
| `DOWNLOAD_003` | 403 | This device is not authorized for downloads. | WARN | NO_RETRY |
| `DOWNLOAD_004` | 410 | Download authorization has expired. | INFO | REFRESH_THEN_RETRY |
| `DOWNLOAD_005` | 409 | Downloaded content is outdated. | INFO | REFRESH_THEN_RETRY |
| `DOWNLOAD_006` | 409 | Download checksum does not match. | WARN | REFRESH_THEN_RETRY |
| `DOWNLOAD_007` | 403 | Offline entitlement has expired. | INFO | NO_RETRY |
| `DOWNLOAD_008` | 404 | Download manifest was not found. | INFO | NO_RETRY |
| `DOWNLOAD_009` | 409 | Download is already registered for this device. | INFO | REFRESH_THEN_RETRY |
| `DOWNLOAD_010` | 409 | Offline license was revoked. | WARN | NO_RETRY |
| `DOWNLOAD_011` | 507 | Not enough device storage is available. | INFO | NO_RETRY |
| `DOWNLOAD_012` | 503 | Download authorization is temporarily unavailable. | ERROR | DELAYED_RETRY |

## 14. Subscriptions and Entitlements

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `SUB_001` | 400 | Purchase proof is invalid. | WARN | NO_RETRY |
| `SUB_002` | 409 | Purchase has already been processed. | INFO | REFRESH_THEN_RETRY |
| `SUB_003` | 502 | Purchase could not be verified. Try again later. | ERROR | RECONCILIATION_ONLY |
| `SUB_004` | 403 | Premium subscription required. | INFO | NO_RETRY |
| `SUB_005` | 409 | Subscription is in a grace period. | INFO | REFRESH_THEN_RETRY |
| `SUB_006` | 403 | Subscription has expired. | INFO | NO_RETRY |
| `SUB_007` | 403 | Subscription was revoked. | WARN | NO_RETRY |
| `SUB_008` | 409 | Subscription state is being reconciled. | INFO | RECONCILIATION_ONLY |
| `SUB_009` | 400 | Unsupported purchase provider. | WARN | NO_RETRY |
| `SUB_010` | 409 | Purchase belongs to another account. | WARN | NO_RETRY |
| `SUB_011` | 409 | Trial is not available for this account. | INFO | NO_RETRY |
| `SUB_012` | 503 | Store verification service is temporarily unavailable. | ERROR | RECONCILIATION_ONLY |
| `SUB_013` | 409 | Entitlement snapshot is stale. | INFO | REFRESH_THEN_RETRY |
| `SUB_014` | 409 | Subscription product is not active. | INFO | NO_RETRY |

Permanent premium entitlement must never be granted in response to `SUB_003`, `SUB_008`, or `SUB_012`.

## 15. Advertising Eligibility

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `AD_001` | 403 | Advertising is not allowed for this account. | INFO | NO_RETRY |
| `AD_002` | 409 | An advertisement is not due yet. | INFO | NO_RETRY |
| `AD_003` | 409 | Advertisement opportunity has expired. | INFO | REFRESH_THEN_RETRY |
| `AD_004` | 503 | Advertisement is temporarily unavailable. | WARN | NO_RETRY |
| `AD_005` | 400 | Advertisement result is invalid. | WARN | NO_RETRY |
| `AD_006` | 409 | Advertisement result was already recorded. | INFO | NO_RETRY |
| `AD_007` | 403 | Premium users are not eligible for advertising. | INFO | NO_RETRY |

An advertisement provider failure must never block story playback. `AD_004` is operationally visible but product behavior degrades by skipping the ad.

## 16. Notifications

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `NOTIF_001` | 404 | Notification was not found. | INFO | NO_RETRY |
| `NOTIF_002` | 400 | Notification preferences are invalid. | INFO | NO_RETRY |
| `NOTIF_003` | 409 | Notification has already been processed. | INFO | NO_RETRY |
| `NOTIF_004` | 502 | Notification provider rejected the request. | ERROR | RECONCILIATION_ONLY |
| `NOTIF_005` | 503 | Notification delivery is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `NOTIF_006` | 400 | Device token is invalid. | WARN | NO_RETRY |
| `NOTIF_007` | 409 | Notification template is not active. | WARN | NO_RETRY |
| `NOTIF_008` | 409 | Notification was suppressed by user preferences. | INFO | NO_RETRY |
| `NOTIF_009` | 409 | Notification was suppressed by quiet hours. | INFO | DELAYED_RETRY |
| `NOTIF_010` | 409 | Notification has expired. | INFO | NO_RETRY |

## 17. Media and Uploads

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `MEDIA_001` | 400 | File type is not supported. | INFO | NO_RETRY |
| `MEDIA_002` | 413 | File is too large. | INFO | NO_RETRY |
| `MEDIA_003` | 400 | File checksum is invalid. | WARN | NO_RETRY |
| `MEDIA_004` | 422 | File did not pass security scanning. | CRITICAL | NO_RETRY |
| `MEDIA_005` | 409 | Media processing is not complete. | INFO | RECONCILIATION_ONLY |
| `MEDIA_006` | 503 | Media processing is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `MEDIA_007` | 404 | Media asset was not found. | INFO | NO_RETRY |
| `MEDIA_008` | 410 | Upload authorization has expired. | INFO | REFRESH_THEN_RETRY |
| `MEDIA_009` | 409 | Media asset is already linked to another version. | INFO | NO_RETRY |
| `MEDIA_010` | 422 | Audio metadata is invalid. | INFO | NO_RETRY |
| `MEDIA_011` | 422 | Illustration dimensions are invalid. | INFO | NO_RETRY |
| `MEDIA_012` | 409 | Media asset is currently being processed. | INFO | RECONCILIATION_ONLY |
| `MEDIA_013` | 507 | Media storage capacity is temporarily exhausted. | ERROR | DELAYED_RETRY |

`MEDIA_004` must create a security event. The public response must not disclose malware signature details.

## 18. Administration and Publishing

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `ADMIN_001` | 403 | You do not have permission to perform this action. | WARN | NO_RETRY |
| `ADMIN_002` | 409 | Resource was modified by another user. Refresh and try again. | INFO | REFRESH_THEN_RETRY |
| `ADMIN_003` | 400 | Approval reason is required. | INFO | NO_RETRY |
| `ADMIN_004` | 409 | Content is already published. | INFO | REFRESH_THEN_RETRY |
| `ADMIN_005` | 409 | Scheduled publication time is invalid. | INFO | NO_RETRY |
| `ADMIN_006` | 409 | Bulk operation is already running. | INFO | RECONCILIATION_ONLY |
| `ADMIN_007` | 409 | Review approval is required. | INFO | NO_RETRY |
| `ADMIN_008` | 409 | Publication was superseded by a newer version. | WARN | REFRESH_THEN_RETRY |
| `ADMIN_009` | 400 | Support action reason is required. | INFO | NO_RETRY |
| `ADMIN_010` | 403 | This action requires elevated approval. | WARN | NO_RETRY |
| `ADMIN_011` | 409 | Scheduled operation can no longer be changed. | INFO | REFRESH_THEN_RETRY |

## 19. Audit and Compliance

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `AUDIT_001` | 500 | Audit record could not be created. | CRITICAL | NO_RETRY |
| `AUDIT_002` | 403 | You cannot access this audit record. | WARN | NO_RETRY |
| `AUDIT_003` | 400 | Audit search criteria are invalid. | INFO | NO_RETRY |
| `AUDIT_004` | 409 | Audit export is already in progress. | INFO | RECONCILIATION_ONLY |
| `AUDIT_005` | 410 | Audit export has expired. | INFO | NO_RETRY |

A privileged operation that requires audit persistence must fail closed when its audit record cannot be committed safely.

## 20. Account Deletion and Privacy

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `PRIVACY_001` | 409 | Account deletion is already scheduled. | INFO | NO_RETRY |
| `PRIVACY_002` | 403 | Recent parent verification is required. | INFO | NO_RETRY |
| `PRIVACY_003` | 409 | Account deletion cannot be completed while billing reconciliation is pending. | INFO | RECONCILIATION_ONLY |
| `PRIVACY_004` | 404 | Data export request was not found. | INFO | NO_RETRY |
| `PRIVACY_005` | 409 | Data export is already being prepared. | INFO | RECONCILIATION_ONLY |
| `PRIVACY_006` | 410 | Data export has expired. | INFO | NO_RETRY |
| `PRIVACY_007` | 500 | Privacy operation failed. | CRITICAL | NO_RETRY |

## 21. Validation, Rate Limiting, and Idempotency

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `VAL_001` | 400 | Request validation failed. | INFO | NO_RETRY |
| `VAL_002` | 400 | Request body is malformed. | INFO | NO_RETRY |
| `VAL_003` | 400 | Unsupported sort or filter value. | INFO | NO_RETRY |
| `VAL_004` | 400 | Required request header is missing. | INFO | NO_RETRY |
| `VAL_005` | 415 | Content type is not supported. | INFO | NO_RETRY |
| `VAL_006` | 406 | Requested response format is not supported. | INFO | NO_RETRY |
| `RATE_001` | 429 | Too many requests. Try again later. | WARN | DELAYED_RETRY |
| `RATE_002` | 429 | Daily operation limit reached. | INFO | DELAYED_RETRY |
| `IDEMP_001` | 409 | Idempotency key was reused with different data. | WARN | NO_RETRY |
| `IDEMP_002` | 409 | This operation is still being processed. | INFO | RECONCILIATION_ONLY |
| `IDEMP_003` | 400 | Idempotency key is invalid. | WARN | NO_RETRY |

## 22. External Dependencies

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `EXT_001` | 503 | An external service is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `EXT_002` | 504 | An external service timed out. | ERROR | DELAYED_RETRY |
| `EXT_003` | 502 | An external service returned an invalid response. | ERROR | RECONCILIATION_ONLY |
| `EXT_004` | 503 | Object storage is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `EXT_005` | 503 | Messaging service is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `EXT_006` | 503 | Cache service is temporarily unavailable. | WARN | DELAYED_RETRY |
| `EXT_007` | 502 | Provider callback could not be verified. | WARN | NO_RETRY |
| `EXT_008` | 409 | Provider callback was already processed. | INFO | NO_RETRY |

Provider-specific diagnostic codes remain internal and must be mapped to one of the stable platform codes.

## 23. System and Data Integrity

| Code | HTTP | User message | Severity | Retry |
|---|---:|---|---|---|
| `SYS_001` | 500 | Something went wrong. Please try again. | ERROR | DELAYED_RETRY |
| `SYS_002` | 503 | Service is temporarily unavailable. | ERROR | DELAYED_RETRY |
| `SYS_003` | 409 | Operation conflicts with the current resource state. | INFO | REFRESH_THEN_RETRY |
| `SYS_004` | 503 | Service is starting. Try again shortly. | WARN | DELAYED_RETRY |
| `SYS_005` | 503 | Service is temporarily read-only. | ERROR | DELAYED_RETRY |
| `DATA_001` | 500 | A data consistency problem occurred. | CRITICAL | NO_RETRY |
| `DATA_002` | 409 | Referenced resource does not exist. | WARN | REFRESH_THEN_RETRY |
| `DATA_003` | 409 | Duplicate resource detected. | WARN | REFRESH_THEN_RETRY |
| `DATA_004` | 409 | Resource version conflict. Refresh and try again. | INFO | REFRESH_THEN_RETRY |
| `DATA_005` | 500 | Required data could not be decrypted. | CRITICAL | NO_RETRY |

## 24. Asynchronous Operation Failures

Background jobs and event consumers do not return HTTP responses, but they use the same catalog codes in logs, metrics, retry records, and dead-letter metadata.

Recommended failure record:

```json
{
  "operationId": "01J4KA0F8TRD0K14YJY2D7G92N",
  "operationType": "MEDIA_PROCESSING",
  "status": "FAILED",
  "errorCode": "MEDIA_006",
  "attempt": 4,
  "retryable": true,
  "nextAttemptAt": "2026-07-15T18:30:00Z",
  "correlationId": "01J4K9ZP6F67SWR5WHM3H6W8VQ"
}
```

Rules:

- retry counts and next-attempt times are internal or admin-only;
- dead-letter records preserve event ID, event type, version, consumer, error code, and correlation ID;
- poison messages are quarantined rather than retried forever;
- an operator replay creates a new audit record;
- public clients receive an operation status, not internal exception details.

## 25. HTTP Status Guidance

| HTTP status | Use |
|---:|---|
| `400` | Malformed or semantically invalid request |
| `401` | Missing, expired, or invalid authentication |
| `403` | Authenticated but not authorized or not entitled |
| `404` | Resource is not visible or does not exist |
| `409` | State conflict, duplicate, optimistic lock, or operation in progress |
| `410` | Previously valid token, authorization, or export has expired |
| `413` | Request or upload exceeds allowed size |
| `415` | Unsupported content type |
| `422` | Content accepted structurally but rejected by domain or security processing |
| `423` | Temporarily locked resource or account |
| `429` | Rate or quota exceeded |
| `451` | Legal or regional unavailability |
| `500` | Unexpected platform failure |
| `502` | Invalid or rejected upstream response |
| `503` | Temporary dependency or service unavailability |
| `504` | Upstream timeout |
| `507` | Capacity or storage limit prevents completion |

A `404` may intentionally hide whether a protected resource exists.

## 26. Client Handling Policy

### 26.1 Flutter mobile application

- `401`: refresh once where allowed; otherwise clear protected session state and return to login.
- `403`: show access, verification, entitlement, or Parent Zone guidance based on the code.
- `404`: remove stale local references when safe.
- `409`: refresh authoritative state before one manual or idempotent retry.
- `410`: request a new authorization, manifest, token, or export.
- `423` and `429`: show cooldown state and respect `Retry-After`.
- `5xx`: preserve local progress or pending action and offer a safe retry.
- unknown codes: use a generic safe message and retain the correlation ID.

### 26.2 Admin dashboard

The dashboard additionally:

- displays optimistic-lock conflicts without overwriting another operator's work;
- surfaces operation IDs for long-running jobs;
- shows elevated warnings for `WARN`, `ERROR`, and `CRITICAL` outcomes when returned through internal APIs;
- requires explicit operator confirmation before replaying a failed operation;
- never exposes raw provider or stack-trace details to unauthorized roles.

## 27. Logging Policy

Known errors log:

- error code;
- correlation and trace identifiers;
- service and bounded context;
- operation name;
- actor type and anonymized actor ID;
- safe resource identifiers;
- HTTP status or consumer outcome;
- retry classification;
- elapsed duration;
- provider name where relevant, without credentials or raw payloads.

Rules:

- `INFO` outcomes are not automatically incidents;
- repeated `WARN` outcomes feed abuse, fraud, and anomaly dashboards;
- `ERROR` codes create failure metrics;
- `CRITICAL` codes create immediate alerts unless explicitly suppressed by an approved incident policy;
- passwords, PINs, tokens, purchase receipts, signed URLs, raw child data, and private media content are never logged.

## 28. Metrics and Alerting

Recommended metrics:

```text
api_errors_total{service,code,status}
async_failures_total{consumer,code}
error_retry_total{code,outcome}
validation_errors_total{endpoint,field,reason}
provider_errors_total{provider,code}
dead_letter_messages_total{consumer,event_type}
```

Alerting must be based on rate, ratio, duration, backlog, or severity rather than on every individual expected error.

Examples:

- do not alert on isolated `SUB_004` premium-required outcomes;
- alert on sustained growth of `SUB_003` or `SUB_012`;
- immediately alert on `DATA_001`, `DATA_005`, `AUDIT_001`, or `PRIVACY_007`;
- investigate spikes in `AUTH_003`, `AUTH_007`, `PROFILE_002`, or `IDEMP_001` as potential abuse.

## 29. Security and Privacy Requirements

- Error messages must not enable account enumeration.
- Authorization failures may return `404` instead of `403` when existence must remain hidden.
- Validation details must not reveal internal schemas or forbidden values.
- Upload scanning failures do not disclose malware names or signatures.
- Purchase verification failures do not echo raw receipts.
- Parent Zone failures do not reveal PIN hashes, attempt counters, or biometric metadata.
- Correlation IDs are opaque and contain no personal information.
- Support tooling must apply role-based access and audit all sensitive error investigations.

## 30. Compatibility and Change Management

### 30.1 Adding a code

A new code requires:

1. a unique reserved identifier;
2. semantic definition;
3. HTTP status or asynchronous category;
4. severity;
5. retry classification;
6. safe default message;
7. client handling expectations;
8. API, flow, and test updates where applicable.

### 30.2 Changing a code

Allowed changes:

- improve message wording without changing semantics;
- add optional safe details;
- improve internal logging;
- tighten alerts;
- change retry timing while preserving retry classification.

Breaking changes:

- assigning a different meaning to an existing code;
- changing a non-retryable business outcome into an automatic retry without compatibility review;
- changing authorization semantics;
- removing a code still used by supported clients;
- replacing a specific code with `SYS_001` without justification.

Breaking changes require an ADR and API versioning review.

### 30.3 Deprecation

Deprecated codes remain documented until telemetry proves that all supported clients and active workers no longer depend on them. Their identifiers are never reused.

## 31. Testing Requirements

Every catalog code used by implementation must have appropriate automated coverage:

- controller or API integration test for HTTP mapping;
- unit test for domain decision where applicable;
- authorization test for protected resources;
- contract test for response schema;
- retry test for transient failures;
- idempotency test for retryable writes;
- log redaction test for sensitive flows;
- client handling test for critical mobile and admin journeys.

The build should fail when implementation references an undocumented error code or when the same code is defined more than once.

## 32. Definition of Completion

An error is implementation-ready when:

- the code exists in this catalog;
- its meaning is unambiguous;
- public wording is safe;
- HTTP or asynchronous mapping is defined;
- severity and retry behavior are explicit;
- client recovery behavior is known;
- logs and metrics are specified;
- security and privacy implications are reviewed;
- tests cover normal and failure behavior;
- related API and flow documents are synchronized.
