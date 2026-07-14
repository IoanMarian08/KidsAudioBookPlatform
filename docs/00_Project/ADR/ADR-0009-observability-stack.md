# ADR-0009: Observability Stack

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture, Backend, DevOps

## Context

The platform requires production-grade visibility into API latency, playback failures, notification delivery, background jobs, RabbitMQ consumers, database health, cache behavior, and business-critical flows. Logs alone are insufficient, and observability must work consistently across local, test, and production environments.

## Decision

Adopt an observability stack based on OpenTelemetry conventions, Micrometer, Prometheus, Grafana, and Loki.

- Spring Boot services expose metrics through Micrometer.
- Prometheus scrapes application and infrastructure metrics.
- Grafana provides dashboards and alert visualization.
- Loki stores structured application logs.
- Correlation IDs and trace IDs propagate across HTTP requests, asynchronous messages, and background jobs.
- OpenTelemetry-compatible tracing is introduced for critical distributed flows as the system is split into independently deployed services.

## Logging Standard

Logs are structured JSON in non-local environments and include:

```json
{
  "timestamp": "2026-07-14T18:12:10Z",
  "level": "INFO",
  "service": "catalog-service",
  "environment": "prod",
  "correlationId": "c8c8...",
  "traceId": "1af3...",
  "event": "story.published",
  "entityId": "story-uuid",
  "durationMs": 42
}
```

Secrets, tokens, PINs, passwords, payment data, full request bodies, and unnecessary child-related data must never be logged.

## Required Metrics

- HTTP request count, latency percentiles, and error rate;
- JVM memory, GC, thread, and connection pool metrics;
- PostgreSQL query and pool saturation indicators;
- Redis latency, miss rate, evictions, and failures;
- RabbitMQ queue depth, consumer lag, redelivery, and dead-letter count;
- playback-start success rate and signed-URL generation failures;
- notification delivery and retry outcomes;
- subscription webhook processing and reconciliation failures;
- background job duration and last successful execution.

## Service-Level Objectives

Initial targets:

| Capability | Objective |
|---|---|
| Authenticated API availability | 99.9% monthly |
| Catalog API p95 latency | under 300 ms excluding media delivery |
| Playback authorization p95 | under 250 ms |
| Critical event processing | 99% within 60 seconds |
| Notification creation | 99% within 2 minutes |

## Alerting Rules

Alerts must be actionable and tied to user or business impact. Examples:

- sustained 5xx rate above threshold;
- authentication failure spike;
- payment webhook backlog;
- dead-letter queue growth;
- no successful media-processing job within expected window;
- database or Redis saturation;
- notification provider outage;
- high crash-free session regression in mobile releases.

## Consequences

### Positive

- Problems can be detected before support reports accumulate.
- Metrics, logs, and traces share correlation context.
- Architecture decisions can be validated with real performance data.

### Negative

- Adds infrastructure, storage, retention, and dashboard maintenance costs.
- Poorly controlled labels can create metric-cardinality problems.

## Rejected Alternatives

- Plain text logs only: insufficient for querying and correlation.
- Vendor-specific instrumentation in application code: creates avoidable lock-in.
- Logging complete request and response bodies: excessive privacy and security risk.
