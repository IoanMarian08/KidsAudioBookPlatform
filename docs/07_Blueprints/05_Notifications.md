# Blueprint 05 — Notification Delivery, Inbox and Preferences

Version: 1.0  
Status: Implementation blueprint / not deployed  
Owners: Notifications, Identity, Mobile and QA

## 1. Product outcome

The authenticated parent receives reliable, respectful account, billing and optional content notifications. The child-facing area cannot configure marketing preferences or reveal private account data. In-app inbox state persists; push/email are optional delivery channels and may fail independently.

**Normative sources:** [Notifications Architecture](../03_Architecture/Notifications.md), [API Specification](../03_Architecture/API_Specification.md) §§41–43, [Event Catalog](../03_Architecture/Event_Catalog.md) §15, [Database Design](../03_Architecture/Database_Design.md) §15 and [Security Architecture](../03_Architecture/Security_Architecture.md).

## 2. Module boundaries

The Notifications bounded context owns templates, the persisted parent inbox, channel preferences, device registrations and delivery attempts. It consumes versioned integration events from Identity, Billing and Catalog without reading their private tables. Resolve recipients through ownership-aware public interfaces; never broadcast full child profile data to push providers.

## 3. Existing API contract

| Path | Behavior |
|---|---|
| PUT /devices/{deviceId} | Register/upsert current account's push device metadata |
| DELETE /devices/{deviceId} | Revoke current account's registration |
| GET /notifications | Paginated account-scoped inbox with status/category filters |
| POST /notifications/{notificationId}/read | Idempotent mark-read |
| POST /notifications/read-all | Idempotent account-scoped bulk update |
| DELETE /notifications/{notificationId} | Dismiss notification, not necessarily hard delete |
| GET /notification-preferences | Read parent notification consent/settings |
| PUT /notification-preferences | Replace/update preference resource per API contract |

Any future /notifications/unread-count endpoint requires an explicit API Specification update and contract tests. Until then, consumers must not assume that endpoint exists.

## 4. Event and delivery flow

~~~mermaid
sequenceDiagram
  participant Billing
  participant Outbox
  participant MQ as RabbitMQ
  participant Notifications
  participant DB as PostgreSQL
  participant Provider as Push/Email
  Billing->>Outbox: SubscriptionRenewed + correlation
  Outbox->>MQ: Durable publish
  MQ->>Notifications: At-least-once delivery
  Notifications->>DB: Idempotency + inbox notification
  Notifications->>DB: Resolve consent and quiet hours
  Notifications->>Provider: Deliver allowed channels
  Provider-->>Notifications: Provider status
  Notifications->>DB: Attempt status and retry schedule
~~~

Events are idempotent by eventId/notification purpose. Publishing an inbox record and outbox command must preserve transactional consistency. External delivery is at least once; assume push providers may duplicate or reorder, and retries must be bounded.

## 5. Preference precedence

1. Legally required account/security messages follow reviewed mandatory-channel rules.
2. Parent opt-out wins for optional marketing and content reminders.
3. Quiet hours suppress/delay optional push, not critical security messages where policy requires immediate delivery.
4. No child-specific behavioral marketing; message previews do not contain private child information.
5. Notification category, template locale, destination and rate limits are resolved at **send time** as appropriate; changed consent must be honored.

## 6. Data lifecycle

Persist parent inbox rows under notifications.notifications, preferences under notifications.notification_preferences, and attempts under notifications.delivery_attempts. Device records must be account scoped. Keep provider tokens encrypted/protected where appropriate, rotate on re-registration and delete/anonymize according to retention policy.

Template content is versioned, localized and independently reviewed. Do not enqueue free-form arbitrary text to external providers from untrusted input.

## 7. Failure matrix and tests

| Condition | Expected behavior |
|---|---|
| Duplicate RabbitMQ event | One logical inbox entry, bounded duplicate sends |
| Push provider outage | Inbox still persists; retry later without blocking billing |
| Opted-out optional reminder | No push/email delivery |
| Account changed or device unregistered | No delivery to previous owner |
| Notification ID from another account | 403/404; no metadata leakage |
| Rate limit or fatigue cap | Delay/drop only optional notifications per policy |
| Expired locale/template | Use approved fallback or log controlled failure |
| Account deletion | Stop deliveries and apply retention/deletion workflow |

**Done:** API authorization/integration tests, opt-out negative tests, provider adapter mocks, retry/DLQ dashboards, localized template review and E2E parent inbox states.
