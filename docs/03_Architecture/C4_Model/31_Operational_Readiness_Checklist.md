# Operational Readiness Checklist

Version: 1.0.0  
Status: Active  
Owners: Architecture, Engineering, QA, Security, DevOps, Product  
Last reviewed: 2026-07-15

## 1. Purpose

This checklist defines the minimum evidence required before a capability, service, major integration, or release is considered operationally ready.

Operational readiness means more than successful implementation. The capability must be deployable, observable, supportable, recoverable, secure, documented, and safe to operate under expected failure conditions.

## 2. Usage

The checklist applies to:

- production launch;
- major feature launches;
- new bounded contexts or extracted services;
- new external providers;
- significant data migrations;
- authentication, subscription, payment, entitlement, or child-safety changes;
- infrastructure replacements;
- high-risk mobile releases.

Each item must be marked:

- `PASS`;
- `FAIL`;
- `NOT APPLICABLE` with justification;
- `EXCEPTION APPROVED` with owner and expiry.

## 3. Ownership

| Area | Accountable owner |
|---|---|
| Product behavior | Product owner |
| Architecture | Architecture owner |
| Backend and data | Backend owner |
| Mobile behavior | Mobile owner |
| Quality evidence | QA owner |
| Security and privacy | Security/privacy owner |
| Infrastructure and operations | DevOps owner |
| Release decision | Release owner |

No single person should approve every area for a high-risk release.

## 4. Scope and architecture

- [ ] The capability has a clearly defined business purpose and owner.
- [ ] The affected bounded contexts and authoritative data owners are identified.
- [ ] Synchronous and asynchronous dependencies are documented.
- [ ] New architecture decisions are captured in ADRs.
- [ ] The implementation conforms to approved module boundaries.
- [ ] No direct cross-context table or repository access has been introduced.
- [ ] Failure behavior is defined for each dependency.
- [ ] Extraction or deployment topology assumptions are documented.
- [ ] Architecture diagrams are updated where topology or flows changed.
- [ ] Known limitations and technical debt are recorded.

## 5. Functional correctness

- [ ] Acceptance criteria are complete and approved.
- [ ] Critical happy paths pass automated validation.
- [ ] Negative and edge cases are covered.
- [ ] Retry behavior does not create duplicate business effects.
- [ ] Concurrency behavior has been considered and tested where relevant.
- [ ] State transitions reject invalid transitions.
- [ ] User-visible errors are understandable and mapped to stable error codes.
- [ ] Administrative operations are authorized and auditable.
- [ ] Feature-flag behavior is tested both enabled and disabled.
- [ ] Rollout cohorts and eligibility rules are deterministic.

## 6. API and event contracts

- [ ] OpenAPI or equivalent synchronous contracts are current.
- [ ] Request and response validation rules are documented.
- [ ] Error contracts and correlation identifiers are defined.
- [ ] Idempotency requirements are explicit.
- [ ] Pagination, filtering, sorting, and limits are bounded.
- [ ] Backward compatibility with supported mobile clients is verified.
- [ ] Event schemas are versioned.
- [ ] Consumers tolerate additive fields.
- [ ] Event ownership, routing, queues, retry, and dead-letter behavior are documented.
- [ ] Contract tests pass for producers and consumers.

## 7. Data readiness

- [ ] Authoritative storage for each data element is identified.
- [ ] Schema migrations are versioned and reviewed.
- [ ] Applied migrations are forward compatible with rollout and rollback plans.
- [ ] Expand-and-contract is used for incompatible schema evolution.
- [ ] Large backfills have a separate, resumable execution plan.
- [ ] Backfills are idempotent and observable.
- [ ] Index impact and lock behavior have been evaluated.
- [ ] Data validation and reconciliation queries exist.
- [ ] Retention and deletion behavior are defined.
- [ ] Restore implications for newly introduced data are documented.

## 8. Security readiness

- [ ] Authentication requirements are enforced server-side.
- [ ] Authorization checks include ownership, role, entitlement, and elevation where applicable.
- [ ] Threat modeling is complete for security-sensitive changes.
- [ ] Secrets are stored outside source code and images.
- [ ] Tokens, passwords, PINs, receipts, and signed URLs are excluded from logs.
- [ ] Rate limiting and abuse protections are configured.
- [ ] Input validation and output encoding are applied.
- [ ] Uploaded files are validated and scanned where relevant.
- [ ] Dependency and container vulnerability scans pass policy.
- [ ] Security events are auditable.
- [ ] Emergency revocation or containment procedures exist.

