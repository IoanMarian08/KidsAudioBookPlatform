# Deployment and operations

Version: 1.0  
Status: Documentation navigation

## Start here

Production-oriented operational blueprints for an intended modular monolith, workers, PostgreSQL, Redis, RabbitMQ and private media/CDN. Example configurations are **not deployed infrastructure** and must be adapted and tested.

**Recommended first document:** [Infrastructure.md](Infrastructure.md).

## Files

| Document | What it answers |
|---|---|
| [Infrastructure.md](Infrastructure.md) | Topology, access, security, capacity |
| [Docker.md](Docker.md) | Secure OCI image guidance |
| [Docker_Compose.md](Docker_Compose.md) | Illustrative local development dependencies |
| [CI_CD.md](CI_CD.md) | Build, test and promotion gates |
| [Deployment.md](Deployment.md) | Staging/production release and rollback |
| [Monitoring.md](Monitoring.md) | SLOs, alerts, incident response and dashboards |
| [Backup_Recovery.md](Backup_Recovery.md) | Backups, PITR, restores and DR |

## How to use this area

Choose actual hosting/cloud provider, IaC, regions, secrets manager, approved RTO/RPO and budget before production. Never use example credentials as production secrets.

## Review rules

- Requirements, architecture and test evidence should remain linked, not duplicated.
- Proposed or sample configurations must be marked as such.
- Update the owner document, impacted contracts and references together.
- Record conflicting assumptions in the [Decision Register](../00_Project/DECISION_REGISTER.md).
