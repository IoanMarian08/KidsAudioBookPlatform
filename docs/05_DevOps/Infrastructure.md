# Infrastructure Architecture and Operations

Version: 2.0.0  
Status: Production deployment blueprint (provider-neutral)  
Owner: Platform / DevOps

## 1. Target topology

Use a small operational footprint for the MVP: load balancer/API ingress; stateless Spring Boot API; isolated worker process; managed or properly operated PostgreSQL, Redis and RabbitMQ; private object storage with CDN; centralized metrics/logs/traces; secret management and audited deployment pipeline. Flutter and Admin Dashboard consume HTTPS endpoints.

~~~mermaid
flowchart LR
    Client[Flutter and Admin] --> TLS[HTTPS ingress / WAF]
    TLS --> API[Spring Boot API]
    API --> PG[(PostgreSQL)]
    API --> Redis[(Redis)]
    API --> MQ[(RabbitMQ)]
    API --> Media[Private Object Storage]
    MQ --> Worker[Background Worker]
    Worker --> PG
    Worker --> Media
    Media --> CDN[CDN signed delivery]
    API --> Obs[Metrics Logs Traces]
    Worker --> Obs
~~~

## 2. Environment separation

| Environment | Intent | Rules |
|---|---|---|
| Local | Fast developer feedback | Docker Compose and fake/sandbox integrations |
| CI | Ephemeral reproducibility | Disposable dependencies; never production secrets |
| Staging | Realistic pre-prod validation | Isolated databases/buckets/credentials, provider sandbox |
| Production | Customer workloads | Least privilege, backups, alerts, controlled releases |

Production and staging must not share encryption keys, store identifiers, DB instances, queues or customer datasets. Test data must be synthetic or anonymized.

## 3. Network and identity

Public exposure is restricted to ingress and approved CDN endpoints. Databases, Redis, message broker and object storage admin consoles use private networks. CI/CD deploy identities are scoped by environment. Require TLS externally and for internal traffic where the infrastructure supports/needs it. SSH/RDP access is not a default operational path.

- No hard-coded credentials or secrets in images, env templates, logs or README files.
- Rotate signing keys and secrets with a staged overlap plan.
- Apply inbound and outbound allowlists where appropriate; audit third-party endpoints.
- Separate service accounts for API, worker, migrations and observability.

## 4. Resource boundaries

API replicas are stateless. Session/device entitlement authority lives in persistent backend data; caches may accelerate reads but are not authoritative. Workers have bounded concurrency and idempotent jobs. Database pools are budgeted across all replicas.

Initial capacity estimates must include peak request rate, concurrent listeners, media egress, storage, background-job throughput and reserve headroom. Scale API and worker independently based on saturation/queue age, not only CPU.

## 5. Data and media

PostgreSQL uses durable volumes or a managed service with PITR. Redis persistence strategy depends on usage; lost cache data must be recoverable from authoritative sources. RabbitMQ uses durable queues where needed, DLQ and monitoring. Object storage uses private originals, versioned keys, controlled uploads and CDN signing. All production media asset lifecycle steps are auditable.

## 6. Infrastructure-as-code

Choose an IaC tool before production; keep modules for network, compute, storage, database, secrets, broker, observability and DNS/TLS. Plan changes must be reviewed; state files may include sensitive metadata and must be secured. Enforce tag conventions: application, environment, owner, cost-center, data classification.

## 7. Failure and recovery

| Failure | Safe behavior | Operational response |
|---|---|---|
| Redis unavailable | API degrades to DB where safe | Alert and restore cache |
| RabbitMQ unavailable | Durable outbox buffers events | Restore broker and drain lag |
| CDN failure | Preserve player state, retry/fallback if approved | Incident and provider escalation |
| PostgreSQL outage | Fail closed for writes/entitlements | Activate DB recovery runbook |
| Worker crash | Jobs remain replayable | Restart with bounded drain |
| Provider billing outage | Do not create unverified permanent grants | Reconcile after recovery |

## 8. Production readiness checks

[ ] Environment identities and secret stores isolated  
[ ] TLS/certificates and expiration alerts configured  
[ ] Resource requests/limits and health probes configured  
[ ] Database backups/restores tested  
[ ] Object retention and CDN expiry rules reviewed  
[ ] Traces/metrics/logs connected to actionable alerts  
[ ] Deployment and rollback exercised in staging  
[ ] SLO/error-budget owners identified  
[ ] Financial and egress cost alerts installed

Related: [Deployment](Deployment.md), [Backup and Recovery](Backup_Recovery.md), [Software Architecture](../03_Architecture/Software_Architecture.md).
