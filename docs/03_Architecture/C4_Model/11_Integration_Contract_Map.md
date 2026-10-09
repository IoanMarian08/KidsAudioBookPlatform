# Integration Contract Map

Version: 1.0.0  
Status: Active Draft  
Owner: Project Architecture  
Last updated: 2026-07-15

## 1. Purpose

This document maps the synchronous and asynchronous contracts that connect KidsAudioBookPlatform bounded contexts, clients, workers, infrastructure, and external providers.

It complements the C4 structural views by answering:

- who calls whom;
- which contract is authoritative;
- whether the interaction is synchronous or asynchronous;
- which party owns retries and idempotency;
- which data may cross the boundary;
- how the interaction fails safely;
- what must be monitored.

## 2. Contract Principles

1. Every integration has one accountable producer or provider.
2. Every public contract is versioned.
3. Consumers depend on documented contracts, not internal implementation details.
4. Synchronous calls use bounded timeouts and explicit error semantics.
5. Asynchronous consumers are idempotent.
6. Business events represent facts that already occurred.
7. Commands and events are not interchangeable.
8. Security-sensitive decisions remain server-authoritative.
9. Personally identifiable and child-related data is minimized.
10. External-provider failures must not silently corrupt internal business state.
11. Every integration defines observability, retry, reconciliation, and ownership.

## 3. Contract Types

| Contract type | Primary technology | Typical use |
|---|---|---|
| Public synchronous API | HTTPS REST + JSON | Mobile and admin requests |
| Internal synchronous contract | In-process application interface initially; REST after extraction when justified | Immediate cross-context query or command |
| Domain event | RabbitMQ | Meaningful internal business fact |
| Integration event | RabbitMQ or provider webhook normalization | Fact shared with external or independently deployed consumers |
| Provider webhook | HTTPS callback | Billing, delivery, or external processing status |
| File/object contract | S3-compatible object storage + signed URL | Audio, image, transcript, derivative upload/download |
| Projection contract | Event-fed read model | Search, recommendations, admin summaries |
| Operational contract | Metrics, logs, traces, health checks | Monitoring and support |

## 4. Client-to-Platform Contracts

### 4.1 Mobile application → Backend API

| Capability | Contract | Authority | Notes |
|---|---|---|---|
| Authentication | `/api/v1/auth/**` | Identity and Access | Short-lived access tokens and rotating refresh tokens |
| Child profiles | `/api/v1/profiles/**` | Family and Profiles | Account ownership validated server-side |
| Catalog browsing | `/api/v1/catalog/**` | Catalog and Editorial | Responses may use cache and projections |
| Playback authorization | `/api/v1/playback/**` | Listening + Entitlements + Media | Signed media access returned only after validation |
| Progress synchronization | `/api/v1/sync/**` | Listening and Progress | Batched, idempotent, cursor-based |
| Offline downloads | `/api/v1/downloads/**` | Downloads + Entitlements + Media | Manifest and expiry rules are server-authoritative |
| Notifications | `/api/v1/notifications/**` | Notifications | Paginated inbox, read state, preferences |
| Subscription state | `/api/v1/subscriptions/**` | Billing and Entitlements | Client receipt is evidence, not authority |
| Parent Zone | `/api/v1/parent-zone/**` | Identity and Access | Requires elevation credential |
| Feature configuration | `/api/v1/configuration/**` | Feature Flags | Only evaluated safe configuration is returned |

Mobile contracts must support old client versions during the approved compatibility window.

### 4.2 Admin dashboard → Admin API

The admin dashboard uses authenticated, role-restricted contracts for:

- editorial workflows;
- media upload intents;
- content approval and publication;
- account-support views;
- subscription-support actions;
- notification campaigns;
- audit searches;
- feature-flag management;
- operational announcements.

Admin contracts must enforce permission checks on every request. UI visibility is not authorization.

## 5. Internal Synchronous Contract Map

| Caller | Provider | Purpose | Response expectation | Failure behavior |
|---|---|---|---|---|
| Listening | Entitlements | Check playback eligibility | Immediate decision | Deny safely or use documented grace policy |
| Listening | Catalog | Validate story/episode availability | Immediate | Return structured unavailable state |
| Listening | Media | Request stream authorization | Immediate signed reference | Do not expose storage credentials |
| Downloads | Entitlements | Check offline eligibility | Immediate | Deny new download if uncertain |
| Downloads | Media | Build download manifest | Immediate or accepted async workflow | Retry only safe transient failures |
| Administration | Catalog | Execute editorial action | Immediate accepted/rejected result | Admin module never writes Catalog tables |
| Administration | Identity | Execute support/security action | Immediate | Strong permission and audit requirements |
| Notifications | Profiles | Resolve locale/timezone where required | Immediate or cached projection | Use safe default if non-critical |
| Advertising Policy | Entitlements | Suppress ads for premium users | Immediate or bounded-staleness cache | Premium users must not receive ads after revocation target |
| API composition | Multiple contexts | Build home or support view | Bounded parallel calls or projection | Partial response only where product-safe |

