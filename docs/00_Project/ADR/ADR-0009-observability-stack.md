# ADR-0009: Observability Stack

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture, Backend, DevOps
- **Last reviewed:** 2026-07-15

## Context

The platform requires production-grade visibility into API latency, playback failures, notification delivery, background jobs, RabbitMQ consumers, database health, cache behavior, mobile stability, and business-critical flows. Logs alone are insufficient. Observability must work consistently across local, test, staging, and production environments while avoiding unnecessary vendor lock-in and protecting sensitive user and child data.

The platform begins as a modular monolith with workers but is expected to evolve toward independently deployable services. Correlation across synchronous requests, asynchronous events, scheduled jobs, and external providers must therefore be designed from the beginning.

## Decision

Adopt an observability stack based on OpenTelemetry conventions, Micrometer, Prometheus, Grafana, and Loki.

- Spring Boot applications expose metrics through Micrometer.
- Prometheus collects application and infrastructure metrics.
- Grafana provides dashboards, SLO views, and alert visualization.
- Loki stores structured application logs.
- Correlation IDs and trace context propagate across HTTP requests, asynchronous messages, and background jobs.
- OpenTelemetry-compatible instrumentation is used for distributed tracing and future backend portability.
- Mobile and admin clients emit privacy-safe operational telemetry through controlled ingestion endpoints or approved providers.
- Business metrics and technical metrics remain distinguishable but correlated.

## Observability Pillars

The platform uses four complementary signal types:

1. **Metrics** for trends, saturation, errors, and alerting.
2. **Logs** for detailed structured diagnostic context.
3. **Traces** for end-to-end request and event flow analysis.
4. **Business events** for product and operational outcomes.

No single signal is considered sufficient for critical flows.

## Correlation Model

Every inbound request receives or generates:

- `correlationId` for the business operation;
- `traceId` for distributed tracing;
- `spanId` for the current operation;
- `requestId` for one transport request where useful.

Asynchronous events additionally include:

- `eventId`;
- `causationId`;
- producer;
- event type and version.

The same correlation context must flow through:

- API gateway or reverse proxy;
- backend controllers;
- application services;
- database operations where supported;
- outbox publication;
- RabbitMQ messages;
- workers;
- external provider calls;
- audit records.

Clients may send a valid correlation identifier, but the server remains authoritative and may replace malformed or unsafe values.

## Logging Standard

Logs are structured JSON outside local development.

Example:

```json
{
  "timestamp": "2026-07-14T18:12:10Z",
  "level": "INFO",
  "service": "catalog-service",
  "module": "catalog",
  "environment": "prod",
  "correlationId": "c8c8...",
  "traceId": "1af3...",
  "spanId": "9021...",
  "event": "story.published",
  "actorType": "ADMIN",
  "entityType": "STORY",
  "entityId": "story-uuid",
  "outcome": "SUCCESS",
  "durationMs": 42,
  "errorCode": null
}
```

## Required Log Fields

Where applicable, structured logs include:

- timestamp in UTC;
- severity;
- service and module;
- environment;
- application version;
- correlation, trace, and span identifiers;
- operation or event name;
- actor type and privacy-safe actor identifier;
- entity type and identifier;
- outcome;
- duration;
- stable error code;
- retry count;
- external provider name;
- queue or routing key for message processing.

## Logging Rules

- Do not log passwords, PINs, access tokens, refresh tokens, purchase receipts, provider credentials, signed URLs, or secrets.
- Do not log raw request or response bodies by default.
- Do not log unnecessary child names, birth dates, profile content, or listening details.
- Use allowlisted fields rather than broad object serialization.
- Stack traces are logged only for unexpected errors and remain internal.
- Known business errors use structured error codes without noisy stack traces.
- Repeated failures must be rate-limited or sampled where necessary.
- Audit logs are distinct from diagnostic logs and follow stronger retention and immutability rules.

## Metric Naming and Labels

Metric names use stable lowercase dot or underscore conventions according to the selected registry adapter.

Examples:

