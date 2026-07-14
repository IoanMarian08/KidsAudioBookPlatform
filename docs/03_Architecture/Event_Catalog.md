# Event Catalog

Version: 1.1.0  
Status: Active Draft  
Owner: Project Architecture  
Last updated: 2026-07-15

## 1. Purpose

This document defines the canonical asynchronous event contracts used by KidsAudioBookPlatform. It is the source of truth for event names, ownership, producers, consumers, delivery semantics, payload expectations, routing, retries, replay, retention, observability, and schema evolution.

Events are immutable facts that describe something which has already happened. Commands, requests, implementation instructions, and mutable snapshots are not published as domain events.

This catalog complements:

- `Software_Architecture.md` for module and service boundaries;
- `System_Flows.md` for end-to-end behavior;
- `API_Specification.md` for synchronous contracts;
- `Database_Design.md` for authoritative persistence;
- `Error_Catalog.md` for error semantics;
- `Logging_Monitoring.md` for operational telemetry.

## 2. Event Categories

### 2.1 Domain events

Domain events represent meaningful business facts owned by one bounded context, for example `StoryPublished`, `SubscriptionActivated`, or `ChildProfileDeleted`.

They may be consumed by other modules, projections, workers, analytics, notifications, and future extracted services.

### 2.2 Integration events

Integration events are stable externalized contracts derived from domain events. In the modular-monolith stage, a domain event and its integration representation may be produced by the same transaction, but external consumers depend only on the integration contract documented here.

### 2.3 Operational events

Operational events describe infrastructure or workflow outcomes such as `MediaProcessingFailed`, `NotificationDeliveryFailed`, or `ScheduledJobCompleted`. They support retries, alerting, audit, and operations but do not replace metrics or logs.

### 2.4 Events that must not be published

The platform must not publish:

- commands such as `PublishStoryNow`;
- database row dumps;
- access tokens, refresh tokens, PINs, passwords, receipts, or signed media URLs;
- internal exception objects or stack traces;
- high-frequency UI telemetry as domain events;
- fields without a defined business meaning or retention purpose.

## 3. Canonical Envelope

```json
{
  "eventId": "01J2M7K9C8Y8G7H6F5E4D3C2B1",
  "eventType": "StoryPublished",
  "eventVersion": 1,
  "occurredAt": "2026-07-15T18:20:31.245Z",
  "publishedAt": "2026-07-15T18:20:31.612Z",
  "producer": "catalog",
  "correlationId": "01J2M7H2M6A6N3B8T7Q4P5R9X1",
  "causationId": "01J2M7F4A8D2S6G9H1J3K5L7Z0",
  "actor": {
    "type": "ADMIN",
    "id": "8a894d95-67cb-4685-9549-b23ba3f75cc9"
  },
  "subject": {
    "type": "STORY",
    "id": "514558dd-dc09-424b-b742-d6aa9371354f"
  },
  "partitionKey": "514558dd-dc09-424b-b742-d6aa9371354f",
  "dataClassification": "INTERNAL",
  "payload": {}
}
```

### 3.1 Required envelope fields

