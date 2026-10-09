# Monitoring, Alerting and Operational Observability

Version: 2.0.0  
Status: Operational baseline  
Owner: SRE / Engineering

## 1. Principles

Monitor critical user journeys and business correctness, not just host uptime. Requests, events and background jobs carry correlation and trace context. Logs must exclude passwords, tokens, child identifiers unnecessary for debugging, full PII and raw payment provider payloads.

Suggested tooling: Prometheus for metrics, Grafana for dashboards, Loki or equivalent for logs and OpenTelemetry for traces. Tool choice may vary; observable signals may not.

## 2. Required service-level indicators

| Capability | Signal |
|---|---|
| API | Requests/s, 4xx/5xx, p50/p95/p99 by route template |
| Auth | Sign-in/refresh success, blocked attempts, unexpected elevations |
| Child profiles | Ownership-denial spikes, profile switch errors |
| Catalog | Empty/failed reads, unavailable publication states |
| Playback | Authorization failures, time-to-first-audio, CDN URL failures |
| Progress | Save latency, sync conflicts, rejected stale updates |
| Billing | Verification/reconciliation lag, entitlement mismatch, webhook DLQ |
| Infrastructure | CPU, memory, GC, DB connections/locks, Redis hit/evict, RabbitMQ age |
| Media | Upload scan backlog, transcode failures, CDN error rate and egress cost |

## 3. Alert design

Alerts must define symptom, severity, owner, runbook and escalation path. Use burn-rate alerts on core availability/error-budget SLOs; guard against paging on temporary noisy metrics.

- **SEV1:** child data exposure, failed authorizations opening Parent Zone, widespread playback outage, data loss.
- **SEV2:** elevated playback errors, billing verification stall, sustained queue lag impacting users.
- **SEV3:** rising resource consumption, minor job backlog, nonessential notification delay.

Only authorized staff may access production telemetry; access is audited.

## 4. Suggested dashboard layout

**Executive:** active incidents, core API availability, time-to-first-play, failed verified entitlements.  
**Backend:** request heatmap, dependency latencies, DB pool saturation, top slow SQL, GC pauses.  
**Event pipeline:** outbox pending, queue depth/oldest message, consumer retry and DLQ.  
**Mobile:** crash-free sessions, startup, frame jank, download/restore success and offline errors.  
**Cost:** egress/asset storage, DB utilization, oversized media/transcode jobs.

## 5. Incident workflow

~~~mermaid
flowchart TD
    A[Automated signal or support report] --> B[Triage impact and child safety]
    B --> C{Severity}
    C -->|SEV1/SEV2| D[Page on-call and incident commander]
    C -->|SEV3| E[Create tracked task]
    D --> F[Mitigate: flag, rollback, failover]
    F --> G[Confirm user journey recovery]
    G --> H[Post-incident review and actions]
~~~

During an incident, prioritize containing data exposure and restoring eligible playback. Incident logs should include timeline, hypotheses, actions, owner and verified recovery.

## 6. Security and privacy

Use structured logging with trace ID, service name, route template, status, latency and safe entity references. Redact headers and authorization values by default. Restrict data retention and restrict dashboard access by job role. Audit administrator event access.

## 7. Operational review

Weekly: noisy alerts, queue lag, incidents, SLO burn. Monthly: error-budget trends, restore test status, capacity, egress cost, security findings and action item closure.

Related: [Logging and Monitoring Architecture](../03_Architecture/Logging_Monitoring.md), [Performance Guidelines](../03_Architecture/Performance_Guidelines.md).
