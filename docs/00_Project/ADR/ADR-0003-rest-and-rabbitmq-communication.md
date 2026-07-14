# ADR-0003: Use REST for Synchronous APIs and RabbitMQ for Asynchronous Events

Status: Accepted
Date: 2026-07-14

## Context

The platform needs both immediate request-response interactions and decoupled background processing. Mobile and admin clients require predictable APIs for authentication, catalog browsing, playback authorization, progress, profiles, and account management. Other workflows such as notification generation, media processing, analytics propagation, subscription lifecycle handling, and audit enrichment should not block the initiating request.

## Decision

HTTP REST with JSON will be used for synchronous public and administrative APIs. RabbitMQ will be used for asynchronous domain and integration events when temporal decoupling, retry, buffering, or fan-out provides clear value.

### REST Rules

- APIs are versioned under `/api/v1`.
- OpenAPI is the source of truth for public contracts.
- Resource-oriented URLs are preferred.
- Commands that do not map naturally to CRUD may use explicit action sub-resources.
- Idempotency keys are required for retry-prone write operations such as purchase processing and selected administrative commands.
- Standard error envelopes and correlation IDs are mandatory.
- Internal module calls inside the modular monolith remain in-process and must not be simulated through HTTP.

### RabbitMQ Rules

- Events describe facts that have already occurred.
- Event names use past tense, for example `StoryPublished` and `SubscriptionActivated`.
- Event envelopes contain event ID, type, version, timestamp, producer, correlation ID, causation ID, and payload.
- Consumers must be idempotent.
- Retries use bounded backoff and dead-letter routing.
- Schema changes must remain backward compatible within a supported event version.
- Publishing business events uses the transactional outbox pattern where data consistency matters.

## Consequences

### Positive

- Clear separation between immediate user interactions and background work.
- Better resilience during temporary downstream failures.
- Easier fan-out to notifications, analytics, and audit consumers.
- Familiar API model for mobile and admin clients.

### Negative

- Asynchronous flows are eventually consistent.
- Message duplication and out-of-order delivery must be handled.
- RabbitMQ introduces operational and observability requirements.
- Debugging cross-component flows requires correlation and tracing discipline.

## Alternatives Considered

### REST for all communication

Rejected because it tightly couples background workflows and propagates downstream failures into user requests.

### Kafka as the initial event platform

Rejected because the first release does not require large-scale durable event streaming, replay-heavy analytics, or very high throughput. Kafka may be reconsidered if these requirements emerge.

### GraphQL for public APIs

Deferred. The product currently has well-defined mobile use cases and can avoid the authorization, caching, and operational complexity of GraphQL. A backend-for-frontend or GraphQL layer may be evaluated later if client composition needs become dominant.

## Follow-up Actions

- Maintain the Event Catalog and API Specification.
- Implement outbox and inbox persistence support.
- Add contract tests for APIs and event payloads.
- Monitor dead-letter queues and consumer lag.
- Define ownership for every exchange, routing key, queue, and consumer.
