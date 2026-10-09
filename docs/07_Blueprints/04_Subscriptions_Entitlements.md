# Blueprint 04 — Store Purchases, Subscriptions and Entitlements

Version: 1.0  
Status: Implementation blueprint / policy gates outstanding  
Owners: Billing, Entitlements, Security, Mobile, Product

## 1. Purpose

A parent can discover plans, purchase/restore through Apple App Store or Google Play and receive accurate Premium access. The platform grants entitlement **only after server-side provider verification**. Refunds, grace periods, cancellations and delayed/repeated provider events converge to provider truth.

**Do not process payment-card data directly.** Store identifiers are configuration, not assumed final commercial offerings.

References: [API Specification](../03_Architecture/API_Specification.md) §§36–39, [Database Design](../03_Architecture/Database_Design.md) §13, [Event Catalog](../03_Architecture/Event_Catalog.md) §12, [Security Architecture](../03_Architecture/Security_Architecture.md), [Decision Register](../00_Project/DECISION_REGISTER.md).

## 2. Existing APIs

| Endpoint | Responsibility |
|---|---|
| GET /subscription-plans | Available configured plans, store product mapping and display metadata |
| GET /me/entitlements | Account's current effective features with version |
| POST /purchases/verify | Validate opaque provider transaction, then reconcile |
| GET /me/subscription | Current subscription and status |
| POST /me/subscription/restore | Re-query provider ownership and reconcile |
| POST /me/subscription/reconcile | Trigger idempotent refresh |
| Provider-specific authenticated webhook ingress | Adapter-only integration; path/signature scheme must be specified before implementation |

The client calls OS-native purchase UI only in protected Parent Zone. A client-reported success is **not** entitlement evidence. The backend must never trust prices from the mobile app.

## 3. Data ownership and constraints

Billing owns **billing.plans, billing.subscriptions, billing.purchase_events, billing.entitlements**. Store provider IDs are unique where applicable. Purchase events are append-only with unique (provider, event_id). Store no raw payment credentials and minimize receipt/provider payload retention.

Entitlements are evaluated account capabilities, not UI booleans. Effects include offline download eligibility, multiple profiles, access to Premium content, and ad suppression. Keep effective capabilities versioned and invalidate relevant caches when provider truth changes.

## 4. Subscription lifecycle

~~~mermaid
stateDiagram-v2
  [*] --> PENDING
  PENDING --> TRIAL: Verified eligible trial
  PENDING --> ACTIVE: Verified paid purchase
  TRIAL --> ACTIVE: Verified renewal
  TRIAL --> EXPIRED: Trial ends without valid renewal
  ACTIVE --> GRACE_PERIOD: Provider reports billing issue
  ACTIVE --> CANCELLED: Cancel at period end
  GRACE_PERIOD --> ACTIVE: Billing recovered
  GRACE_PERIOD --> EXPIRED: Grace ends
  ACTIVE --> REVOKED: Refund or fraud revocation
  CANCELLED --> EXPIRED: Paid term ends
  EXPIRED --> ACTIVE: New verified purchase
~~~

These labels must stay consistent with [Database Design](../03_Architecture/Database_Design.md); PAUSED and any provider-specific transitional states require an explicit policy. A cancellation request normally changes renewal preference, **not** immediate Premium rights while already paid.

## 5. Provider event processing

1. Receive provider notification over a protected endpoint with signature/JWS verification and replay-window policy.
2. Persist a redacted purchase event keyed by provider + event ID and enqueue/reconcile through outbox if necessary.
3. Resolve account ownership and provider subscription reference without allowing arbitrary account association.
4. Fetch authoritative provider state when event order or authenticity requires it.
5. Within an atomic transaction, update subscription revision, recompute entitlements and append outbox integration event.
6. Update cache only after committed state; consumers must tolerate repeated EntitlementsRecalculated.
7. If provider unavailable, mark reconciliation pending; **never permanently grant an unverified entitlement**.

~~~mermaid
sequenceDiagram
  actor Parent
  participant Mobile
  participant Store as Apple/Google Store
  participant Billing as Billing API
  participant DB as PostgreSQL
  Parent->>Mobile: Buy in Parent Zone
  Mobile->>Store: Native store purchase
  Store-->>Mobile: Opaque transaction reference
  Mobile->>Billing: POST /purchases/verify
  Billing->>Store: Verify with provider
  Store-->>Billing: Signed/authoritative state
  Billing->>DB: Save provider event and entitlements
  Billing-->>Mobile: Verified account capabilities
~~~

## 6. Edge cases and policy gates

| Case | Expected invariant |
|---|---|
| Duplicate webhook | No duplicate purchase or extra grant |
| Out-of-order expiry after newer renewal | Provider truth/version prevents false revocation |
| Refund while download exists | New rights denied; offline grant follows documented expiry/kill switch |
| Store sandbox down | Retry bounded, reconciliation pending, no fake Premium |
| User restores on another device | Parent account/provider ownership verified |
| Purchase linked to different account | Reject/resolve through support policy, never silently rebind |
| Free profile quota on downgrade | Preserve data and follow explicit profile accessibility policy |
| Trial request | Verify DEC-003 region/provider eligibility; prevent repeated abuse |

### Unapproved product decisions

The Product Bible expects monthly/annual Premium, a three-day trial and a controlled free tier; **pricing, availability, profile limits, exact grace behavior and child-directed advertising must be approved** before launch. Maintain ads disabled by feature flag until product/legal/security/store review.

## 7. Testing matrix

- Unit: entitlement state table for FREE/TRIAL/ACTIVE/GRACE/CANCELLED/EXPIRED/REVOKED; configured premium capabilities.
- Integration: verified provider samples, signature failure, purchase idempotency, unique indexes and transaction rollback.
- Contract: Apple/Google sandbox transaction types and notification versions; use provider-approved simulated payloads.
- Mobile E2E: purchase cancellation, restore purchase, pending purchase, device reinstallation, no child billing UI.
- Operations: webhook outage replay, reconciliation lag dashboard, unexpected provider duplicate rate, support audit trail.

## 8. Done criteria

Contract/API schemas, DB migration, provider adapter, signature validation, audited purchase state, idempotent reconcile, entitlements cache invalidation, security regression and release dashboard are present. Confirm all open decisions in [DEC-002–DEC-005](../00_Project/DECISION_REGISTER.md) before enabling real monetization.
