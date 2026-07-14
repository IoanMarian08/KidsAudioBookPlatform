# Error Catalog

Version: 1.0.0  
Status: Draft

## Purpose

This document defines stable, machine-readable error codes shared by backend, mobile application and admin dashboard. Human-readable messages may be localized; error codes and semantic meaning remain stable.

## Standard Error Response

```json
{
  "timestamp": "2026-07-14T18:20:31Z",
  "status": 403,
  "code": "SUB_004",
  "message": "Premium subscription required.",
  "correlationId": "01J...",
  "path": "/v1/downloads/authorize",
  "details": []
}
```

Rules:
- Never expose stack traces, SQL fragments, secrets or provider credentials.
- `message` is safe for users; internal context belongs in structured logs.
- validation failures may include field-level details.
- clients branch on `code`, never on message text.
- unexpected failures use `SYS_001` and a correlation identifier.

## Severity

| Severity | Meaning |
|---|---|
| INFO | Expected business outcome requiring no operational action |
| WARN | Suspicious or degraded behavior worth monitoring |
| ERROR | Request or asynchronous operation failed unexpectedly |
| CRITICAL | Security, data-integrity or availability incident requiring immediate response |

## Authentication and Session

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| AUTH_001 | 401 | Invalid email or password. | INFO |
| AUTH_002 | 401 | Your session has expired. Please sign in again. | INFO |
| AUTH_003 | 401 | Invalid refresh token. | WARN |
| AUTH_004 | 423 | Account temporarily locked. Try again later. | WARN |
| AUTH_005 | 403 | Email verification is required. | INFO |
| AUTH_006 | 403 | Account is disabled. | WARN |
| AUTH_007 | 429 | Too many authentication attempts. | WARN |
| AUTH_008 | 409 | This email address is already registered. | INFO |
| AUTH_009 | 400 | Verification token is invalid or expired. | INFO |
| AUTH_010 | 401 | Session was revoked. | WARN |

## Parent Zone

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| PARENT_001 | 401 | Parent verification is required. | INFO |
| PARENT_002 | 401 | Incorrect PIN. | INFO |
| PARENT_003 | 423 | Parent Zone is temporarily locked. | WARN |
| PARENT_004 | 400 | Parent Zone grant is invalid or expired. | INFO |
| PARENT_005 | 409 | A Parent Zone PIN is already configured. | INFO |

## Profiles

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| PROFILE_001 | 404 | Child profile was not found. | INFO |
| PROFILE_002 | 403 | You cannot access this profile. | WARN |
| PROFILE_003 | 409 | Maximum number of profiles reached. | INFO |
| PROFILE_004 | 400 | Profile name is invalid. | INFO |
| PROFILE_005 | 400 | Unsupported age range. | INFO |
| PROFILE_006 | 409 | Profile cannot be deleted while an operation is in progress. | INFO |

## Catalog and Content

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| STORY_001 | 404 | Story was not found. | INFO |
| STORY_002 | 409 | Story is not published. | INFO |
| STORY_003 | 403 | Story is not available for this profile. | INFO |
| STORY_004 | 409 | Story version has changed. Refresh and try again. | INFO |
| STORY_005 | 409 | Story cannot be published in its current state. | INFO |
| STORY_006 | 400 | Story metadata is invalid. | INFO |
| STORY_007 | 404 | Episode was not found. | INFO |
| STORY_008 | 409 | Transcript timing is invalid. | INFO |
| STORY_009 | 409 | Required media assets are missing. | INFO |
| STORY_010 | 451 | Story is unavailable in your region. | INFO |

## Playback and Progress

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| PLAY_001 | 403 | Playback is not allowed. | INFO |
| PLAY_002 | 404 | Listening session was not found. | INFO |
| PLAY_003 | 409 | Listening session is already closed. | INFO |
| PLAY_004 | 400 | Playback position is invalid. | INFO |
| PLAY_005 | 409 | Progress update is older than the current state. | INFO |
| PLAY_006 | 410 | Media authorization has expired. | INFO |
| PLAY_007 | 503 | Audio is temporarily unavailable. | ERROR |

## Downloads

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| DOWNLOAD_001 | 403 | Offline downloads require Premium. | INFO |
| DOWNLOAD_002 | 409 | Offline download limit reached. | INFO |
| DOWNLOAD_003 | 403 | This device is not authorized for downloads. | WARN |
| DOWNLOAD_004 | 410 | Download authorization has expired. | INFO |
| DOWNLOAD_005 | 409 | Downloaded content is outdated. | INFO |
| DOWNLOAD_006 | 409 | Download checksum does not match. | WARN |
| DOWNLOAD_007 | 403 | Offline entitlement has expired. | INFO |

