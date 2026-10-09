# Blueprint 06 — Parent Privacy, Export and Account Deletion

Version: 1.0  
Status: Design blueprint; legal retention policy pending  
Owners: Identity, Data Governance, Security, Product

## 1. Goal

A verified parent can request deletion or export of their family account data without exposing child information to third parties or destroying required audit/financial records prematurely. Child profile information is minimized throughout its lifecycle.

**Normative references:** [Product Bible](../00_Project/Product_Bible.md), [Security Architecture](../03_Architecture/Security_Architecture.md), [Data Retention Map](../03_Architecture/C4_Model/14_Data_Retention_and_Privacy_Map.md), [Database Design](../03_Architecture/Database_Design.md) §26, [API Specification](../03_Architecture/API_Specification.md) §20 and [Decision Register](../00_Project/DECISION_REGISTER.md).

## 2. Public contract and authorization

Current API includes POST /me/deletion-request and POST /me/deletion-request/cancel. The account owner must be authenticated with elevated Parent Zone proof where account deletion is considered sensitive. Never accept arbitrary accountId from the client for this workflow.

Data export needs a documented consented request flow and an explicit API contract before implementation; **no export endpoint is inferred** from this blueprint.

## 3. Data-classification and retention

| Data | Typical owner | Handling |
|---|---|---|
| Adult account/session records | Identity | Revoke credentials on deletion; erase/anonymize when permitted |
| Child profiles, preferences | Profiles | Minimize birth/age data; erase or anonymize with parent request |
| Listening progress, downloads, favorites | Playback/Media | Purge account-scoped derived content; revoke grants |
| Subscriptions/purchase events | Billing | Preserve only records required by approved finance/tax obligations |
| Notification inbox/devices | Notifications | Stop push and clean registrations promptly |
| Audit trail | Administration/Audit | Retain only mandated, appropriately pseudonymized records |
| Original catalog/media | Catalog/Media | Licensed global content remains if not owned by account |

**Retention durations are deliberately not invented.** Legal/Product must decide by jurisdiction; record in DEC-008 and map to archival/purge automation.

## 4. Deletion state model

~~~mermaid
stateDiagram-v2
  [*] --> Active
  Active --> Requested: Verified parent request
  Requested --> Cancelled: Parent cancels in policy window
  Requested --> InProgress: Deletion scheduler
  InProgress --> Completed: Domain erasures verified
  InProgress --> RetryPending: Temporary dependency failure
  RetryPending --> InProgress: Bounded retry
~~~

Never report Completed while a domain erase is still pending. Design cancellation semantics and grace window before launch. Asynchronous workers use idempotency and a durable job/outbox trail.

## 5. Deletion workflow

1. Parent enters protected zone; API authenticates ownership and captures a durable request with unique ID.
2. Deletion service marks account state appropriately and schedules work; no unverified deletion trigger from a child or push link.
3. Revoke sessions, refresh credentials, device registrations, download grants and optional outbound messages.
4. Remove/anonymize profiles, progress, history, preferences and account-specific analytics by owning context.
5. Billing and Audit apply their approved legal-retention exceptions, with recorded justification and access restriction.
6. Verify completion by domain, record status and communicate to parent through an approved channel without leaking PII.
7. Account re-registration and previously cached devices must not resurrect deleted profiles or subscription links accidentally.

## 6. Recovery, audit and threat scenarios

| Case | Safe behavior |
|---|---|
| Foreign account deletion request | Reject without confirming its existence |
| Parent challenge expired | Request not accepted |
| Repeat request / worker replay | Same logical deletion; no duplicate external side effects |
| Partial failure after session revocation | Job retries safely, no false completed state |
| Account has active subscription | Tell parent how store-managed billing is handled; do not falsely claim store cancellation |
| Device offline during deletion | Local caches/download grants cannot regain server authorization after reconnect |
| Required tax/audit retention | Minimize, restrict and set auditable purge expiration |
| Export link guessed/expired | Reject via signed short-lived authorized download |

## 7. Release gates

Data map, retention matrix by country, consent notices, request/cancel time window, backup deletion strategy and operator controls are legal/security decisions. QA tests cross-domain erasure, revoked access, mixed offline devices, purchase/legal exceptions, restore conflicts and auditability. Implement only when approved policies are explicit.