```text
http.server.requests
playback.start.success
rabbitmq.consumer.redelivery
subscription.reconciliation.failure
notification.delivery.duration
```

Allowed labels are low-cardinality values such as:

- service;
- module;
- environment;
- endpoint template;
- HTTP method;
- status class;
- error code;
- provider;
- queue;
- outcome;
- app version.

User IDs, profile IDs, story IDs, request IDs, and arbitrary exception messages must not be metric labels.

## Required Technical Metrics

### API and JVM

- request count, latency percentiles, and error rate;
- active requests;
- JVM heap, non-heap, GC, thread, and class-loading metrics;
- process CPU and memory;
- connection-pool utilization;
- readiness and liveness state.

### PostgreSQL

- connection saturation;
- query latency;
- lock waits;
- transaction failures;
- replication lag where applicable;
- migration status;
- storage growth.

### Redis

- latency;
- cache hit and miss rate;
- evictions;
- memory utilization;
- connection failures;
- command errors.

### RabbitMQ

- queue depth;
- consumer count;
- oldest message age;
- redelivery count;
- retry queue depth;
- dead-letter count;
- publish failures;
- consumer processing duration.

### Object Storage and CDN

- upload failures;
- processing failures;
- signed-access failures;
- CDN hit ratio;
- origin egress;
- missing-object and orphan counts.

## Required Business and Journey Metrics

- registration success rate;
- login success and lockout rate;
- profile creation success;
- catalog home success and latency;
- playback-start success rate;
- playback authorization failures by stable reason;
- progress synchronization success;
- offline synchronization failures;
- purchase verification success;
- subscription reconciliation backlog;
- entitlement evaluation failure;
- notification creation and delivery outcomes;
- content publication success;
- media processing completion time;
- account-deletion workflow age.

Business metrics must remain privacy-safe and must not enable sensitive child profiling.

## Distributed Tracing

Tracing is mandatory for critical flows and sampled for ordinary traffic.

Priority traces include:

- authentication and token refresh;
- story discovery and playback authorization;
- purchase verification and entitlement activation;
- outbox publication and event consumption;
- media upload and processing;
- notification creation and provider delivery;
- offline synchronization;
- account deletion.

Sampling rules:

- keep all traces for errors and critical workflows where feasible;
- sample a bounded percentage of successful high-volume requests;
- avoid recording sensitive payloads in spans;
- preserve trace context across RabbitMQ headers;
- use consistent service and operation names.

## Service-Level Indicators and Objectives

Initial objectives:

| Capability | Objective |
|---|---|
| Authenticated API availability | 99.9% monthly |
| Catalog API p95 latency | under 300 ms excluding media delivery |
| Playback authorization p95 | under 250 ms |
| Playback-start success | at least 99.5% excluding client connectivity |
| Critical event processing | 99% within 60 seconds |
| Notification creation | 99% within 2 minutes |
| Purchase verification processing | 99% within 60 seconds when provider is available |

SLOs are reviewed after real production data becomes available. Targets must not be silently weakened to match poor performance.

## Error Budgets

Each SLO has an error budget used to guide release risk.

When a critical error budget is exhausted:

- high-risk releases may be paused;
- reliability work takes priority;
- root causes and recurring failure modes are reviewed;
- temporary mitigations must have owners and expiry dates.

## Alerting Principles

Alerts must be:

- actionable;
- tied to user, security, data, or business impact;
- routed to a clear owner;
- documented with a runbook;
- deduplicated and rate-controlled;
- tested periodically.

## Required Alerts

Examples:

- sustained 5xx rate above threshold;
- authentication failure or lockout spike;
- playback-start success regression;
- payment webhook or reconciliation backlog;
- dead-letter queue growth;
- oldest event age above threshold;
- no successful media-processing job within the expected window;
- database, Redis, or connection-pool saturation;
- object-storage or CDN failure;
- notification provider outage;
- account deletion workflow stalled;
- high crash-free session regression in mobile releases;
- critical security event spike.

Single transient failures should not page operators unless they indicate security or data-integrity risk.