## Subscriptions and Entitlements

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| SUB_001 | 400 | Purchase proof is invalid. | WARN |
| SUB_002 | 409 | Purchase has already been processed. | INFO |
| SUB_003 | 502 | Purchase could not be verified. Try again later. | ERROR |
| SUB_004 | 403 | Premium subscription required. | INFO |
| SUB_005 | 409 | Subscription is in a grace period. | INFO |
| SUB_006 | 403 | Subscription has expired. | INFO |
| SUB_007 | 403 | Subscription was revoked. | WARN |
| SUB_008 | 409 | Subscription state is being reconciled. | INFO |
| SUB_009 | 400 | Unsupported purchase provider. | WARN |

## Notifications

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| NOTIF_001 | 404 | Notification was not found. | INFO |
| NOTIF_002 | 400 | Notification preferences are invalid. | INFO |
| NOTIF_003 | 409 | Notification has already been processed. | INFO |
| NOTIF_004 | 502 | Notification provider rejected the request. | ERROR |
| NOTIF_005 | 503 | Notification delivery is temporarily unavailable. | ERROR |
| NOTIF_006 | 400 | Device token is invalid. | WARN |

## Media and Uploads

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| MEDIA_001 | 400 | File type is not supported. | INFO |
| MEDIA_002 | 413 | File is too large. | INFO |
| MEDIA_003 | 400 | File checksum is invalid. | WARN |
| MEDIA_004 | 422 | File did not pass security scanning. | CRITICAL |
| MEDIA_005 | 409 | Media processing is not complete. | INFO |
| MEDIA_006 | 503 | Media processing is temporarily unavailable. | ERROR |
| MEDIA_007 | 404 | Media asset was not found. | INFO |
| MEDIA_008 | 410 | Upload authorization has expired. | INFO |

## Administration

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| ADMIN_001 | 403 | You do not have permission to perform this action. | WARN |
| ADMIN_002 | 409 | Resource was modified by another user. Refresh and try again. | INFO |
| ADMIN_003 | 400 | Approval reason is required. | INFO |
| ADMIN_004 | 409 | Content is already published. | INFO |
| ADMIN_005 | 409 | Scheduled publication time is invalid. | INFO |
| ADMIN_006 | 409 | Bulk operation is already running. | INFO |

## Validation, Rate Limiting and Idempotency

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| VAL_001 | 400 | Request validation failed. | INFO |
| VAL_002 | 400 | Request body is malformed. | INFO |
| VAL_003 | 400 | Unsupported sort or filter value. | INFO |
| RATE_001 | 429 | Too many requests. Try again later. | WARN |
| IDEMP_001 | 409 | Idempotency key was reused with different data. | WARN |
| IDEMP_002 | 409 | This operation is still being processed. | INFO |

## External Dependencies

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| EXT_001 | 503 | An external service is temporarily unavailable. | ERROR |
| EXT_002 | 504 | An external service timed out. | ERROR |
| EXT_003 | 502 | An external service returned an invalid response. | ERROR |
| EXT_004 | 503 | Object storage is temporarily unavailable. | ERROR |
| EXT_005 | 503 | Messaging service is temporarily unavailable. | ERROR |

## System and Data Integrity

| Code | HTTP | User message | Severity |
|---|---:|---|---|
| SYS_001 | 500 | Something went wrong. Please try again. | ERROR |
| SYS_002 | 503 | Service is temporarily unavailable. | ERROR |
| SYS_003 | 409 | Operation conflicts with the current resource state. | INFO |
| DATA_001 | 500 | A data consistency problem occurred. | CRITICAL |
| DATA_002 | 409 | Referenced resource does not exist. | WARN |
| DATA_003 | 409 | Duplicate resource detected. | WARN |

## Logging Policy

Logs for known business errors contain code, correlation ID, actor type, resource identifiers and outcome, but no secrets or sensitive child data. `INFO` errors are not automatically treated as incidents. `WARN` errors contribute to abuse and anomaly dashboards. `ERROR` and `CRITICAL` codes create operational metrics; critical codes may trigger immediate alerts.

## Client Handling

- `401`: refresh once where allowed, otherwise return to login.
- `403`: show the relevant access or entitlement explanation.
- `409`: refresh authoritative state before retrying.
- `429`: respect `Retry-After`.
- `5xx`: offer a safe retry without duplicating writes.
- Unknown codes: use a generic message and preserve the correlation ID for support.

## Change Management

Existing codes must never be silently reused for a different meaning. New codes are added here before or in the same change as implementation. Removing a code requires evidence that supported client versions no longer depend on it.
