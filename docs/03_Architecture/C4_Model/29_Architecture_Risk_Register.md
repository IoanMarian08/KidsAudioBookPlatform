# Architecture Risk Register

Version: 1.0.0  
Status: Active  
Owners: Architecture, Engineering, Security, DevOps  
Last reviewed: 2026-07-15

## 1. Purpose

This document records architecture-level risks that can affect security, reliability, scalability, maintainability, cost, compliance, or delivery. It complements the technical-debt register by focusing on uncertain events and conditions that may prevent the platform from meeting its objectives.

The register must be reviewed during architecture reviews, major releases, provider changes, security assessments, and incidents that expose new systemic risks.

## 2. Scoring model

Each risk is evaluated using:

- **Likelihood**: 1 rare, 2 unlikely, 3 possible, 4 likely, 5 almost certain;
- **Impact**: 1 negligible, 2 minor, 3 moderate, 4 major, 5 critical;
- **Exposure**: likelihood multiplied by impact.

Suggested interpretation:

| Exposure | Classification | Expected action |
|---:|---|---|
| 1-4 | Low | Accept or monitor |
| 5-9 | Medium | Define owner and mitigation |
| 10-15 | High | Prioritize active reduction |
| 16-25 | Critical | Escalate and block unsafe release where appropriate |

A low numerical score does not override mandatory security, privacy, legal, or child-safety requirements.

## 3. Risk lifecycle

Every risk progresses through one of these states:

```text
IDENTIFIED -> ASSESSED -> MITIGATING -> MONITORING -> CLOSED
                         \-> ACCEPTED
```

- **IDENTIFIED**: discovered but not yet scored;
- **ASSESSED**: likelihood, impact, owner, and treatment are defined;
- **MITIGATING**: reduction work is active;
- **MONITORING**: mitigations exist and indicators are observed;
- **ACCEPTED**: remaining exposure is explicitly approved;
- **CLOSED**: the condition no longer exists or has been removed.

## 4. Required fields

Each entry must contain:

- risk ID;
- title and category;
- affected capabilities and assets;
- cause and potential consequence;
- likelihood, impact, and exposure;
- treatment strategy;
- preventive and detective controls;
- accountable owner;
- target date;
- indicators and trigger thresholds;
- residual risk;
- status and review date;
- related ADRs, incidents, or roadmap items.

## 5. Initial architecture risks

| ID | Risk | L | I | Exposure | Treatment | Owner | Status |
|---|---|---:|---:|---:|---|---|---|
| AR-001 | Modular boundaries erode and create a tightly coupled monolith | 3 | 4 | 12 | Reduce | Backend Architecture | Mitigating |
| AR-002 | Subscription provider delays create incorrect entitlement windows | 3 | 5 | 15 | Reduce | Subscription Engineering | Mitigating |
| AR-003 | Offline clients retain stale premium access longer than policy permits | 3 | 5 | 15 | Reduce | Mobile and Backend | Mitigating |
| AR-004 | Notification retries produce duplicate or intrusive delivery | 3 | 3 | 9 | Reduce | Notifications | Monitoring |
| AR-005 | Media-processing backlog delays publication | 3 | 3 | 9 | Reduce | Media Platform | Monitoring |
| AR-006 | Redis outage impacts controls that require conservative fallback | 2 | 4 | 8 | Reduce | Backend and DevOps | Monitoring |
| AR-007 | Metric-cardinality growth destabilizes observability costs and queries | 3 | 3 | 9 | Reduce | DevOps | Monitoring |
| AR-008 | Third-party SDK or dependency compromise enters the supply chain | 2 | 5 | 10 | Reduce | Security and Engineering | Mitigating |
| AR-009 | Child-related data appears in logs, analytics, or provider payloads | 2 | 5 | 10 | Avoid/Reduce | Security and Privacy | Mitigating |
| AR-010 | Database migrations cause lock contention during deployment | 3 | 4 | 12 | Reduce | Backend and DBA | Mitigating |
| AR-011 | Backup exists but restoration fails during an incident | 2 | 5 | 10 | Reduce | DevOps | Mitigating |
| AR-012 | Mobile-store review or rollout delay blocks urgent client fixes | 3 | 4 | 12 | Reduce | Mobile and Product | Monitoring |
| AR-013 | Feature flags remain permanently active and increase behavioral complexity | 3 | 3 | 9 | Reduce | Engineering | Monitoring |
| AR-014 | External push, email, CDN, or object-storage outage affects user journeys | 3 | 4 | 12 | Reduce/Transfer | DevOps | Monitoring |
| AR-015 | Rapid service extraction introduces distributed-system complexity before readiness | 2 | 4 | 8 | Avoid | Architecture | Monitoring |

