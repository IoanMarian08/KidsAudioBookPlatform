# ADR-0003: Use REST for Synchronous APIs and RabbitMQ for Asynchronous Events

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture, Backend Engineering, DevOps

## Context

The platform needs both immediate request-response interactions and decoupled background processing.

Mobile and admin clients require predictable APIs for authentication, catalog browsing, playback authorization, progress, profiles, subscriptions, notifications, and account management. Other workflows such as notification generation, media processing, analytics propagation, subscription lifecycle handling, audit enrichment, privacy processing, and reconciliation should not block the initiating request.

A single communication style would either couple long-running work to user-facing latency or make simple interactions unnecessarily asynchronous.

## Decision

Use HTTP REST with JSON for synchronous public and administrative APIs. Use RabbitMQ for asynchronous domain and integration events when temporal decoupling, retry, buffering, fan-out, or independent processing provides clear value.

Internal module calls inside the modular monolith remain in-process. They must not be simulated through HTTP or RabbitMQ merely to imitate a distributed system.

## Communication Selection Rules

Use synchronous REST when:

- the caller needs an immediate result;
- the operation is a query or short command;
- validation feedback must be returned directly;
- the caller must know whether the operation was accepted;
- strong read-after-write behavior is required.

Use asynchronous messaging when:

- work can complete later;
- multiple consumers react independently;
- buffering protects the producer from downstream load;
- retries should not block the initiating request;
- eventual consistency is acceptable and documented;
- a durable fact must be distributed to other bounded contexts.

Do not use asynchronous messaging to hide unclear ownership or to avoid designing a proper application interface.

## REST Contract Rules

- APIs are versioned under `/api/v1`.
- OpenAPI is the source of truth for public HTTP contracts.
- Resource-oriented URLs are preferred.
- Commands that do not map naturally to CRUD may use explicit action sub-resources.
- Standard error envelopes and correlation IDs are mandatory.
- Request and response bodies use explicit DTOs, not persistence entities.
- Pagination is mandatory for unbounded collections.
- Filtering and sorting options are allow-listed.
- Date and time values use ISO 8601 and UTC unless the field explicitly represents a local concept.
- Unknown response fields must be tolerated by clients.
- Breaking changes require a new major API version according to ADR-0013.

## HTTP Semantics

- `GET` is safe and idempotent.
- `PUT` is used for complete idempotent replacement where appropriate.
- `PATCH` is used only with a documented partial-update contract.
- `POST` is used for creation or non-idempotent commands.
- `DELETE` must define whether deletion is immediate, soft, asynchronous, or policy-driven.
- `202 Accepted` is used when processing continues asynchronously.
- `409 Conflict` represents a state or idempotency conflict.
- `422 Unprocessable Entity` may represent semantically invalid input where appropriate.
- `429 Too Many Requests` includes retry guidance.

## Idempotency

Idempotency keys are required for retry-prone write operations including:

- purchase and webhook processing;
- account deletion requests;
- selected administrative bulk actions;
- upload finalization;
- notification campaign creation;
- commands that may be retried by mobile offline synchronization.

The server stores the key, operation scope, request fingerprint, outcome, and expiry. Reuse with different request content is rejected.

## Timeouts and Retries

Every synchronous dependency call has an explicit timeout.

Retry rules:

- retry only transient failures;
- retry only idempotent operations or operations protected by idempotency;
- use bounded exponential backoff with jitter;
- never retry validation, authorization, or deterministic business failures;
- do not create nested retry storms across layers;
- use circuit breakers for unstable external dependencies where evidence supports them.

Client-facing APIs must not wait indefinitely for downstream providers.

## RabbitMQ Topology

Use topic exchanges grouped by bounded context or integration purpose.

Examples:

```text
identity.events
profiles.events
catalog.events
playback.events
subscriptions.events
notifications.events
media.events
platform.integration
```

Routing keys use lowercase dot notation and include a version when it improves operational clarity, for example:

```text
catalog.story.published.v1
subscriptions.subscription.activated.v1
media.asset.processing-completed.v1
```

Queues are owned by consumers, not producers.

## Event Contract Rules

- Events describe facts that have already occurred.
- Event names use past tense.
- Event envelopes contain event ID, type, version, occurred-at timestamp, producer, correlation ID, causation ID, and payload.
- Event IDs are globally unique.
- Consumers must be idempotent.
- Producers must not include secrets or unnecessary child-related data.
- Consumers must ignore unknown optional fields.
- Breaking payload changes create a new event version.
- Event schemas are defined in the Event Catalog.
- Events are immutable after publication.

## Commands and Work Messages

RabbitMQ may also transport internal work messages for background processing, but these are not domain events.

Commands:

- are named imperatively;
- have one logical owner;
- are not fan-out facts;
- require explicit retry and deduplication behavior;
- must not be mistaken for durable business history.

Examples include `ProcessMediaAsset` or `SendNotificationDelivery`.

## Transactional Outbox

When a database change and event publication must remain consistent, use the transactional outbox pattern.

Flow:

1. Commit business state and outbox record in one PostgreSQL transaction.
2. A publisher reads pending outbox records.
3. Publish to RabbitMQ with publisher confirmation.
4. Mark the outbox record as published.
5. Reconcile records left in an uncertain state.

Direct publication before the business transaction commits is forbidden.

