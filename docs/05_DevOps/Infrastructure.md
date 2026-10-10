# Infrastructure Architecture and Operations

Version: 2.0.0  
Status: Production deployment blueprint (provider-neutral)  
Owner: Platform / DevOps

## 1. Target topology

**Architecture is microservices-first**, [ADR-0015](../00_Project/ADR/ADR-0015-microservices-from-first-release.md). Production requires individually buildable and deployable services for identity, profiles, catalog, media, playback, billing, notifications and admin; an optional advertising-policy service is disabled pending legal/product review. Workers belong to the service that owns their job/data.

~~~mermaid
flowchart TB
  Client[Flutter / Admin] --> GW[HTTPS API Gateway / WAF]
  subgraph Runtime[Private independently deployed microservices]
    ID[identity-service]
    P[profiles-service]
    C[catalog-service]
    M[media-service / worker]
    PL[playback-service]
    B[billing-service / worker]
    N[notifications-service / worker]
    A[admin-service]
  end
  GW --> ID
  GW --> P
  GW --> C
  GW --> M
  GW --> PL
  GW --> B
  GW --> N
  GW --> A
  PL --> C
  PL --> P
  PL --> B
  PL --> M
  subgraph Infrastructure[Stateful shared infrastructure; isolated service credentials]
    PG[(Separate PostgreSQL logical DBs)]
    Redis[(Redis)]
    MQ[(RabbitMQ)]
    Storage[(Private object storage)]
  end
  ID --> PG
  P --> PG
  C --> PG
  M --> PG
  PL --> PG
  B --> PG
  N --> PG
  A --> PG
  B --> MQ
  C --> MQ
  MQ --> N
  M --> Storage
  Storage --> CDN[CDN]
  Client --> CDN
~~~

PostgreSQL *infrastructure* may be shared to reduce early expense, but **each service has a separate logical database, DB user and Flyway history**. No service connects to another service's database. REST calls use private authenticated networking with deadlines; events use RabbitMQ outbox/inbox.

The deployment orchestrator (Kubernetes vs managed containers) is pending an infrastructure decision; requirements include independent service rollout, autoscaling, secrets injection, health probes, network policies, resource isolation and centralized tracing.


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
- Separate workload identities, service DB users, migration roles and access policies for **each** deployed microservice and its workers.

## 4. Resource boundaries

Every service's API replicas are stateless. Identity and billing maintain their own authoritative databases; caches only accelerate reads. Workers use only their owning service's database, with bounded concurrency and idempotent jobs. Pool budgets are tracked **per service and across the shared PostgreSQL infrastructure**.

Initial capacity estimates must include peak request rate, concurrent listeners, media egress, storage, background-job throughput and reserve headroom. Scale **each service and its workers independently** based on per-service p95, error rate, request concurrency, CPU/memory, DB pressure and queue lag.

## 5. Data and media

Every PostgreSQL logical service database has independent ownership, migrations, backups, restore evidence and retention; databases may share a managed cluster with PITR but not SQL/table access. Redis persistence strategy depends on usage; lost cache data must be recoverable from authoritative sources. RabbitMQ uses durable queues where needed, DLQ and monitoring. Object storage uses private originals, versioned keys, controlled uploads and CDN signing. All production media asset lifecycle steps are auditable.

## 6. Infrastructure-as-code

Choose an IaC tool before production; keep modules for network, compute, storage, database, secrets, broker, observability and DNS/TLS. Plan changes must be reviewed; state files may include sensitive metadata and must be secured. Enforce tag conventions: application, environment, owner, cost-center, data classification.

## 7. Failure and recovery

| Failure | Safe behavior | Operational response |
|---|---|---|
| Redis unavailable | API degrades to DB where safe | Alert and restore cache |
| RabbitMQ unavailable | Durable outbox buffers events | Restore broker and drain lag |
| CDN failure | Preserve player state, retry/fallback if approved | Incident and provider escalation |
| Service database outage | Only that owning service degrades; authorizations fail closed where uncertain | Restore service DB, replay owned inbox/outbox, verify dependent service behavior |
| Worker crash | Jobs remain replayable | Restart with bounded drain |
| Provider billing outage | Do not create unverified permanent grants | Reconcile after recovery |

## 8. Production readiness checks

[ ] Environment identities and secret stores isolated  
[ ] TLS/certificates and expiration alerts configured  
[ ] Resource requests/limits and health probes configured  
[ ] **Every service** database has scoped credentials, backup/restore tests and cross-database access-denial evidence  
[ ] Object retention and CDN expiry rules reviewed  
[ ] Traces/metrics/logs connected to actionable alerts  
[ ] Deployment and rollback exercised in staging  
[ ] SLO/error-budget owners identified  
[ ] Financial and egress cost alerts installed

Related: [Deployment](Deployment.md), [Backup and Recovery](Backup_Recovery.md), [Software Architecture](../03_Architecture/Software_Architecture.md).
