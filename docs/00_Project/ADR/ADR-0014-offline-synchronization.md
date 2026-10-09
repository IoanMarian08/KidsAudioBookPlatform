# ADR-0014: Offline Synchronization Strategy

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture, Backend, and Mobile Engineering

## Context

Premium users may download stories and continue listening without connectivity. Playback progress, completion state, favorites, download metadata, and local queue state can change while the device is offline.

The synchronization model must avoid:

- data loss;
- duplicate commands;
- entitlement bypass;
- stale state overwriting newer state;
- confusing progress regression;
- corrupted or partially downloaded media;
- cross-profile data leakage;
- unbounded retry loops;
- inconsistent behavior across multiple devices.

Mobile connectivity is intermittent by design. Offline support is therefore a first-class architecture concern rather than an exception path.

## Decision

Use an offline-first mobile read model with:

- a durable local database;
- a durable local operation queue;
- server-authoritative reconciliation;
- explicit synchronization cursors;
- idempotent backend processing;
- versioned download manifests;
- deterministic conflict-resolution rules;
- encrypted or platform-protected local media storage;
- bounded offline entitlement behavior.

Security-sensitive decisions remain server-authoritative. The client may use previously issued offline metadata only within an explicitly defined validity window.

## Scope

The offline synchronization model applies to:

- downloaded story and episode metadata;
- media asset manifests;
- playback position;
- story completion;
- favorites;
- listening-session summaries;
- pending analytics where permitted;
- last successful synchronization cursor;
- local notification read state where supported;
- offline entitlement metadata.

The following remain online-only unless a future ADR changes the decision:

- profile creation and deletion;
- Parent Zone security changes;
- subscription purchase and restoration;
- billing state changes;
- account deletion;
- administrative actions;
- content publication;
- security-sensitive account changes.

## Local Data Model

The mobile application stores:

- downloaded story and episode identifiers;
- content and manifest versions;
- asset checksums and expected sizes;
- encrypted or platform-protected file references;
- playback position and completion state;
- favorites and user-action timestamps;
- pending synchronization operations;
- operation status and retry metadata;
- last successful synchronization cursor;
- last known entitlement expiry;
- device installation identifier;
- local database schema version.

Access tokens and refresh tokens use platform secure storage and are never stored in the local content database.

## Data Separation

All local records that belong to a child experience are scoped by:

- authenticated account identifier;
- child profile identifier;
- device installation identifier where relevant.

Switching accounts or removing a profile must prevent the next user from accessing previous local content or metadata. Account logout clears or locks protected local state according to the security policy.

## Operation Queue

Offline mutations are represented as durable operations.

Each operation contains:

```json
{
  "operationId": "01J...",
  "operationType": "PLAYBACK_PROGRESS_RECORDED",
  "accountId": "uuid",
  "profileId": "uuid",
  "aggregateId": "uuid",
  "clientSequence": 42,
  "clientOccurredAt": "2026-07-15T18:20:31Z",
  "baseVersion": 7,
  "payload": {},
  "retryCount": 0,
  "nextAttemptAt": null,
  "idempotencyKey": "01J..."
}
```

### Queue rules

1. Operations are persisted before the UI reports durable success.
2. Stable operation IDs survive application restart.
3. Operations are sent in bounded batches.
4. Ordering is preserved per aggregate when ordering matters.
5. Independent aggregates may synchronize concurrently within limits.
6. The backend stores or recognizes idempotency keys.
7. Retryable and permanent failures are distinguished explicitly.
8. A permanently rejected operation remains visible long enough for reconciliation and diagnostics.
9. Queue growth is bounded and monitored.
10. Security-sensitive operations are not queued offline.

## Operation States

Local queue entries use explicit states:

```text
PENDING
IN_FLIGHT
ACCEPTED
RETRYABLE_FAILURE
PERMANENTLY_REJECTED
SUPERSEDED
```

An operation must not remain indefinitely in `IN_FLIGHT`. On app restart, expired in-flight leases return to a retryable state.

## Synchronization Triggering

Synchronization may be triggered by:

- application start;
- authentication success;
- connectivity restoration;
- foreground transition;
- playback pause or completion;
- explicit user refresh;
- background execution where the operating system allows it;
- push notification indicating relevant server changes.

Triggers are coalesced to avoid duplicate concurrent synchronization sessions.

## Synchronization Protocol

The default protocol is:

1. Client confirms account and device context.
2. Client sends its last synchronization cursor and supported protocol versions.
3. Client submits queued operations in bounded batches.
4. Server validates authentication, profile ownership, entitlement, schema version, idempotency, and operation semantics.
5. Server applies accepted operations transactionally.
6. Server returns per-operation results.
7. Client requests or receives authoritative changes since its cursor.
8. Server returns a bounded change page and next cursor.
9. Client applies server changes in one local transaction.
10. Client advances the cursor only after successful local commit.
11. Client removes or archives acknowledged operations according to retention rules.

