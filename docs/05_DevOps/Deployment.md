# Deployment and Release Runbook

Version: 2.0.0  
Status: Staging-ready runbook template, provider-specific commands TBD  
Owner: DevOps / Release Engineering

## 1. Scope

Deploy the Spring Boot API, worker, admin dashboard, object/media configurations, and supporting infrastructure. Mobile apps are delivered via Apple/Google app stores and require separate rollout/compatibility planning.

## 2. Release prerequisites

- Change set reviewed and linked to issue/PR/ADR where needed.
- Automated CI security, unit, integration, API contract and acceptance gates pass.
- Immutable image digest and SBOM available.
- Database migration checked on staging snapshot and rollback/forward-fix designed.
- New configuration and secrets validated; required flags default off.
- Relevant SLO dashboards and incident responder known.
- Current backup and successful restore exercise are within policy.

## 3. Safe release sequence

1. Announce release window/owner and record previous deployment digest.
2. Run non-destructive preflight: DB connectivity, queues, storage, provider connectivity, free capacity.
3. Apply additive migrations where the release requires new columns/tables/indexes; avoid long locks.
4. Deploy new API/worker replicas in rolling or canary mode with readiness gating.
5. Execute smoke suite: login, profile, catalog, playback grant, progress, verified entitlement sandbox path and admin access.
6. Watch p95/p99 latency, 5xx, DB pool/locks, RabbitMQ queue lag, signed URL failures and mobile error telemetry.
7. Gradually expose feature flags; verify business-level safety and analytics.
8. Complete release record: SHA/digest, migration ID, known issues, health evidence.

## 4. Rollback and forward repair

Application rollback reuses prior image digest; it must be compatible with schema already migrated. **Do not automatically roll back destructive DB schema migrations.** If data is corrupted, initiate incident handling and restore/run forward repair under approved runbook.

Trigger rollback for sustained SLO breach, security exposure, P0 user journey failure or data-integrity risk. Suspension of unsafe content or commercial features may be immediate via approved flags/admin controls.

## 5. Background workers and events

Before deploying consumer contract changes, verify producers/consumers can coexist. Consumers must handle duplicate delivery. Queue drains/replays are supervised; never purge production queues to make dashboards green. Failed events remain in DLQ with owner and replay instructions.

## 6. Store release compatibility

Server contracts remain compatible with deployed mobile versions for a defined support window. Gate server-required fields carefully, account for app-store review delays, and ensure old clients remain safe when new entitlements or media fields are introduced.

## 7. Emergency hotfix

Use minimum review path defined in Git workflow; keep secrets and quality gates mandatory. Record incident ID, affected scope, precise steps, recovery evidence and post-incident review. Validate hotfix in staging when practical.

## 8. Verification checklist

[ ] Healthy readiness/liveness and non-regressing metrics  
[ ] Login and protected Parent Zone functional  
[ ] Published stories authorize, stream and resume  
[ ] Downloads and entitlement checks safe  
[ ] Workers processing, DLQ and outbox observed  
[ ] CDN/media signing TTL correct  
[ ] Backups current and logs retained  
[ ] Rollback/feature-disable path verified  
[ ] Change documented and support informed

Related: [CI/CD](CI_CD.md), [Infrastructure](Infrastructure.md), [Monitoring](Monitoring.md), [Backup Recovery](Backup_Recovery.md).