## Dashboards

Minimum dashboard set:

1. Platform overview.
2. API health and latency.
3. Playback and media delivery.
4. Subscriptions and entitlements.
5. RabbitMQ and workers.
6. Notifications.
7. PostgreSQL and Redis.
8. Object storage and CDN.
9. Mobile release health.
10. Security and abuse indicators.
11. SLO and error-budget status.

Dashboards must use the same stable metric definitions as alerts.

## Mobile Observability

Mobile telemetry includes:

- app version and platform;
- crash-free sessions;
- startup duration;
- playback-start duration and failures;
- download and sync failures;
- API error codes;
- background audio failures;
- local database migration failures.

Mobile telemetry must not include raw child content, names, tokens, or sensitive listening history. Device identifiers must be privacy-safe and purpose-limited.

## Admin Dashboard Observability

Track:

- page and API failures;
- publishing workflow failures;
- upload failures;
- permission denials;
- destructive action outcomes;
- browser errors;
- frontend release version.

Frontend errors include a correlation ID when linked to a backend request.

## Retention

Retention differs by signal:

- high-volume debug logs have short retention;
- operational logs have moderate retention;
- metrics retain enough history for trend and capacity analysis;
- traces have sampled, bounded retention;
- audit records follow security and legal retention requirements;
- security incident evidence may receive temporary extended retention.

Exact periods are configured per environment and documented operationally.

## Environment Strategy

### Local

- human-readable logs are allowed;
- local Prometheus/Grafana/Loki may run through Docker Compose;
- tracing may use a local collector.

### Test and CI

- tests verify correlation propagation and metric registration;
- observability infrastructure is not required for every unit test;
- integration environments validate exporters and dashboards where practical.

### Staging

- mirrors production signal formats and alert logic;
- supports alert and runbook testing.

### Production

- structured logs only;
- controlled sampling;
- production retention and access controls;
- alerts routed to responsible owners.

## Access Control

- Observability access follows least privilege.
- Production logs and traces are not publicly accessible.
- Sensitive dashboards require explicit roles.
- Query and export actions may be audited.
- Support users receive only the minimum data required.

## Testing and Validation

Required validation includes:

- correlation ID propagation tests;
- RabbitMQ trace-context propagation tests;
- structured log schema tests;
- secret and token redaction tests;
- metric registration tests;
- cardinality review;
- alert-rule validation;
- dashboard query validation;
- synthetic checks for critical journeys;
- runbook and paging drills before production launch.

## Operational Ownership

Each service or module owner is responsible for:

- its key metrics;
- dashboards;
- alerts;
- runbooks;
- SLO review;
- cardinality control;
- removing obsolete instrumentation.

DevOps owns shared collection infrastructure, not the semantic correctness of every application metric.

## Consequences

### Positive

- Problems can be detected before support reports accumulate.
- Metrics, logs, traces, and business events share correlation context.
- Architecture decisions can be validated with real performance data.
- The platform retains provider portability through open instrumentation conventions.
- SLOs and error budgets support evidence-based release decisions.

### Negative

- Adds infrastructure, storage, retention, and dashboard maintenance costs.
- Poorly controlled labels can create metric-cardinality problems.
- Instrumentation requires ongoing ownership.
- Tracing and telemetry can create privacy risk if fields are not tightly controlled.

## Rejected Alternatives

- **Plain text logs only:** insufficient for querying and correlation.
- **Metrics without logs or traces:** insufficient for detailed diagnosis.
- **Vendor-specific instrumentation in application code:** creates avoidable lock-in.
- **Logging complete request and response bodies:** excessive privacy and security risk.
- **Alerting on every exception:** creates noise and operator fatigue.

## Follow-up Actions

- Define shared logging and correlation libraries.
- Add Micrometer and OpenTelemetry conventions to backend templates.
- Create the minimum dashboard set.
- Add alert runbooks before production launch.
- Document retention and access policies.
- Add mobile and admin telemetry schemas.
- Review SLO targets after initial load testing and production data.