In the modular monolith, these interactions are in-process interfaces. They must remain explicit and extraction-ready.

## 6. Asynchronous Event Map

| Producer | Event | Primary consumers | Purpose |
|---|---|---|---|
| Identity | `AccountRegistered` | Notifications, Analytics | Verification and onboarding |
| Identity | `AccountVerified` | Notifications, Analytics | Account lifecycle |
| Identity | `AccountLocked` | Security Monitoring, Notifications | Security response |
| Identity | `AccountDeletionRequested` | Privacy Worker, Audit, Notifications | Coordinated deletion |
| Profiles | `ChildProfileCreated` | Recommendations, Analytics | Initialize derived state |
| Profiles | `ChildProfileUpdated` | Recommendations, Cache Invalidation | Refresh dependent state |
| Profiles | `ChildProfileDeleted` | Listening Cleanup, Privacy Worker, Recommendations | Delete/anonymize derived records |
| Catalog | `StoryPublished` | Search, Recommendations, Notifications, Cache Invalidation | Make content discoverable |
| Catalog | `StoryUnpublished` | Search, Downloads, Cache Invalidation | Remove availability |
| Media | `MediaUploaded` | Security Scan, Media Processing | Begin validation pipeline |
| Media | `MediaScanCompleted` | Catalog, Administration | Gate publication |
| Media | `MediaProcessingCompleted` | Catalog, Administration | Mark derivatives ready |
| Listening | `ListeningSessionStarted` | Analytics, Advertising Policy | Session analytics and policy |
| Listening | `ListeningProgressUpdated` | Recommendations, Analytics | Derived personalization |
| Listening | `StoryCompleted` | Recommendations, Analytics, Achievements | Completion workflows |
| Billing | `SubscriptionActivated` | Entitlements, Notifications, Analytics | Grant premium capabilities |
| Billing | `SubscriptionRenewed` | Entitlements, Analytics | Extend access |
| Billing | `SubscriptionExpired` | Entitlements, Downloads, Notifications | Remove or reduce access |
| Billing | `SubscriptionRevoked` | Entitlements, Security Monitoring, Downloads | Immediate revocation workflow |
| Entitlements | `OfflineEntitlementRevoked` | Downloads, Notifications | Invalidate offline access |
| Notifications | `NotificationCreated` | Delivery Workers, In-App Projection | Deliver communication |
| Delivery Worker | `NotificationDelivered` | Analytics | Delivery outcome |
| Delivery Worker | `NotificationFailed` | Retry Scheduler, Operations Monitoring | Recovery and alerting |
| Administration | `AdminActionRecorded` | Audit, Security Monitoring | Durable accountability |

The Event Catalog remains the canonical schema reference.

## 7. External Provider Contracts

### 7.1 Apple App Store and Google Play

Inbound:

- purchase evidence submitted by the client;
- server-to-server subscription notifications;
- provider verification responses.

Outbound:

- receipt/token verification requests;
- reconciliation queries.

Rules:

- provider callbacks are authenticated and deduplicated;
- raw evidence is retained securely where required;
- event order is not trusted blindly;
- internal subscription state is derived through a validated state machine;
- reconciliation corrects missed or delayed callbacks;
- provider outage does not automatically grant permanent entitlement.

### 7.2 Firebase Cloud Messaging and APNs

Outbound:

- channel-specific push requests containing safe, minimal content.

Inbound:

- provider acceptance or failure result;
- token invalidation signals where available.

Rules:

- provider acceptance is not equivalent to user delivery;
- invalid tokens are disabled;
- retries are bounded and classified;
- sensitive content is not placed in lock-screen payloads;
- notification business state is persisted before provider calls.

### 7.3 Email Provider

Outbound:

- approved rendered templates;
- destination reference;
- idempotency or provider metadata.

Inbound:

- delivery, bounce, complaint, or rejection status where supported.

Transactional and marketing messages use separate policy and consent handling.

### 7.4 Object Storage and CDN

Contracts include:

- upload intent;
- pre-signed upload URL;
- object-completion signal;
- scan and processing result;
- signed download or streaming authorization;
- lifecycle deletion request.

The backend owns authorization. Storage and CDN credentials never reach clients.

## 8. Webhook Contract Standard

Every webhook endpoint must define:

- provider identity and authentication method;
- signature verification;
- supported event types and versions;
- raw-body handling requirements;
- replay protection;
- idempotency key;
- maximum payload size;
- response deadline;
- retry semantics;
- persistence-before-processing behavior;
- reconciliation path;
- audit and observability requirements.

Webhook handlers acknowledge only after the event has been durably accepted.

Slow business processing occurs asynchronously.

