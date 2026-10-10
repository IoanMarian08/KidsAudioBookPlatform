# Integration and Contract Testing

Version: 2.0.0  
Status: Required quality standard  
Owner: Backend / QA

## 1. Purpose

Test interactions within **each independently deployed Spring Boot microservice** and across remote service boundaries, PostgreSQL, Redis, RabbitMQ, object storage and provider contracts. Each service must own a distinct logical database and migration history ([ADR-0015](../00_Project/ADR/ADR-0015-microservices-from-first-release.md)). Unit tests cannot detect broken Flyway migrations, SQL mappings, outbox transactions, event serialization or API authorization filters.

## 2. Test environment

Use Testcontainers for **service-owned PostgreSQL databases** and RabbitMQ; Redis and S3-compatible storage can use containers or standards-compliant fixtures. Use a **different database role for each service** and verify that foreign database SQL access is denied. Versions should match production major versions. Migrations run from an empty database as part of test bootstrap.

External App Store/Play APIs and push/email providers use recorded sandbox contract fixtures or mocks; never use live production endpoints for CI.

## 3. Database tests

- Verify **each service's independent Flyway migrations** apply in order and on representative upgrade paths.
- Check uniqueness/foreign keys/null handling and optimistic locking.
- Verify account-scoped queries cannot return foreign child profiles.
- Assert local transaction boundaries: business mutation and **service-owned outbox** record commit together; cross-service operations never rely on one shared DB transaction.
- Test pagination with equal sort keys and empty/large datasets.
- Confirm indexes for critical queries with representative data where warranted.
- Verify rollback on expected exception and safe replay after an interrupted operation.

### Cross-service REST contract and security tests

Validate REST compatibility for old/new service versions, end-user and workload identity, downstream profile/Parent Zone ownership, request-deadline propagation and failure mapping. Simulate peer timeout, 503, circuit-open, stale projection and gateway bypass. Producer/consumer releases must be independently deployable without lockstep. Include explicit negative tests against service database boundaries.

## 4. Messaging and outbox tests

~~~mermaid
sequenceDiagram
    participant API
    participant DB as PostgreSQL
    participant Pub as Outbox publisher
    participant MQ as RabbitMQ
    participant Worker
    API->>DB: Commit business change + event
    Pub->>DB: Load pending outbox event
    Pub->>MQ: Publish event
    MQ-->>Pub: Confirm
    MQ->>Worker: Deliver
    Worker->>DB: Idempotency check + effect
    MQ->>Worker: Redelivery (duplicate)
    Worker->>DB: Deduplicate safely
~~~

Cover failure before publish, failure after broker ack but before outbox status update, duplicate delivery, out-of-order updates, poison payload, retries and DLQ. Exact-once network delivery is not assumed.

## 5. API contract checks

OpenAPI request/response, status codes, validation and versioning must match implementation. For each secured endpoint test unauthenticated, wrong role, wrong account, missing profile and expired elevated session, not only successful requests.

Use representative JSON snapshots/contract assertions rather than serializing JPA entities directly. Unknown optional fields should follow compatibility policy; removed required fields break consumers and block release.

## 6. Media and entitlement integration

Test signed URL grant expiry, private bucket permissions, audio range request behavior through approved integration environments, malware scan status gating, story takedown/cache invalidation and provider reconciliation of refund/renewal.

## 7. Isolation and cleanup

Each test owns its fixtures and cleans its data transactionally or by disposable test container. Avoid relying on the previous test's side effects. Sanitize logs and redact signed URLs.

## 8. Release gates

[ ] Fresh and upgrade migrations pass  
[ ] Repository ownership isolation proven  
[ ] Outbox producer/consumer contract and replay proven  
[ ] Billing sandbox states reconciled correctly  
[ ] Media authorization and takedown pass  
[ ] API compatibility and error contracts pass  
[ ] No real user data or production integrations involved  

Related: [Testing Strategy](Testing_Strategy.md), [Event Catalog](../03_Architecture/Event_Catalog.md), [Database Design](../03_Architecture/Database_Design.md).