## 9. Privacy and child safety

- [ ] Data collection is limited to documented purposes.
- [ ] Child-related data is minimized.
- [ ] Analytics events use approved allow-listed fields.
- [ ] External providers receive only necessary data.
- [ ] Retention periods are documented.
- [ ] Account and profile deletion workflows include the new capability.
- [ ] Data export includes relevant user-owned records where required.
- [ ] Child-facing communication is age appropriate and non-manipulative.
- [ ] Marketing is not directed to child profiles.
- [ ] Parent Zone controls cannot be bypassed through deep links, notifications, or offline state.

## 10. Reliability and resilience

- [ ] Timeouts are configured for external and internal network calls.
- [ ] Retries are bounded, classified, and use backoff with jitter.
- [ ] Non-retryable failures are not retried blindly.
- [ ] Circuit breaking or load shedding is used where justified.
- [ ] Queue consumers are idempotent.
- [ ] Dead-letter handling and replay procedures are defined.
- [ ] Cache failure behavior is safe and documented.
- [ ] Dependency outages have been simulated.
- [ ] Partial failure does not corrupt authoritative state.
- [ ] Recovery after restart or redeployment is verified.
- [ ] Single points of failure are documented and accepted or mitigated.

## 11. Performance and capacity

- [ ] Performance objectives are defined for affected journeys.
- [ ] Load-test profiles are documented and reproducible.
- [ ] p50, p95, p99, throughput, and error rate are measured as appropriate.
- [ ] Database query plans and indexes are reviewed for critical paths.
- [ ] Cache behavior is tested for warm, cold, and unavailable states.
- [ ] Queue throughput and backlog recovery are validated.
- [ ] Object-storage and CDN behavior are validated for media flows.
- [ ] Mobile memory, startup, frame, and battery impact are evaluated.
- [ ] Capacity thresholds and scaling triggers are defined.
- [ ] Cost impact is estimated and accepted.

## 12. Observability

- [ ] Structured logs use stable fields.
- [ ] Correlation and trace context propagate across the complete flow.
- [ ] Sensitive data is redacted or omitted.
- [ ] Technical metrics exist for rate, errors, duration, and saturation.
- [ ] Business indicators exist for the capability's critical outcomes.
- [ ] Dashboards are created or updated.
- [ ] Alerts are actionable and linked to runbooks.
- [ ] Alert severity and ownership are defined.
- [ ] Health checks reflect actual readiness without exposing sensitive details.
- [ ] Telemetry cardinality and retention are controlled.
- [ ] A support engineer can trace a failed transaction using approved identifiers.

## 13. Deployment and rollback

- [ ] Build artifacts are immutable and traceable to source commit.
- [ ] CI quality gates pass.
- [ ] Deployment steps are automated or precisely documented.
- [ ] Environment-specific configuration is validated before rollout.
- [ ] Feature flags have owner, purpose, expiry, and safe default.
- [ ] Database changes are compatible with mixed application versions.
- [ ] Rollback or safe forward-fix procedure is documented.
- [ ] Rollback has been rehearsed for high-risk changes.
- [ ] Progressive rollout and halt thresholds are defined.
- [ ] Post-deployment smoke tests exist.
- [ ] Change records include exact artifact and migration versions.

## 14. Backup and recovery

- [ ] New authoritative data is included in backup scope.
- [ ] RPO and RTO expectations are documented.
- [ ] Restoration dependencies and order are understood.
- [ ] Object references remain consistent after restoration.
- [ ] Encryption keys and secrets required for recovery are recoverable securely.
- [ ] Restore procedures have been tested within the approved interval.
- [ ] The capability can reconcile external provider state after restoration.
- [ ] Recovery does not silently re-send unsafe commands or notifications.

## 15. Mobile readiness