## Batch Response

The server returns explicit outcomes:

```json
{
  "results": [
    {
      "operationId": "01J...",
      "status": "ACCEPTED",
      "authoritativeVersion": 8
    },
    {
      "operationId": "01K...",
      "status": "RETRYABLE_FAILURE",
      "errorCode": "SYNC_503",
      "retryAfterSeconds": 30
    },
    {
      "operationId": "01L...",
      "status": "REJECTED",
      "errorCode": "ENTITLEMENT_EXPIRED"
    }
  ],
  "nextCursor": "cursor-token"
}
```

One invalid operation must not make the outcome of the entire batch ambiguous.

## Cursor Semantics

Synchronization cursors are opaque server-issued values.

Rules:

- clients do not construct or interpret cursors;
- cursors are scoped to account and profile context;
- cursors advance monotonically;
- a cursor is advanced locally only after all returned changes are committed;
- expired or invalid cursors trigger a bounded full resynchronization;
- cursor reset does not automatically delete valid downloaded media;
- cursor values are not logged at high verbosity when they could expose sensitive context.

## Conflict Resolution

Conflict resolution is defined by domain semantics rather than one universal timestamp rule.

### Playback progress

- Keep the furthest meaningful progress for normal forward listening.
- Never accept a position beyond episode duration.
- Preserve a newer explicit restart command.
- Treat client timestamps as advisory.
- Use server receipt time, operation sequence, and version metadata for deterministic resolution.

### Completion

- Completion is monotonic by default.
- An explicit restart does not silently erase completion history.
- A dedicated reset operation is required when product behavior supports reset.

### Favorites

- Apply the most recent accepted user action.
- Deduplicate repeated add or remove operations.
- Preserve the final authoritative state returned by the server.

### Profile and parental settings

- Server state wins.
- Sensitive settings are not editable offline.

### Entitlements

- Server state always wins.
- The client may use only a previously issued offline grant within its validity window.
- Revocation is applied at the next required reconciliation or earlier when a trusted push signal is received.

### Content metadata

- Published server version wins.
- Withdrawn or suspended content becomes unavailable according to policy.
- Client-local metadata is replaced transactionally.

## Multiple Devices

Each device maintains its own queue and cursor.

The backend resolves operations against shared authoritative account and profile state. The protocol must tolerate:

- progress created on two devices;
- a favorite removed on one device and added on another;
- downloaded content on a device after subscription expiry;
- account logout or session revocation on another device;
- replay of previously acknowledged operations.

No device is treated as the sole authoritative source.

## Download Authorization

Offline download is Premium-only.

Before download, the backend verifies:

- authenticated account;
- selected profile ownership;
- active entitlement or trial policy;
- device authorization;
- download-count or storage policy;
- story publication state;
- region and age eligibility;
- content version;
- application capability.

The backend returns a versioned manifest and short-lived download authorization.

## Download Manifest

A manifest contains:

```json
{
  "manifestVersion": 1,
  "downloadId": "uuid",
  "storyId": "uuid",
  "episodeId": "uuid",
  "contentVersion": 4,
  "issuedAt": "2026-07-15T18:20:31Z",
  "offlineValidUntil": "2026-07-22T18:20:31Z",
  "assets": [
    {
      "assetId": "uuid",
      "type": "AUDIO",
      "sizeBytes": 12345678,
      "checksumAlgorithm": "SHA-256",
      "checksum": "...",
      "downloadUrl": "signed-url"
    }
  ]
}
```

Signed URLs are short-lived and are not persisted in application logs.

## Download Lifecycle

```text
AUTHORIZED
QUEUED
DOWNLOADING
PAUSED
VERIFYING
AVAILABLE
FAILED
EXPIRED
REVOKED
REMOVED
```

### Rules

1. Partial downloads are resumable when provider support allows it.
2. File size and checksum are verified before availability.
3. Corrupted files are quarantined or removed.
4. A manifest is committed locally only after required assets are valid.
5. Insufficient-storage failures preserve recoverable state.
6. Content version changes mark the local copy stale.
7. Expired or revoked content is no longer playable after policy reconciliation.
8. Cleanup must not delete files actively used by the player.

## Offline Entitlement

Offline playback uses a bounded offline grant issued by the backend.

The grant is scoped to:

- account;
- device;
- story or plan capability;
- issue time;
- expiry time;
- manifest version;
- optional revocation generation.

The client must not extend or regenerate this grant.

When the grant expires:

- playback is blocked until successful reconciliation;
- already active playback may finish only if product policy explicitly permits it;
- the user receives a parent-appropriate explanation;
- the child interface avoids exposing billing details.

## Authentication and Session Expiry

Offline media access does not make the account session permanently valid.

Rules:

- secure local state is bound to the authenticated account;
- revoked sessions are honored when the device reconnects;
- logout removes or locks account-scoped offline data;
- refresh-token failure does not expose another user's local content;
- Parent Zone operations remain unavailable without required verification.

