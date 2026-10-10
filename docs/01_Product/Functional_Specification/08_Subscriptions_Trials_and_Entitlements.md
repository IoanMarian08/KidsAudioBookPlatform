# 08 — Free/Premium, Trials, Purchases, Subscription States and Entitlements

**Actor:** adult in Parent Zone; child sees content access outcomes only.
**Requirements:** PRD-07; FR-SU-001..006.
**Owning service:** billing-service; authoritative store verification by Apple/Google providers.
**Contracts:** [API Specification](../../03_Architecture/API_Specification.md) sections 36–39; [Billing blueprint](../../07_Blueprints/04_Subscriptions_Entitlements.md).

## 1. Commercial product shape

Product Bible specifies a useful Free tier, Premium monthly/annual and an intended three-day trial. Approximately 50 Free stories are a launch target, subject to rights approval. Premium can include expanded catalog, authorized offline downloads, more profiles and no advertising if advertising is ever approved. **Exact prices, currencies, storefront products, trial eligibility, profile quotas and country restrictions must be signed off** [DEC-001..005]. No arbitrary amount or threshold is canonical.

**FS-SU-001** Parent Zone GET /subscription-plans displays only actual configured eligible plans from the authoritative service/store mapping: period, price, currency, included benefits, billing cadence, trial terms when eligible, and legally required disclosures.

**FS-SU-002** A child may encounter a Premium-labeled story but cannot initiate a purchase. UI can provide a gentle “ask a parent” hint without pressure, reward manipulation or unrestricted store links.

**FS-SU-003** Entitlements are account capabilities from GET /me/entitlements, not a trustable “isPremium” client boolean. All protected content, offline grants and quotas validate entitlement independently.

## 2. Purchase lifecycle

Steps: adult opens Parent Zone -> opens plan details -> reviews price, renewal/terms -> confirms -> native Apple/Google purchase sheet -> app receives provider transaction reference -> POST /purchases/verify to backend -> provider verification/reconciliation -> entitlements updated -> parent receives accurate result.

**FS-SU-004** No payment-card numbers are stored or processed directly by this platform. Native store UI performs purchase and applicable cancellation/management actions.

**FS-SU-005** A client success callback is not proof of purchase. Pending/unverified/invalid receipts never grant Premium. Verification can be retried idempotently; a timeout remains Pending/Unconfirmed, never automatically Active.

**FS-SU-006** Duplicate, delayed and out-of-order provider notifications must not double grant or incorrectly roll back newer verified rights. Purchase event data remains auditably associated with the right adult account.

**FS-SU-007** If the user buys on one device then signs in on another under the same authorized adult account, GET /me/entitlements and restore flows reflect provider-verified ownership, without rebinding an unrelated account.

## 3. Subscription and trial states

Visible statuses can include Free, Trial, Active Premium, Cancelled (but paid period remains), Grace/Payment Issue, Expired, Revoked/Refunded, Pending Verification and Unknown while provider reconciliation is unavailable.

**FS-SU-008** A canceled auto-renewal normally retains access through the paid period verified by the store. UI must not promise immediate loss or perpetual access incorrectly.

**FS-SU-009** Trial availability is displayed only after provider eligibility and approved country/product policy. A three-day duration is intended in Product Bible but requires [DEC-003] approval for each offer/market. Reused or ineligible trials are refused.

**FS-SU-010** Grace periods, paused state, billing retry, refund and chargeback transitions obey verified provider truth and approved policy. No service invents trial eligibility or extends paid access from an untrusted mobile timestamp.

**FS-SU-011** On refund/revocation, new Premium access and new download grants are denied immediately when authority is established. Existing offline rights follow separately approved expiry/revocation policy.

**FS-SU-012** Downgrading from Premium must not silently delete child profiles, progress, favorites or purchased history; accessible profiles/feature limits await [DEC-005].

## 4. Manage and restore

Current API supports GET /me/subscription, POST /me/subscription/restore and POST /me/subscription/reconcile.

**FS-SU-013** Subscription management shows current verified plan/status, next billing date or period end when available, and an accurate store-managed billing route. Draft copy must not imply local cancellation when it actually opens the store.

**FS-SU-014** Restore prompts provider re-verification and maps only legitimate entitlements to the authenticated parent. It cannot grant rights using another account's transaction.

**FS-SU-015** Parent can retry reconcile after an outage. During uncertainty the UI displays accurate Pending/Unavailable state, not a fabricated paid badge; service enforces safe authorization.

## 5. Free/Premium feature access matrix

| Capability | Free | Premium | Decision |
|---|---|---|---|
| Browse approved catalog | Yes | Yes | Age/parent restrictions always enforced |
| Listen to designated Free stories | Yes | Yes | Current publication/locale required |
| Listen to Premium-only stories | No | Yes if verified | Server-side grant |
| Add child profiles | Within configured policy | Within configured policy | [OPEN: DEC-005] |
| Offline downloads | As approved; do not assume | Eligible when verified | Device/TTL policy [OPEN] |
| Ambient sounds | Selected items | Expanded eligible set | Content policy [OPEN] |
| Advertising | Potentially eligible only if approved | Suppressed | [GATED: DEC-004] |
| Trial | Eligible approved offer only | N/A after activation | [OPEN: DEC-003] |
| Parent safety controls | Yes | Yes | Never paywall essential safety |

**FS-SU-016** Safety, account recovery and privacy controls are never intentionally broken on Free to force upgrading.

## 6. Failure scenarios

| Event | Parent sees | Invariant |
|---|---|---|
| Native purchase canceled | No purchase; can retry voluntarily | No charge claim |
| Provider pending | Pending verification | No unverified Premium |
| Receipt invalid or forged | Purchase not confirmed | No entitlement grant |
| Webhook delayed/duplicate | Latest verified status | Idempotent updates |
| App reinstalled | Sign in and restore where eligible | Provider/account binding verified |
| Billing provider down | Retry/temporary status | No fake trial or paid rights |
| Refund while streaming | Rights reassessed at policy boundary | No new grant |
| Expired paid period | Renewal/manage guidance in Parent Zone | State follows verified provider |
| Plan not available in locale | Explain availability | No fabricated prices |
| Excess profiles after downgrade | Parent-facing resolution | No silent data loss |

## 7. Acceptance scenarios

- **SU-AT-01:** Given an unverified purchase reference, when client reports success, then billing-service does not grant Premium.
- **SU-AT-02:** Given an active subscription, when duplicate webhook notifications arrive, then entitlements are updated once logically.
- **SU-AT-03:** Given a newer paid renewal then an older expiry event, when delivered out of order, then verified newer access remains authoritative.
- **SU-AT-04:** Given a purchase from account A, when account B tries to restore it, then B receives no unauthorized entitlement.
- **SU-AT-05:** Given a paid plan canceled for future renewal, when within verified paid period, then UI shows the correct end date and available rights.
- **SU-AT-06:** Given a refunded purchase, when new Premium media is requested, then the entitlement check denies it.
- **SU-AT-07:** Given a child on a Free profile opens Premium item, then no child checkout/payment flow is offered.
- **SU-AT-08:** Given a configured three-day trial is unavailable in the current market, then no falsely eligible trial banner appears.
- **SU-AT-09:** Given downgrade with excessive profiles, then no deletion occurs automatically.

## 8. Decisions before monetization

Resolve DEC-001 catalog rights, DEC-002 price/currency/tax, DEC-003 trial terms/store offer IDs, DEC-004 ads, DEC-005 profile/offline quotas, DEC-007 market/locale and review every app-store disclosure. Every release must be verified in Apple/Google sandbox/approved testing before real transactions.