## 6. Example detailed record

### AR-003: Stale offline entitlement

**Description:** A device may continue to provide premium offline playback after the server-side subscription has expired or been revoked.

**Causes:**

- prolonged lack of connectivity;
- incorrect local grace-period calculation;
- clock manipulation;
- failed revocation synchronization;
- manifest or entitlement-cache defects.

**Consequences:**

- revenue leakage;
- inconsistent experience across devices;
- support disputes;
- bypass of product policy.

**Preventive controls:**

- signed, versioned download manifests;
- server-defined offline grace windows;
- monotonic elapsed-time checks where supported;
- bounded content leases;
- no client-authoritative subscription state;
- forced reconciliation before renewing offline access.

**Detective controls:**

- offline access beyond grace metric;
- reconciliation rejection counts;
- unusual device clock changes;
- repeated manifest-refresh failures.

**Response trigger:** Any confirmed access beyond the maximum approved grace period creates a security and revenue incident and pauses related releases until contained.

## 7. Risk treatment strategies

### Avoid

Remove the activity or design choice creating unacceptable risk. Examples include rejecting client-authoritative entitlements or public premium-media buckets.

### Reduce

Introduce preventive, detective, and corrective controls to lower likelihood or impact.

### Transfer

Use contracts, managed providers, insurance, or shared responsibility where appropriate. Accountability for architecture correctness remains internal.

### Accept

Accept residual risk only when:

- the exposure is understood;
- mandatory obligations remain satisfied;
- an accountable owner approves;
- monitoring exists;
- the acceptance has an expiry or review date.

## 8. Indicators and early warnings

Risk indicators should be measurable. Examples:

- growth of cross-module dependency violations;
- migration duration and lock-wait time;
- entitlement reconciliation failures;
- dead-letter queue growth;
- backup-restore test age;
- mobile crash-free session regression;
- dependency vulnerability age;
- cost-per-active-user trend;
- provider error rate and latency;
- privacy redaction violations;
- feature flags past expiry.

Indicators must have owners, thresholds, and links to dashboards or reports.

## 9. Review process

The register is reviewed:

- monthly during active development;
- before production launch;
- before extracting a module into an independent service;
- after major architecture changes;
- after severity-one or severity-two incidents;
- when a critical dependency or provider changes;
- during quarterly operational reviews after launch.

Critical and high risks must appear in planning and release-governance discussions until reduced or formally accepted.

## 10. Escalation rules

A release must be delayed or constrained when:

- a critical risk lacks an accountable owner;
- required mitigation is incomplete and no approved compensating control exists;
- child safety, privacy, authentication, entitlement, or data integrity may be violated;
- backup restoration, rollback, or incident response is not credible;
- known exposure exceeds the documented release threshold.

## 11. Relationship to other documents

- `16_Known_Technical_Debt.md` records existing compromises and remediation work.
- `13_Resilience_and_Failure_Mode_Catalog.md` defines expected failure behavior.
- `12_Security_Control_Matrix.md` maps security controls.
- `15_Architecture_Roadmap.md` schedules structural improvements.
- ADRs explain decisions that create, reduce, or accept significant risk.

## 12. Definition of done for a risk

A risk can be closed only when:

- the cause has been removed or controlled;
- evidence confirms the mitigation operates as intended;
- monitoring and ownership are established where residual exposure remains;
- related documentation and runbooks are updated;
- the owner and architecture reviewer approve closure.