| Field | Requirement |
|---|---|
| `eventId` | Globally unique ULID or UUID generated once and preserved during retries |
| `eventType` | Stable PascalCase name written in past tense |
| `eventVersion` | Positive integer identifying the payload contract version |
| `occurredAt` | UTC timestamp when the business fact became true |
| `publishedAt` | UTC timestamp when the broker publication occurred |
| `producer` | Stable bounded-context or service identifier |
| `correlationId` | Identifier shared across the initiating request and resulting work |
| `causationId` | Request, command, job, or prior event that caused this event |
| `partitionKey` | Stable key used when ordering for one aggregate or subject matters |
| `dataClassification` | `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, or `RESTRICTED` |
| `payload` | Versioned event-specific object |

### 3.2 Optional envelope fields

`actor` and `subject` are included when their meaning is known and safe to expose. System-generated events use actor type `SYSTEM` or `SCHEDULED_JOB`. Anonymous child-facing behavior must not introduce unnecessary personal identifiers.

### 3.3 Envelope rules

- `eventId` never changes during retry, redelivery, dead-lettering, or replay.
- `occurredAt` is the business time; `publishedAt` is transport time.
- consumers must not infer event order from wall-clock timestamps alone;
- payload fields use camelCase;
- identifiers are opaque strings;
- timestamps use ISO 8601 UTC with milliseconds where available;
- enum values use stable uppercase snake case;
- monetary values use decimal strings and an explicit ISO currency code;
- unknown optional fields must be ignored by consumers;
- missing required fields fail schema validation and are not processed.

## 4. Delivery Contract

RabbitMQ provides at-least-once delivery. Exactly-once processing is not assumed.

Every consumer must therefore:

1. identify the event through `eventId`;
2. reject an unsupported schema version safely;
3. check whether the event was already applied;
4. apply the state transition and deduplication record in one transaction where practical;
5. acknowledge only after successful durable processing;
6. classify failures as transient or permanent;
7. expose processing latency, retry count, and outcome metrics.

Producer-side publication uses the transactional outbox pattern. A successful domain transaction and its outbox record commit atomically. A relay publishes pending records and marks them published only after broker confirmation.

## 5. Ordering and Concurrency

Global event ordering is not guaranteed.

Ordering is required only within a documented subject boundary, such as:

- subscription lifecycle for one `subscriptionId`;
- publication lifecycle for one `storyId`;
- media processing lifecycle for one `mediaAssetId`;
- account deletion lifecycle for one `accountId`.

Consumers must use aggregate version, sequence, effective timestamp, or current authoritative state when later delivery could otherwise revert newer data.

Events for unrelated subjects may be processed concurrently. A consumer must not require one queue to serialize the entire platform.

## 6. Idempotency and Deduplication

The default deduplication key is `(consumerName, eventId)`.

Rules:

- duplicate delivery returns a successful no-op outcome;
- deduplication records are written transactionally with consumer state where possible;
- retention of deduplication records must exceed broker retry and replay windows;
- an event reused with a different payload is a critical integrity violation;
- provider events use both platform `eventId` and provider-specific identifiers where available;
- side effects such as email, push, webhook, or object deletion require their own idempotency key.

## 7. Identity Events

### 7.1 AccountRegistered

Producer: Identity  
Consumers: Notifications, Analytics  
Partition key: `accountId`

```json
{
  "accountId": "uuid",
  "emailVerificationRequired": true,
  "locale": "ro-RO",
  "registeredAt": "2026-07-15T18:20:31Z"
}
```

The event does not contain a password, verification token, or full email address. Notification workers resolve protected delivery data through an authorized internal interface.

### 7.2 AccountVerified

Producer: Identity  
Consumers: Notifications, Analytics  
Required payload: `accountId`, `verifiedAt`

### 7.3 AccountLocked

Producer: Identity  
Consumers: Security Monitoring, Notifications  
Required payload: `accountId`, `reason`, `lockedUntil`, `securityEventId`

### 7.4 AccountUnlocked

Producer: Identity  
Consumers: Security Monitoring, Notifications  
Required payload: `accountId`, `reason`, `unlockedAt`

### 7.5 SessionRevoked

Producer: Identity  
Consumers: Security Monitoring, Device Session Projection  
Required payload: `accountId`, `sessionId`, `reason`, `revokedAt`

### 7.6 AccountDeletionRequested

Producer: Identity  
Consumers: Privacy Worker, Notifications, Audit  
Required payload: `accountId`, `deletionRequestId`, `requestedAt`, `scheduledExecutionAt`

### 7.7 AccountDeletionCompleted

Producer: Privacy Worker  
Consumers: Identity, Audit, Operations  
Required payload: `accountId`, `deletionRequestId`, `completedAt`, `retainedRecordCategories`

The payload must not contain deleted personal data.

## 8. Profile Events

### 8.1 ChildProfileCreated

Producer: Profiles  
Consumers: Recommendations, Analytics, Cache Invalidation  
Partition key: `profileId`

```json
{
  "accountId": "uuid",
  "profileId": "uuid",
  "ageBand": "AGE_3_5",
  "locale": "ro-RO",
  "createdAt": "2026-07-15T18:20:31Z"
}
```

### 8.2 ChildProfileUpdated

Producer: Profiles  
Consumers: Recommendations, Cache Invalidation, Download Reconciliation  
Required payload: `accountId`, `profileId`, `changedFields`, `profileVersion`, `updatedAt`

The event contains only changed field names and safe projection values. It does not carry free-form personal text unless a consumer has a documented need.

### 8.3 ChildProfileArchived

Producer: Profiles  
Consumers: Playback, Recommendations, Downloads, Cache Invalidation  
Required payload: `accountId`, `profileId`, `archivedAt`

### 8.4 ChildProfileDeleted

Producer: Profiles  
Consumers: Playback Cleanup, Recommendations, Privacy Worker, Downloads  
Required payload: `accountId`, `profileId`, `deletedAt`

## 9. Catalog and Publishing Events

### 9.1 StoryDraftCreated

Producer: Catalog  
Consumers: Audit, Admin Projections  
Required payload: `storyId`, `draftVersionId`, `locale`, `createdAt`

### 9.2 StoryVersionSubmittedForReview

Producer: Catalog  
Consumers: Admin Projections, Notifications  
Required payload: `storyId`, `versionId`, `submittedBy`, `submittedAt`

### 9.3 StoryVersionApproved

Producer: Catalog  
Consumers: Admin Projections, Audit  
Required payload: `storyId`, `versionId`, `approvedBy`, `approvedAt`

### 9.4 StoryPublicationScheduled

Producer: Catalog  
Consumers: Publication Scheduler, Admin Projections  
Required payload: `storyId`, `versionId`, `scheduledFor`, `timezone`

### 9.5 StoryPublished

Producer: Catalog  
Consumers: Cache Invalidation, Recommendations, Notifications, Search Projection, Analytics  
Partition key: `storyId`

```json
{
  "storyId": "uuid",
  "versionId": "uuid",
  "locale": "ro-RO",
  "ageBands": ["AGE_3_5", "AGE_6_7"],
  "contentTier": "FREE",
  "publishedAt": "2026-07-15T18:20:31Z",
  "catalogVersion": 12
}
```

Titles and descriptions are omitted unless a consumer explicitly requires localized display data. Consumers should retrieve authoritative catalog projections rather than treating event payloads as complete content records.

### 9.6 StoryUnpublished

Producer: Catalog  
Consumers: Cache Invalidation, Search Projection, Download Reconciliation, Playback  
Required payload: `storyId`, `versionId`, `reason`, `effectiveAt`, `catalogVersion`

### 9.7 StoryVersionRolledBack

Producer: Catalog  
Consumers: Cache Invalidation, Audit, Search Projection, Download Reconciliation  
Required payload: `storyId`, `fromVersionId`, `toVersionId`, `reason`, `rolledBackAt`

### 9.8 CollectionPublished

Producer: Catalog  
Consumers: Cache Invalidation, Search Projection, Notifications  
Required payload: `collectionId`, `locale`, `publishedAt`, `catalogVersion`

## 10. Media Events

### 10.1 MediaUploadAuthorized

Producer: Media  
Consumers: Audit, Security Monitoring  
Required payload: `mediaAssetId`, `mediaType`, `uploadExpiresAt`, `expectedContentType`, `maximumBytes`

No signed upload URL is included in the event.

### 10.2 MediaUploaded

Producer: Media  
Consumers: Malware Scan, Media Processing  
Partition key: `mediaAssetId`

```json
{
  "mediaAssetId": "uuid",
  "mediaType": "AUDIO",
  "objectKey": "opaque-key",
  "sizeBytes": 10485760,
  "checksumAlgorithm": "SHA_256",
  "checksum": "hex-value",
  "uploadedAt": "2026-07-15T18:20:31Z"
}
```

### 10.3 MediaScanCompleted

Producer: Media Security Worker  
Consumers: Catalog, Media Processing, Admin Projections, Security Monitoring  
Required payload: `mediaAssetId`, `result`, `scannerVersion`, `completedAt`

### 10.4 MediaProcessingCompleted

Producer: Media Worker  
Consumers: Catalog, Admin Projections  
Required payload: `mediaAssetId`, `derivedAssetIds`, `technicalMetadata`, `completedAt`

### 10.5 MediaProcessingFailed

Producer: Media Worker  
Consumers: Retry Scheduler, Admin Projections, Operations Monitoring  
Required payload: `mediaAssetId`, `failureCode`, `retryable`, `attempt`, `failedAt`

## 11. Playback and Progress Events

### 11.1 ListeningSessionStarted

Producer: Playback  
Consumers: Analytics, Advertising Eligibility  
Partition key: `profileId`

Required payload: `accountId`, `profileId`, `storyId`, `episodeId`, `sessionId`, `startedAt`, `accessMode`.

### 11.2 ListeningProgressUpdated

Producer: Playback  
Consumers: Recommendations, Analytics, Continue Listening Projection  
Required payload: `profileId`, `storyId`, `episodeId`, `sessionId`, `positionMs`, `durationMs`, `progressVersion`, `updatedAt`

This event may be sampled or compacted for analytics. The authoritative progress state remains in PostgreSQL. Consumers must reject a lower `progressVersion` after a higher version has already been applied.

### 11.3 StoryCompleted

Producer: Playback  
Consumers: Recommendations, Analytics, Achievements, Advertising Eligibility

```json
{
  "accountId": "uuid",
  "profileId": "uuid",
  "storyId": "uuid",
  "episodeId": "uuid",
  "sessionId": "uuid",
  "completedAt": "2026-07-15T18:20:31Z"
}
```

### 11.4 ListeningSessionEnded

Producer: Playback  
Consumers: Analytics, Advertising Eligibility  
Required payload: `accountId`, `profileId`, `sessionId`, `endReason`, `listenedDurationMs`, `endedAt`

## 12. Subscription and Entitlement Events

### 12.1 PurchaseVerificationRequested

Producer: Subscriptions  
Consumers: Purchase Verification Worker  
Required payload: `verificationRequestId`, `accountId`, `provider`, `providerTransactionReference`, `requestedAt`

Sensitive raw receipts and purchase tokens remain encrypted in authoritative storage and are referenced indirectly.

### 12.2 SubscriptionActivated

Producer: Subscriptions  
Consumers: Entitlements, Notifications, Analytics  
Partition key: `subscriptionId`

Required payload: `accountId`, `subscriptionId`, `provider`, `productId`, `effectiveAt`, `expiresAt`, `subscriptionVersion`.

### 12.3 SubscriptionRenewed

Producer: Subscriptions  
Consumers: Entitlements, Analytics, Notifications  
Required payload: `accountId`, `subscriptionId`, `previousExpiry`, `newExpiry`, `renewedAt`, `subscriptionVersion`

### 12.4 SubscriptionGracePeriodStarted

Producer: Subscriptions  
Consumers: Entitlements, Notifications  
Required payload: `accountId`, `subscriptionId`, `gracePeriodEndsAt`, `subscriptionVersion`

### 12.5 SubscriptionExpired

Producer: Subscriptions  
Consumers: Entitlements, Download Reconciliation, Notifications  
Required payload: `accountId`, `subscriptionId`, `effectiveAt`, `subscriptionVersion`

### 12.6 SubscriptionRevoked

Producer: Subscriptions  
Consumers: Entitlements, Security Monitoring, Download Reconciliation, Notifications

```json
{
  "accountId": "uuid",
  "subscriptionId": "uuid",
  "provider": "GOOGLE_PLAY",
  "effectiveAt": "2026-07-15T18:20:31Z",
  "reason": "REFUND",
  "subscriptionVersion": 9
}
```

### 12.7 EntitlementsRecalculated

Producer: Entitlements  
Consumers: Cache Invalidation, Downloads, Mobile Sync Projection  
Required payload: `accountId`, `entitlementVersion`, `effectiveCapabilities`, `recalculatedAt`

The payload includes capability identifiers, not provider receipt details.

## 13. Download and Offline Events

### 13.1 OfflineDownloadAuthorized

Producer: Downloads  
Consumers: Analytics, Security Monitoring  
Required payload: `downloadAuthorizationId`, `accountId`, `profileId`, `deviceId`, `storyId`, `expiresAt`

### 13.2 OfflineDownloadCompleted

Producer: Downloads  
Consumers: Analytics, Storage Quota Projection  
Required payload: `downloadId`, `profileId`, `deviceId`, `storyId`, `contentVersion`, `completedAt`

### 13.3 OfflineDownloadRemoved

Producer: Downloads  
Consumers: Analytics, Storage Quota Projection  
Required payload: `downloadId`, `deviceId`, `reason`, `removedAt`

### 13.4 OfflineEntitlementRevoked

Producer: Entitlements  
Consumers: Download Reconciliation, Notifications, Mobile Sync Projection  
Required payload: `accountId`, `deviceIds`, `reason`, `effectiveAt`, `entitlementVersion`

## 14. Advertising Events

### 14.1 AdEligibilityEvaluated

Producer: Advertising Eligibility  
Consumers: Analytics, Audit Projection  
Required payload: `accountId`, `profileId`, `sessionId`, `eligible`, `decisionReason`, `policyVersion`, `evaluatedAt`

No behavioral profile beyond the minimum policy inputs is included.

### 14.2 AdImpressionReported

Producer: Mobile Ad Adapter  
Consumers: Advertising Eligibility, Analytics  
Required payload: `impressionId`, `accountId`, `sessionId`, `provider`, `placement`, `reportedAt`

### 14.3 AdAttemptFailed

Producer: Mobile Ad Adapter  
Consumers: Analytics, Operations Monitoring  
Required payload: `attemptId`, `provider`, `failureCategory`, `retryable`, `failedAt`

An advertising failure must never block story playback.

## 15. Notification Events

### 15.1 NotificationCreated

Producer: Notifications  
Consumers: Delivery Workers, In-App Projection  
Partition key: `notificationId`

Required payload: `notificationId`, `accountId`, `templateKey`, `locale`, `channels`, `scheduledFor`.

### 15.2 NotificationDeliveryRequested

Producer: Notifications  
Consumers: Channel Delivery Worker  
Required payload: `notificationId`, `deliveryAttemptId`, `channel`, `scheduledFor`

### 15.3 NotificationDelivered

Producer: Delivery Worker  
Consumers: Analytics, Notification Projection  
Required payload: `notificationId`, `deliveryAttemptId`, `channel`, `providerMessageId`, `deliveredAt`

### 15.4 NotificationFailed

Producer: Delivery Worker  
Consumers: Retry Scheduler, Operations Monitoring, Notification Projection

```json
{
  "notificationId": "uuid",
  "deliveryAttemptId": "uuid",
  "channel": "PUSH",
  "provider": "FCM",
  "failureCode": "TOKEN_INVALID",
  "retryable": false,
  "attempt": 1,
  "failedAt": "2026-07-15T18:20:31Z"
}
```

### 15.5 NotificationRead

Producer: Notifications  
Consumers: Analytics, In-App Projection  
Required payload: `notificationId`, `accountId`, `readAt`

## 16. Administration and Audit Events

### 16.1 AdminActionRecorded

Producer: Administration  
Consumers: Audit Projection, Security Monitoring  
Required payload: `auditRecordId`, `adminId`, `action`, `resourceType`, `resourceId`, `outcome`, `recordedAt`

Sensitive before-and-after values are stored in the protected audit system and are not copied broadly through RabbitMQ.

### 16.2 AdminRoleChanged

Producer: Administration  
Consumers: Identity, Security Monitoring, Audit Projection  
Required payload: `adminId`, `changedBy`, `previousRoles`, `newRoles`, `changedAt`

### 16.3 SupportOverrideApplied

Producer: Administration  
Consumers: Entitlements, Audit Projection, Security Monitoring  
Required payload: `overrideId`, `accountId`, `capability`, `expiresAt`, `reasonCode`, `appliedBy`, `appliedAt`

## 17. Operational Events

### 17.1 ScheduledJobStarted

Producer: Scheduler  
Consumers: Operations Projection  
Required payload: `jobExecutionId`, `jobName`, `scheduledAt`, `startedAt`

### 17.2 ScheduledJobCompleted

Producer: Scheduler  
Consumers: Operations Projection, Metrics Aggregator  
Required payload: `jobExecutionId`, `jobName`, `processedCount`, `succeededCount`, `failedCount`, `completedAt`

### 17.3 ScheduledJobFailed

Producer: Scheduler  
Consumers: Retry Scheduler, Operations Monitoring  
Required payload: `jobExecutionId`, `jobName`, `failureCode`, `retryable`, `failedAt`

### 17.4 DeadLetterMessageCreated

Producer: Messaging Operations  
Consumers: Operations Monitoring, Audit  
Required payload: `deadLetterId`, `originalEventId`, `consumer`, `routingKey`, `failureCategory`, `attempts`, `deadLetteredAt`

The original sensitive payload is retained only in protected broker or operational storage, not duplicated into this event.

## 18. RabbitMQ Topology

Recommended topic exchanges:

- `identity.events`;
- `profiles.events`;
- `catalog.events`;
- `media.events`;
- `playback.events`;
- `subscriptions.events`;
- `entitlements.events`;
- `downloads.events`;
- `advertising.events`;
- `notifications.events`;
- `administration.events`;
- `operations.events`.

Routing keys use lowercase dot notation:

```text
catalog.story.published.v1
subscriptions.subscription.revoked.v1
media.asset.processing-failed.v1
notifications.delivery.failed.v1
```

Queue names identify the consumer and purpose rather than copying the producer name:

```text
recommendations.story-published.v1
entitlements.subscription-lifecycle.v1
downloads.entitlement-reconciliation.v1
operations.notification-failures.v1
```

Each consumer owns its queues, retry queues, dead-letter queues, alert thresholds, and replay procedure.

## 19. Retry and Dead-Letter Policy

Failures are classified as:

- **transient**: timeout, temporary dependency failure, rate limit, unavailable lock;
- **permanent contract**: invalid schema, unsupported version, missing required field;
- **permanent business**: referenced entity intentionally deleted, operation no longer applicable;
- **integrity or security**: payload mismatch for reused event ID, impossible lifecycle regression, unauthorized data.

Rules:

- retry only transient failures;
- use exponential backoff with jitter;
- keep attempts bounded by consumer-specific policy;
- acknowledge successful no-op duplicates;
- invalid schemas go directly to dead letter after validation failure;
- integrity and security failures trigger immediate operational alerts;
- dead-letter entries preserve original routing metadata and failure reason;
- replay requires operator authorization, reason, scope, and audit record;
- replay must not generate a new business fact unless the original consumer action truly failed.

## 20. Replay and Backfill

Replay is used to rebuild projections, recover from a consumer defect, or process a newly introduced consumer.

Before replay:

1. define exact event types, versions, subjects, and time range;
2. confirm consumer idempotency;
3. estimate load and external side effects;
4. disable unsafe outbound actions or use dry-run mode;
5. capture approval and rollback plan;
6. monitor throughput, errors, lag, and duplicates.

Backfills generated from authoritative database state use a distinct documented process and must not impersonate historical events without marking their origin. Synthetic replay events include replay metadata in protected headers, not in business payloads.

## 21. Retention

Retention depends on purpose:

| Data | Minimum expectation |
|---|---|
| Active broker queues | Long enough for bounded retry and operational recovery |
| Dead-letter queues | Long enough for investigation and authorized replay |
| Outbox records | Until confirmed publication plus operational retention window |
| Consumer deduplication records | Longer than replay and redelivery window |
| Audit-relevant event references | According to audit and legal retention policy |
| Analytics event copies | According to privacy, minimization, and aggregation policy |

The broker is not the permanent system of record. PostgreSQL remains authoritative for domain state.

## 22. Privacy and Security

- events contain the minimum data required by documented consumers;
- child names, free-form profile text, raw email addresses, tokens, receipts, and credentials are excluded by default;
- restricted payloads use encrypted transport and access-controlled queues;
- logs record event ID, type, version, producer, consumer, outcome, and timing but not sensitive payloads;
- consumer access follows least privilege;
- exports, replays, and dead-letter inspection are audited;
- retention and deletion obligations apply to event stores and analytics copies, not only transactional tables.

## 23. Schema Evolution

Compatible additions may keep the same event version when:

- fields are optional;
- existing meaning is unchanged;
- consumers ignore unknown fields;
- defaults are unambiguous.

A new event version is required when:

- a field is removed or renamed;
- a type changes;
- optional becomes required;
- enum meaning changes incompatibly;
- business semantics change;
- partitioning or ordering meaning changes.

During migration:

1. document the new schema;
2. publish contract fixtures;
3. update consumer contract tests;
4. deploy tolerant consumers first;
5. enable the producer version;
6. observe adoption and failures;
7. retire the old version only after supported consumers no longer require it.

Event names are never reused for a different fact.

## 24. Contract Testing

CI must validate:

- envelope schema;
- event-specific required fields;
- enum compatibility;
- representative producer serialization;
- consumer deserialization of current and supported prior versions;
- unknown optional field tolerance;
- duplicate delivery behavior;
- retry and dead-letter classification;
- absence of prohibited sensitive fields;
- routing-key and queue-binding correctness where configuration is code-managed.

Canonical JSON fixtures should be version-controlled alongside implementation contracts.

## 25. Observability

Producer metrics:

- outbox pending count and oldest age;
- publication attempts and failures;
- broker confirmation latency;
- event count by type and version.

Consumer metrics:

- delivery count;
- success, duplicate, retry, permanent failure, and dead-letter outcomes;
- processing latency;
- queue depth and oldest-message age;
- unsupported-version count;
- replay throughput.

Every processing log includes `eventId`, `eventType`, `eventVersion`, `producer`, `consumer`, `correlationId`, attempt, outcome, and duration.

## 26. Ownership and Change Management

The producing bounded context owns the event name, schema, meaning, and publication timing. Consumers may not redefine its semantics or depend on undocumented fields.

Any event change requires:

- owner approval;
- catalog update;
- schema or fixture update;
- affected consumer review;
- compatibility assessment;
- contract-test coverage;
- rollout and rollback plan for incompatible changes.

A new event is implementation-ready only when its producer, consumers, partition key, payload, privacy classification, retry behavior, retention need, metrics, and versioning strategy are defined.