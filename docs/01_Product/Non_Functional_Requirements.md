# Non-Functional Requirements (NFR)

Version: 2.0.0  
Status: Proposed measurable baseline  
Owner: Architecture, Product, SRE

## 1. Policy

NFRs are release constraints, not optional polish. Every NFR must have: measurable SLI, target, traffic/environment definition, monitoring source, test evidence, exception owner and review date. Targets below are initial engineering goals until calibrated with realistic usage.

## 2. Reliability and availability

| ID | Requirement | Target / Evidence |
|---|---|---|
| NFR-REL-01 | Core API availability | >= 99.9% calendar-month success excluding explicitly documented client faults |
| NFR-REL-02 | Recovery | Tested backups + restore drill, RTO/RPO defined before launch based on business impact |
| NFR-REL-03 | Safe degradation | Redis/recommendations/push outage does not block eligible playback when authoritative fallback is available |
| NFR-REL-04 | Async reliability | At-least-once processing, idempotent consumers, DLQ and manual replay runbook |
| NFR-REL-05 | Delivery | Production deploy supports health gating and rollback |

Use an incident review whenever an SLO is breached. Do not silently relax targets.

## 3. Response time and throughput

| ID | Workload | Initial goal |
|---|---|---|
| NFR-PER-01 | Read API | p95 <= 400 ms under reference load |
| NFR-PER-02 | Write API | p95 <= 700 ms under reference load |
| NFR-PER-03 | Catalog | p95 <= 500 ms under reference load |
| NFR-PER-04 | Progress write | p95 <= 400 ms under reference load |
| NFR-PER-05 | Playback start | <= 2 seconds on a defined good network |
| NFR-PER-06 | Background event handling | 95% complete within 30 seconds when downstream available |

These targets follow [Performance Guidelines](../03_Architecture/Performance_Guidelines.md), which is authoritative if values differ. Reference load and devices must be defined before claiming compliance. Track p50/p95/p99, error rate, saturation and queue age.

## 4. Security and privacy

| ID | Requirement | Verification |
|---|---|---|
| NFR-SEC-01 | TLS and secrets | Encrypted transport; secrets managed outside repo |
| NFR-SEC-02 | Authorization | Every child/account resource enforces server-side ownership |
| NFR-SEC-03 | Parent Zone | Elevated authorization for sensitive operations, expiry and anti-bruteforce controls |
| NFR-SEC-04 | Supply chain | SCA, SAST, dependency provenance and container scanning in CI |
| NFR-SEC-05 | Audit | Privileged editorial, billing and admin actions traceable |
| NFR-SEC-06 | Children's privacy | Minimize child data; legal review for age/consent/retention and store compliance |
| NFR-SEC-07 | Media | Short-lived signed URLs, upload scanning, private originals |

Release blockers: critical exploitable vulnerabilities, unauthorized child data disclosure, disabled ownership validation or unreviewed child-directed monetization.

## 5. Mobile UX and accessibility

- **NFR-MOB-01**: Profile switching never leaks previous child's content, favorites or activity.
- **NFR-MOB-02**: Playback control stays responsive during unreliable connectivity; predownloaded authorized content follows offline policy.
- **NFR-MOB-03**: Accessibility supports screen readers, semantic labels, contrast, focus order and configurable text sizing where platform permits.
- **NFR-MOB-04**: Performance is measured on at least one representative low/mid-tier Android and iOS device.
- **NFR-MOB-05**: No dark patterns or coercive advertising for children. Parent-only payment experience.

## 6. Maintainability and evolvability

- **NFR-MNT-01**: Package by feature with explicit API/application/domain/infrastructure boundaries.
- **NFR-MNT-02**: No cross-module direct table/repository access; interactions through public interfaces and events.
- **NFR-MNT-03**: Feature changes ship contract tests, migrations (if needed), logs, metrics and updated docs.
- **NFR-MNT-04**: Automated unit/integration/contract/acceptance security tests gate merging.
- **NFR-MNT-05**: Rollout is backwards compatible across old mobile clients for a documented window.

## 7. Observability and operations

- **NFR-OPS-01**: Every production request has a correlation ID and trace; no PII or token leakage in logs.
- **NFR-OPS-02**: Dashboards cover API SLOs, database pools, Redis hit/evictions, RabbitMQ queue age/DLQ, CDN signing errors and mobile crash rate.
- **NFR-OPS-03**: Actionable alerts connect to runbooks and incident owners.
- **NFR-OPS-04**: Monthly reviews track costs, storage growth, egress, incident themes and technical debt.
- **NFR-OPS-05**: Data migrations use tested expand/migrate/contract for breaking schemas.

## 8. Scalability and capacity

Capacity models must estimate daily active parents/children, concurrency, peak API RPS, media delivery/egress, asset storage, progress writes, event volume and retention. Scale stateless API/worker processes horizontally after measuring the bottleneck; bound DB pools; use CDN for audio. A scaling claim is valid only with before/after load evidence.

## 9. Verification matrix

| Area | Primary test | Observability |
|---|---|---|
| Latency | k6/Gatling load tests with production-like data | HTTP percentiles |
| Availability | Synthetic probes and dependency-failure tests | SLI + error budget |
| Child safety | RBAC/IDOR and end-to-end Parent Zone tests | Audit events |
| Data durability | Backup restore and offline sync reconciliation | Restore results + data correctness |
| Compatibility | OpenAPI consumer contract checks | Version errors |
| Mobile | Real-device frame, memory, crash and offline tests | Client telemetry |
| Security | SAST/SCA/DAST + manual threat review | Security findings |

## 10. Release sign-off

P0 requirements must have owners and passing evidence. Any accepted deviation names an expiry date, business risk, compensating control and ADR/issue reference; no permanent silent exceptions.

Related: [PRD](Product_Requirements_Document.md), [Quality Metrics](../03_Architecture/C4_Model/21_Architecture_KPI_and_Metrics.md), [Testing Strategy](../06_Testing/Testing_Strategy.md).
