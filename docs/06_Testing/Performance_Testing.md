# Performance and Capacity Testing

Version: 2.0.0  
Status: Required pre-release plan  
Owner: Performance Engineering / DevOps

## 1. Performance baselines

Reference targets follow [Performance Guidelines](../03_Architecture/Performance_Guidelines.md): read API p95 <= 400 ms, write API p95 <= 700 ms, catalog p95 <= 500 ms, progress p95 <= 400 ms, good-network playback start <= 2 s, and 99.9% target core API availability. These are proposed goals until a realistic workload is established.

Always report p50/p95/p99, throughput, error rate and resource saturation together.

## 2. Workload model

Define reference population and load prior to testing: concurrent child sessions, active parents, story catalog size, storage bytes, free/premium ratio, requests per playback session, app-start bursts, progress sync batches, verified purchase webhook spikes and content uploads.

Keep CDN/media byte load separate from backend API requests; audio should stream from object storage/CDN, not transit the API server.

## 3. Required tests

| Test | Goal | Signals |
|---|---|---|
| Baseline | Compare builds with same data | p95/p99, SQL count, CPU |
| Load | Validate expected busy-hour traffic | Errors, DB/Redis pool, GC |
| Stress | Discover overload and safe refusal | Saturation, 429/503 behavior |
| Spike | Detect onboarding/notification traffic burst | Recovery time, queue lag |
| Soak | Reveal leaks and gradual degradation | Heap, threads, connections |
| Failover | Validate Redis/broker/CDN partial failure | Critical journey availability |
| Mobile | Measure low/mid-tier startup and playback | Jank, memory, battery |
| CDN | Test signed URL, range requests and cache | Byte delivery, egress cost |

## 4. Example scenario mix

Use a documented starting mix (adjust after analytics): 45% catalog browse, 20% story detail, 10% playback grant, 15% progress write, 5% parent/profile operations and 5% entitlement or admin. This is **test-data illustration**, not an observed production mix.

Don't test with an empty DB. Include realistic number of series, stories, child profiles, progress rows, notification history and recent outbox events.

## 5. Database and queue checks

Inspect slow SQL with EXPLAIN (ANALYZE, BUFFERS) only in safe test environments; identify N+1 queries and lock contention. Track DB connection pool occupancy, Redis hit/eviction, RabbitMQ oldest-message age, consumer retries and dead letters.

## 6. Safe execution

Never run uncontrolled stress/soak tests against production. Use synthetic accounts and a designated environment with clear resource/cost limits. Prevent accidental real push notifications or purchases.

## 7. Reporting template

~~~text
Build SHA / environment / test date:
Scenario and workload parameters:
Dataset volume and shape:
p50/p95/p99 and error rate:
Peak RPS, backlog and throughput:
Infrastructure saturation:
Baseline comparison and regression:
Root cause / owner / next action:
Decision: PASS / CONDITIONAL / FAIL
~~~

## 8. Release acceptance

No substantial regression from agreed baseline without approval. New capacity claims require reproducible evidence, and any SLO failure must have an owner and remediation before broad rollout.

Related: [Non-functional Requirements](../01_Product/Non_Functional_Requirements.md), [Monitoring](../05_DevOps/Monitoring.md).