- [ ] Supported iOS and Android versions are defined.
- [ ] Representative low-, mid-, and high-range devices were tested.
- [ ] Offline and connectivity-transition behavior is validated.
- [ ] Secure storage behavior is verified.
- [ ] Background audio and lifecycle transitions are tested.
- [ ] Push deep links respect authentication and Parent Zone gates.
- [ ] Store purchase and restore flows are tested against sandbox providers.
- [ ] Forced and recommended upgrade behavior is validated.
- [ ] Accessibility checks pass for core journeys.
- [ ] Crash reporting and release version telemetry are enabled.

## 16. External-provider readiness

- [ ] Provider ownership and contract details are recorded.
- [ ] Credentials and environments are separated.
- [ ] Webhook signatures or callback authenticity are validated.
- [ ] Provider retries and duplicate callbacks are handled idempotently.
- [ ] Rate limits, quotas, and timeout behavior are known.
- [ ] Failure and degradation behavior are defined.
- [ ] Reconciliation jobs exist for stateful integrations.
- [ ] Provider status and errors are observable.
- [ ] Data-sharing and privacy implications are approved.
- [ ] Exit or replacement strategy is documented for critical providers.

## 17. Support and incident readiness

- [ ] A runbook describes normal operation, failure symptoms, diagnosis, mitigation, and recovery.
- [ ] Support-safe identifiers are available to users and operators.
- [ ] On-call ownership is defined.
- [ ] Escalation paths are current.
- [ ] Severity classification is understood.
- [ ] Manual remediation actions are authorized and audited.
- [ ] Customer communication templates exist for likely severe failures.
- [ ] Incident responders can disable or contain the capability safely.
- [ ] Post-incident evidence can be reconstructed from logs, traces, metrics, and audit records.

## 18. Documentation and training

- [ ] Architecture documentation is current.
- [ ] API, event, data, and operational documents are current.
- [ ] User-facing help or support material is updated where necessary.
- [ ] Developers and operators understand the new failure modes.
- [ ] New manual procedures have named trained owners.
- [ ] Temporary migration or rollout steps have expiry and cleanup tasks.

## 19. Launch criteria

A launch may proceed only when:

- all mandatory security, privacy, child-safety, integrity, and recovery items pass;
- critical and high risks have approved treatment;
- monitoring and containment are available before exposure begins;
- known exceptions are explicit, owned, time-bounded, and approved;
- the release owner records the final decision and evidence.

## 20. Stop conditions

Deployment or rollout must be halted when:

- authorization, profile isolation, or entitlement behavior is incorrect;
- unexpected child-data exposure is detected;
- duplicate financial or destructive effects occur;
- migration integrity cannot be established;
- rollback and forward recovery are both unsafe;
- critical alerts or telemetry are unavailable;
- error rate, latency, crash rate, or queue backlog crosses the approved halt threshold;
- external-provider responses cannot be reconciled reliably.

## 21. Post-launch validation

After launch, validate:

- smoke-test outcomes;
- authentication and authorization success/failure distribution;
- latency, error, and saturation indicators;
- queue lag, retries, and dead letters;
- migration and backfill progress;
- mobile crash-free sessions and supported-version traffic;
- provider error and reconciliation state;
- privacy and logging safeguards;
- user-support signals;
- cost and capacity changes.

The observation window must be proportional to release risk.

## 22. Readiness record template

```text
Capability or release:
Version / commit:
Release owner:
Review date:
Affected environments:
Risk classification:

Architecture: PASS / FAIL / N/A / EXCEPTION
Security: PASS / FAIL / N/A / EXCEPTION
Privacy: PASS / FAIL / N/A / EXCEPTION
Quality: PASS / FAIL / N/A / EXCEPTION
Reliability: PASS / FAIL / N/A / EXCEPTION
Performance: PASS / FAIL / N/A / EXCEPTION
Operations: PASS / FAIL / N/A / EXCEPTION
Recovery: PASS / FAIL / N/A / EXCEPTION
Mobile: PASS / FAIL / N/A / EXCEPTION

Approved exceptions:
Evidence links:
Rollout plan:
Rollback or containment plan:
Final decision:
Approvers:
```

## 23. Definition of operationally ready

A capability is operationally ready when:

- it is correct and secure;
- its data and contracts are controlled;
- expected failures are survivable;
- telemetry makes behavior visible;
- operators can diagnose and recover it;
- releases and rollbacks are credible;
- privacy and child-safety requirements are satisfied;
- evidence is current and approved;
- remaining risk is explicit and owned.
