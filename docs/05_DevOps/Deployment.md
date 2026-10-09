# Deployment and Release Runbook

Version: 2.0.0  
Status: Staging-ready runbook template, provider-specific commands TBD  
Owner: DevOps / Release Engineering

## 1. Scope

Deploy **each independently built Spring Boot microservice** (identity, profiles, catalog, media, playback, billing, notifications, admin) through the API gateway, plus its service-owned workers, admin dashboard, and supporting infrastructure. No single backend API artifact contains the whole business system. Mobile apps are delivered via Apple/Google app stores and require separate rollout/compatibility planning.

## 2. Release prerequisites

- Change set reviewed and linked to issue/PR/ADR where needed.
- Automated CI security, unit, integration, API contract and acceptance gates pass.
- Immutable image digest and SBOM available.
- The affected **owning service's** logical database migration has been tested against a staging snapshot; contract compatibility with prior/new consumer versions is proven.
- New configuration and secrets validated; required flags default off.
- Relevant SLO dashboards and incident responder known.
- Current backup and successful restore exercise are within policy.

## 3. Safe release sequence

1. Announce the affected microservice(s), contract versions, release window/owner and previous per-service digest.
2. Run non-destructive preflight: DB connectivity, queues, storage, provider connectivity, free capacity.
3. Apply additive migrations **only to each deploying service's database**; do not mutate schemas owned by peers. Avoid long locks.
4. Deploy only the affected service and its owned workers with independent canary/rolling readiness checks. Keep older service versions compatible with other live producers/consumers.
5. Execute smoke suite: login, profile, catalog, playback grant, progress, verified entitlement sandbox path and admin access.
6. Watch affected service p95/p99, 5xx, per-service database health, remote call timeouts, RabbitMQ queue lag/DLQ, signing and client E2E metrics.
7. Gradually expose feature flags; verify business-level safety and analytics.
8. Complete release record: SHA/digest, migration ID, known issues, health evidence.

## 4. Rollback and forward repair

Rollback **one service at a time** using its prior tested digest; older peer API/event versions must remain compatible with deployed consumers and each service's migrated schema. **Do not automatically roll back destructive DB schema migrations.** If data is corrupted, initiate incident handling and restore/run forward repair under approved runbook.

Trigger rollback for sustained SLO breach, security exposure, P0 user journey failure or data-integrity risk. Suspension of unsafe content or commercial features may be immediate via approved flags/admin controls.

## 5. Background workers and events

Before independently deploying a producer or consumer contract change, verify old/new versions of **separately deployed services** can coexist. Consumers must handle duplicate delivery. Queue drains/replays are supervised; never purge production queues to make dashboards green. Failed events remain in DLQ with owner and replay instructions.

## 6. Store release compatibility

Server contracts remain compatible with deployed mobile versions for a defined support window. Gate server-required fields carefully, account for app-store review delays, and ensure old clients remain safe when new entitlements or media fields are introduced.

## 7. Emergency hotfix

Use minimum review path defined in Git workflow; keep secrets and quality gates mandatory. Record incident ID, affected scope, precise steps, recovery evidence and post-incident review. Validate hotfix in staging when practical.

## 8. Verification checklist

[ ] Healthy readiness/liveness and non-regressing metrics  
[ ] Login and protected Parent Zone functional  
[ ] Published stories authorize, stream and resume  
[ ] Downloads and entitlement checks safe  
[ ] Per-service image, Flyway version, DB ownership and worker outbox/DLQ health verified  
[ ] CDN/media signing TTL correct  
[ ] Backups current and logs retained  
[ ] Rollback/feature-disable path verified  
[ ] Change documented and support informed

Related: [CI/CD](CI_CD.md), [Infrastructure](Infrastructure.md), [Monitoring](Monitoring.md), [Backup Recovery](Backup_Recovery.md).