## 9. Error Contract

Synchronous APIs use the standard error envelope:

```json
{
  "timestamp": "2026-07-15T10:00:00Z",
  "status": 409,
  "code": "STORY_004",
  "message": "Story version has changed. Refresh and try again.",
  "correlationId": "01J...",
  "path": "/api/v1/admin/stories/...",
  "details": []
}
```

Clients branch on `code`, never on localized message text.

The Error Catalog is authoritative for stable error semantics.

## 10. Idempotency Ownership

| Interaction | Idempotency owner |
|---|---|
| Client write request | Receiving API |
| Provider webhook | Webhook adapter and owning domain |
| Event publication | Producer outbox |
| Event consumption | Consumer inbox or processed-event store |
| Notification delivery | Notifications and channel worker |
| Offline sync operation | Listening/Sync API |
| Administrative bulk action | Administration orchestrator |
| Media processing job | Media worker |

Idempotency records must have explicit retention and conflict behavior.

## 11. Retry Ownership

The caller owns retries for synchronous calls unless the contract states otherwise.

Rules:

- retry only transient failures;
- use exponential backoff with jitter;
- enforce an overall deadline;
- do not retry non-idempotent operations without an idempotency key;
- avoid layered retry storms;
- respect provider rate limits and `Retry-After`;
- expose exhausted retries through metrics and alerts.

For asynchronous delivery, the consumer infrastructure owns bounded retries and dead-letter routing.

## 12. Timeout Budget

Each synchronous flow must define an end-to-end deadline and allocate smaller budgets to dependencies.

Example:

```text
Mobile playback authorization deadline: 2,000 ms
- edge and authentication: 250 ms
- entitlement decision: 300 ms
- catalog validation: 300 ms
- media authorization: 500 ms
- serialization and network reserve: 650 ms
```

A dependency timeout must be shorter than the caller's remaining deadline.

## 13. Security Classification

| Classification | Examples | Contract rule |
|---|---|---|
| Public | Published story title, public category | May be cached and distributed safely |
| Internal | Internal IDs, processing status | Expose only to authorized platform components |
| Confidential | Email, subscription evidence, device metadata | Minimize, encrypt, authorize, and audit |
| Restricted child data | Child profile settings, listening history | Strict purpose limitation and minimal propagation |
| Secret | Tokens, credentials, signing keys | Never include in contracts, logs, events, or analytics |

Every new contract must identify the highest data classification it carries.

## 14. Observability Contract

Each integration exposes:

- request or event count;
- success and failure count;
- latency or processing duration;
- retries;
- timeout count;
- dead-letter count where applicable;
- backlog or queue depth;
- provider error classification;
- last successful operation for scheduled flows;
- correlation and trace context.

Metric labels must not include account IDs, profile IDs, raw URLs, or uncontrolled provider messages.

## 15. Contract Testing

Required tests include:

- OpenAPI compatibility checks;
- request and response serialization tests;
- provider adapter tests using recorded safe fixtures or stubs;
- event schema validation;
- producer-consumer contract tests;
- webhook signature and replay tests;
- idempotency tests;
- retry and timeout tests;
- backward-compatibility tests;
- malformed and oversized payload tests;
- authorization tests for every protected contract.

## 16. Versioning and Deprecation

A contract change is compatible when consumers can continue operating without modification.

Breaking changes require:

- a new major API or event version;
- migration documentation;
- telemetry for old-version usage;
- an announced support window;
- dual support or dual publishing where necessary;
- removal only after approved criteria are met.

Unknown optional fields must be ignored by tolerant consumers.

## 17. Contract Registry

Every contract entry should record:

- name;
- owner;
- consumers;
- protocol;
- version;
- authentication;
- data classification;
- idempotency behavior;
- timeout;
- retry owner;
- SLO;
- documentation link;
- deprecation status.

The initial registry may live in Markdown and OpenAPI/Event Catalog documents. It may later be automated if the number of independently deployed services grows.

## 18. Change Review Checklist

Before changing an integration:

- Is the owner identified?
- Is the change backward compatible?
- Are mobile compatibility implications understood?
- Does it expose new personal or child data?
- Are authorization rules explicit?
- Is idempotency preserved?
- Are timeout and retry policies defined?
- Can the consumer tolerate duplication and reordering?
- Is reconciliation available?
- Are metrics, logs, and traces updated?
- Are contract tests included?
- Is an ADR required?

## 19. Related Documents

- `README.md`
- `01_System_Context.md`
- `02_Container_Diagram.md`
- `03_Component_Diagram.md`
- `06_Runtime_Views.md`
- `07_Security_Trust_Boundaries.md`
- `09_Data_Ownership_Matrix.md`
- `../API_Specification.md`
- `../Event_Catalog.md`
- `../Error_Catalog.md`
- `../System_Flows.md`
- `../Security_Architecture.md`
