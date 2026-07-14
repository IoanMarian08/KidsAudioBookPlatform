# ADR-0014: Offline Synchronization Strategy

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture, Backend, and Mobile Engineering

## Context

Premium users may download stories and continue listening without connectivity. Playback progress, completion state, favorites, and download metadata can change while the device is offline. The synchronization model must avoid data loss, duplicate commands, entitlement bypass, and confusing regressions in progress.

## Decision

Use an offline-first mobile read model with a durable local operation queue and server-authoritative reconciliation. Media files are stored locally only after entitlement and manifest validation. Security-sensitive decisions remain server-authoritative.

## Local Data

The mobile application stores:

- downloaded story and episode metadata;
- encrypted or platform-protected media references;
- playback position and completion state;
- pending synchronization operations;
- last successful synchronization cursor;
- last known entitlement expiry required for offline grace handling.

Access tokens and refresh tokens use platform secure storage and are never stored in the local content database.

## Operation Queue

Offline mutations are represented as durable operations containing:

- operation ID;
- operation type;
- aggregate ID;
- child profile ID;
- client timestamp;
- payload;
- retry count;
- idempotency key.

Operations are sent in order where ordering matters and retried with exponential backoff. The backend records idempotency keys to prevent duplicate application.

## Conflict Resolution

- Playback progress: keep the furthest meaningful progress unless the user explicitly restarts a story.
- Completion: completed state is monotonic unless explicitly reset through a dedicated command.
- Favorites: use the most recent accepted user action.
- Profile and parental settings: server state wins; offline editing of sensitive settings is not supported.
- Entitlements: server state wins, with a limited documented offline grace period.

## Synchronization Protocol

1. Client authenticates or uses a still-valid offline session state.
2. Client submits queued operations in bounded batches.
3. Server validates identity, profile ownership, entitlement, idempotency, and version information.
4. Server returns accepted, rejected, and retryable results.
5. Client requests changes since its last synchronization cursor.
6. Client applies server changes transactionally and advances the cursor.

## Downloads

A download manifest includes media identifiers, checksums, sizes, content version, entitlement requirements, and expiry behavior. Partial downloads must be resumable. Corrupted files are removed and downloaded again. Revoked or expired content becomes unavailable according to subscription policy.

## Observability

Track queue depth, sync duration, rejected operations, conflict counts, repeated retries, corrupted downloads, and offline playback failures. Logs must not contain child personal data or raw tokens.

## Consequences

### Positive

- Reliable offline playback.
- Reduced risk of duplicate mutations.
- Clear ownership of conflict resolution.
- Backend remains authoritative for security-sensitive state.

### Negative

- More complex mobile persistence and testing.
- Eventual consistency between device and server.
- Additional migration requirements for the local database.

## Rejected Alternatives

- Last-write-wins for every field: can regress progress and lose completion state.
- Direct API calls without a durable queue: loses offline changes.
- Fully client-authoritative entitlement: unacceptable security and revenue risk.