## Retry Policy

Retryable failures include transient network, timeout, rate-limit, and temporary service-unavailable responses.

Retries use:

- exponential backoff;
- jitter;
- server-provided `Retry-After` when present;
- maximum retry delay;
- maximum automatic retry count for individual attempts;
- continued durable retention for unresolved operations where appropriate.

Permanent validation, ownership, entitlement, and unsupported-version failures are not retried indefinitely.

## Failure Recovery

### Local database failure

The application attempts safe recovery without losing server-reconstructable state. Destructive reset is a last resort and must not silently preserve inaccessible orphaned media.

### Corrupted queue entry

The entry is isolated, recorded with a safe diagnostic reason, and does not block unrelated operations.

### Invalid cursor

The client performs bounded full resynchronization.

### Server partial failure

Each operation retains an explicit status. The client retries only unresolved retryable operations.

### Application termination during sync

Local transactions and in-flight leases ensure that restart resumes from the last committed state.

## Local Database Migrations

The local database has explicit schema versions and deterministic migrations.

Migration tests cover:

- supported app upgrade paths;
- preservation of queued operations;
- preservation of valid download metadata;
- cleanup of obsolete records;
- recovery from migration interruption where supported;
- account and profile scoping.

## Security

- Local media uses application-private storage.
- Sensitive metadata is encrypted or protected using platform capabilities.
- Tokens are stored only in platform secure storage.
- Raw PINs, passwords, purchase receipts, and child personal data are never placed in queue diagnostics.
- File paths and manifests must not permit path traversal.
- Downloaded assets are never exposed through public shared-storage locations by default.
- Server validation is repeated for every synchronized operation.
- Operation IDs and cursors are treated as untrusted input.

## Privacy and Retention

Local data is minimized to what is necessary for the selected feature.

On profile or account deletion:

- pending operations are cancelled or reconciled according to policy;
- local metadata is removed;
- media assets are deleted;
- secure-storage references are cleared;
- audit evidence remains only on the server where legally or operationally required.

Acknowledged queue entries are retained locally only for a bounded diagnostic period.

## Observability

Track:

- queue depth;
- oldest pending operation age;
- synchronization duration;
- batch size;
- accepted, rejected, and retryable operations;
- conflict counts by type;
- invalid cursor count;
- full-resynchronization count;
- repeated retries;
- download success and failure rate;
- checksum failures;
- corrupted downloads;
- offline entitlement expiry;
- local database migration failures;
- offline playback-start success rate.

Logs contain correlation identifiers and safe resource identifiers, but no raw tokens, signed URLs, PINs, or unnecessary child data.

## Testing Strategy

Required tests include:

- queue persistence across app restart;
- duplicate-operation delivery;
- out-of-order operation delivery;
- multi-device progress conflicts;
- explicit restart behavior;
- cursor pagination and reset;
- partial batch failure;
- expired entitlement;
- subscription revocation;
- partial and resumed downloads;
- checksum mismatch;
- insufficient storage;
- account switching;
- profile deletion;
- local database migration;
- old client protocol compatibility;
- intermittent connectivity during playback and synchronization.

## Operational Controls

Operations may configure:

- batch-size limits;
- retry intervals;
- maximum concurrent downloads;
- offline-validity duration;
- synchronization timeout;
- forced manifest refresh;
- minimum supported synchronization protocol;
- emergency disablement of new downloads.

Configuration changes are audited. Security and entitlement rules cannot be weakened solely through client configuration.

## Consequences

### Positive

- Reliable offline playback.
- Reduced risk of duplicate mutations.
- Deterministic conflict handling.
- Clear server authority for sensitive state.
- Recoverable mobile operation queue.
- Safer multi-device behavior.
- Explicit download integrity verification.

### Negative

- More complex mobile persistence and testing.
- Eventual consistency between device and server.
- Additional local-database migrations.
- More operational metrics and reconciliation paths.
- Temporary stale state is unavoidable while offline.

## Rejected Alternatives

### Last-write-wins for every field

Rejected because timestamps alone can regress playback, lose completion, and behave unpredictably across devices.

### Direct API calls without a durable queue

Rejected because process termination or connectivity loss would silently lose offline changes.

### Fully client-authoritative entitlement

Rejected because it creates unacceptable security and revenue risk.

### Store media without a versioned manifest

Rejected because integrity, expiry, revocation, and content-version reconciliation would be unreliable.

### One global synchronization cursor for all users and profiles

Rejected because it complicates isolation, account switching, and targeted recovery.

## Follow-up Actions

- Define the synchronization API in `API_Specification.md`.
- Add synchronization errors to `Error_Catalog.md`.
- Add operation and reconciliation events to `Event_Catalog.md` where needed.
- Implement local queue and database migration tests in Flutter.
- Define the production offline-validity policy with Product and Security.
- Add download integrity and entitlement-revocation end-to-end tests.
- Create dashboards for queue age, conflicts, sync failures, and corrupted downloads.