## Consumer Inbox and Deduplication

Critical consumers persist processed event IDs or idempotency state before acknowledging a message.

Consumers must handle:

- duplicate delivery;
- redelivery after timeout;
- delayed processing;
- unsupported schema versions;
- out-of-order messages;
- poison messages;
- partial downstream failure.

Acknowledgement occurs only after the durable effect is complete.

## Ordering

Global event ordering is not guaranteed.

Where order matters:

- partition logically by aggregate or routing key;
- include aggregate version or sequence information;
- reject, defer, or reconcile stale transitions;
- avoid relying on broker timing as a business guarantee.

A consumer must document whether it requires per-aggregate ordering.

## Retry and Dead-Letter Policy

- Retry only transient failures.
- Use bounded retries with exponential backoff and jitter.
- Route exhausted messages to a dead-letter queue.
- Invalid schemas and permanent business failures are not retried indefinitely.
- Dead-letter records preserve original routing metadata, failure category, timestamps, and retry count.
- Replay requires authorization, audit logging, and an idempotent consumer.
- Large DLQ growth triggers operational alerts.

## Delivery Guarantees

The platform assumes at-least-once delivery for asynchronous processing.

Exactly-once delivery is not claimed. Business-level exactly-once effects are approximated through:

- idempotency keys;
- unique database constraints;
- consumer inbox records;
- aggregate version checks;
- reconciliation jobs.

## Security

- All external HTTP traffic uses TLS.
- Authentication and authorization are enforced at API boundaries.
- Administrative APIs require stronger scopes and audit trails.
- RabbitMQ uses environment-specific credentials and least-privilege virtual hosts, exchanges, and queues.
- Broker management endpoints are not publicly exposed.
- Sensitive payloads are minimized and encrypted in transit.
- Message headers must not contain raw tokens or personal data.
- External webhooks are signature-verified and replay-protected.

## Observability

Synchronous telemetry includes:

- request count;
- latency percentiles;
- status and error code distribution;
- timeout and retry counts;
- dependency latency;
- idempotency reuse and conflict rates.

Asynchronous telemetry includes:

- publish failures;
- outbox backlog and age;
- queue depth;
- consumer lag;
- processing duration;
- redelivery count;
- dead-letter count;
- unsupported schema versions;
- replay outcomes.

Correlation and trace context propagate across HTTP, outbox, RabbitMQ, and background jobs.

## Failure Behavior

If RabbitMQ is unavailable:

- transactional business writes may still commit when the outbox record is durable;
- publishers retry later;
- queue-dependent user flows return an accepted or degraded result only when the product contract permits it;
- no event is reported as published without broker confirmation.

If a synchronous dependency is unavailable:

- fail fast after the configured timeout;
- use a safe degraded response where possible;
- do not silently convert a failed synchronous command into an asynchronous one unless the API contract explicitly supports `202 Accepted`.

## Testing

Required tests include:

- OpenAPI contract validation;
- controller and serialization tests;
- idempotency behavior;
- timeout and retry behavior;
- outbox atomicity;
- RabbitMQ integration tests with Testcontainers;
- duplicate-delivery consumer tests;
- unsupported event-version tests;
- dead-letter routing tests;
- replay and reconciliation tests;
- security tests for authentication, scopes, and webhook signatures.

## Governance

Every public endpoint must have:

- an owning bounded context;
- an OpenAPI definition;
- documented authentication and authorization;
- error-code mappings;
- compatibility classification;
- observability expectations.

Every exchange, routing key, queue, event, command, and consumer must have an owner.

A new communication pattern or broker requires a separate ADR.

## Consequences

### Positive

- Clear separation between immediate user interactions and background work.
- Better resilience during temporary downstream failures.
- Easier fan-out to notifications, analytics, search, and audit consumers.
- Familiar API model for mobile and admin clients.
- Explicit ownership and compatibility rules.
- Preserves a simple modular monolith while enabling later extraction.

### Negative

- Asynchronous flows are eventually consistent.
- Message duplication and out-of-order delivery must be handled.
- RabbitMQ introduces operational, security, and observability requirements.
- Temporary schema and API version overlap increases maintenance.
- Debugging cross-component flows requires strong correlation discipline.

## Alternatives Considered

### REST for all communication

Rejected because it tightly couples background workflows and propagates downstream failures into user requests.

### RabbitMQ for all internal communication

Rejected because it would add unnecessary eventual consistency and operational complexity to simple in-process interactions.

### Kafka as the initial event platform

Rejected because the first release does not require high-throughput event streaming, long-term replay, or large-scale analytical consumption. It may be reconsidered with production evidence.

### GraphQL for public APIs

Deferred. Current mobile use cases are well-defined and do not justify the authorization, caching, and operational complexity.

### gRPC for public mobile APIs

Rejected for the initial release because REST and OpenAPI provide simpler tooling, debugging, caching, and external compatibility. gRPC may be considered for future internal service-to-service calls.

## Follow-up Actions

- Maintain the Event Catalog and API Specification.
- Implement reusable outbox and inbox support.
- Add API and event contract tests to CI.
- Monitor dead-letter queues, consumer lag, and outbox age.
- Define and review ownership for every exchange, routing key, queue, and consumer.
- Document retry and timeout budgets per integration.
- Review this ADR before introducing Kafka, gRPC, GraphQL, or a second broker.
