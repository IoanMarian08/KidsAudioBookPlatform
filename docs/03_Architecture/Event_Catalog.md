# Event Catalog

Version: 1.0.0  
Status: Draft

## Purpose

This document defines the canonical asynchronous events used by KidsAudioBookPlatform. Events are immutable facts. Commands are not published as events.

## Envelope

```json
{
  "eventId": "01J...",
  "eventType": "StoryPublished",
  "eventVersion": 1,
  "occurredAt": "2026-07-14T18:20:31Z",
  "producer": "catalog",
  "correlationId": "01J...",
  "causationId": "01J...",
  "tenantId": null,
  "payload": {}
}
```

Required rules:
- `eventId` is globally unique.
- `eventType` is stable and past tense.
- `eventVersion` changes only for incompatible schema evolution.
- consumers must be idempotent.
- sensitive data must not be included unless strictly necessary.
- publication uses the transactional outbox.
- poison messages move to a dead-letter queue after bounded retries.

## Identity Events

### AccountRegistered
Producer: Identity  
Consumers: Notifications, Analytics

```json
{
  "accountId": "uuid",
  "emailVerificationRequired": true,
  "locale": "ro-RO"
}
```

### AccountVerified
Producer: Identity  
Consumers: Notifications, Analytics

### AccountLocked
Producer: Identity  
Consumers: Security Monitoring, Notifications

### AccountDeletionRequested
Producer: Identity  
Consumers: Privacy Worker, Notifications, Audit

## Profile Events

### ChildProfileCreated
Producer: Profiles  
Consumers: Recommendations, Analytics

```json
{
  "accountId": "uuid",
  "profileId": "uuid",
  "ageBand": "AGE_3_5",
  "createdAt": "2026-07-14T18:20:31Z"
}
```

### ChildProfileUpdated
Producer: Profiles  
Consumers: Recommendations, Cache Invalidation

### ChildProfileDeleted
Producer: Profiles  
Consumers: Playback Cleanup, Recommendations, Privacy Worker

## Catalog Events

### StoryDraftCreated
Producer: Catalog  
Consumers: Audit, Admin Projections

### StoryVersionApproved
Producer: Catalog  
Consumers: Admin Projections

### StoryPublished
Producer: Catalog  
Consumers: Cache Invalidation, Recommendations, Notifications, Search Projection

```json
{
  "storyId": "uuid",
  "versionId": "uuid",
  "title": "The Moon Rabbit",
  "locale": "ro-RO",
  "ageBands": ["AGE_3_5", "AGE_6_7"],
  "publishedAt": "2026-07-14T18:20:31Z"
}
```

### StoryUnpublished
Producer: Catalog  
Consumers: Cache Invalidation, Search Projection, Download Reconciliation

### StoryVersionRolledBack
Producer: Catalog  
Consumers: Cache Invalidation, Audit, Search Projection

## Playback Events

### ListeningSessionStarted
Producer: Playback  
Consumers: Analytics, Ads Eligibility

### ListeningProgressUpdated
Producer: Playback  
Consumers: Recommendations, Analytics

This event may be sampled or compacted for analytics. The authoritative progress state remains in PostgreSQL.

### StoryCompleted
Producer: Playback  
Consumers: Recommendations, Analytics, Achievements

```json
{
  "accountId": "uuid",
  "profileId": "uuid",
  "storyId": "uuid",
  "episodeId": "uuid",
  "sessionId": "uuid",
  "completedAt": "2026-07-14T18:20:31Z"
}
```

### ListeningSessionEnded
Producer: Playback  
Consumers: Analytics, Ads Eligibility

## Subscription Events

### SubscriptionActivated
Producer: Subscriptions  
Consumers: Entitlements, Notifications, Analytics

### SubscriptionRenewed
Producer: Subscriptions  
Consumers: Entitlements, Analytics

### SubscriptionGracePeriodStarted
Producer: Subscriptions  
Consumers: Entitlements, Notifications

### SubscriptionExpired
Producer: Subscriptions  
Consumers: Entitlements, Download Reconciliation, Notifications

### SubscriptionRevoked
Producer: Subscriptions  
Consumers: Entitlements, Security Monitoring, Download Reconciliation

```json
{
  "accountId": "uuid",
  "subscriptionId": "uuid",
  "provider": "GOOGLE_PLAY",
  "effectiveAt": "2026-07-14T18:20:31Z",
  "reason": "REFUND"
}
```

## Download Events

### OfflineDownloadAuthorized
Producer: Downloads  
Consumers: Analytics, Security Monitoring

### OfflineDownloadCompleted
Producer: Mobile Sync / Downloads  
Consumers: Analytics

### OfflineEntitlementRevoked
Producer: Entitlements  
Consumers: Download Reconciliation, Notifications

## Notification Events

### NotificationCreated
Producer: Notifications  
Consumers: Delivery Workers, In-App Projection

### NotificationDelivered
Producer: Delivery Worker  
Consumers: Analytics

### NotificationFailed
Producer: Delivery Worker  
Consumers: Retry Scheduler, Operations Monitoring

```json
{
  "notificationId": "uuid",
  "channel": "PUSH",
  "provider": "FCM",
  "failureCode": "TOKEN_INVALID",
  "retryable": false
}
```

## Administration and Media Events

### MediaUploaded
Producer: Media  
Consumers: Malware Scan, Media Processing

### MediaScanCompleted
Producer: Media Security Worker  
Consumers: Catalog, Admin Projections

### MediaProcessingCompleted
Producer: Media Worker  
Consumers: Catalog, Admin Projections

### AdminActionRecorded
Producer: Administration  
Consumers: Audit Projection, Security Monitoring

## Routing

Recommended exchanges:
- `identity.events`
- `profiles.events`
- `catalog.events`
- `playback.events`
- `subscriptions.events`
- `notifications.events`
- `media.events`

Routing keys use lowercase dot notation, for example `catalog.story.published.v1`.

## Retry Policy

- retry only transient failures;
- use exponential backoff with jitter;
- keep retry count bounded;
- invalid schemas are not retried indefinitely;
- dead-letter messages include failure reason and original routing metadata;
- replay requires operator authorization and remains auditable.

## Schema Evolution

Compatible additions may keep the same event version. Removing, renaming or changing the meaning/type of a field requires a new version. Producers should support a migration window where necessary. Consumers must ignore unknown optional fields.

## Ownership

The producing bounded context owns an event schema. Consumers may not redefine its meaning. Any change affecting consumers requires review of this catalog and contract tests in CI.
