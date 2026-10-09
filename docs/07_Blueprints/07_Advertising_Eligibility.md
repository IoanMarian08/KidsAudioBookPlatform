# Blueprint 07 — Child-Safe Advertising Eligibility (GATED)

Version: 1.0  
Status: **Design-only — advertising must remain disabled until legal, product and store approvals**  
Owners: Product, Advertising Policy, Security, Mobile

## 1. Intent and launch gate

The Product Bible describes free-tier advertising: non-interruptive, post-session only, with an initial maximum of one ad after two completed sessions and a suggested short duration. These are product intent/configuration candidates, **not permission to ship unreviewed third-party advertising to children**.

Explicitly require DEC-004 approval for geography, age suitability, no child behavioral targeting, vendors, tracking/consent requirements, app-store rules and parent messaging. Disable ad-provider calls by default until release approval.

## 2. Architecture ownership

Advertising Policy owns eligibility rules, profile-safe counters and audited decisions, not purchase verification or child behavioral profiling. Playback emits validated completed-session facts. Entitlements provides verified Premium status. Parent restrictions and platform policy can veto a decision.

Database Design names advertising.profile_ad_counters and advertising.ad_decisions. Use only minimal scoped IDs and counts; do not send full child profiles, listening histories or personal information to an ad SDK.

## 3. Existing API paths

- POST /advertising/decisions — body includes profileId, trigger SESSION_COMPLETED and playbackSessionId.
- POST /advertising/decisions/{decisionToken}/result — records delivered/skipped/unavailable/failed outcome.

These paths remain behind feature/market allowlist and server-side parent-account/profile authorization. A client cannot claim fake completed sessions to generate eligibility, bypass Premium suppression or repeatedly redeem a decision token.

## 4. Evaluation order

~~~mermaid
flowchart TD
  A[Playback session completed] --> B{Advertising feature approved and enabled?}
  B -->|No| N[Not eligible]
  B -->|Yes| C{Verified Premium or parental restriction?}
  C -->|Yes| N
  C -->|No| D{Session count policy reached?}
  D -->|No| N
  D -->|Yes| E{Market, age, creative, consent policy permits?}
  E -->|No| N
  E -->|Yes| F[Create short-lived idempotent decision token]
  F --> G[Eligible post-session placement]
  G --> H[Result reported once]
~~~

Never place ads inside a story. Application must not require ad interaction to access essential audio controls. Do not issue a result acknowledgement before verifying a valid decision token and session identity.

## 5. Idempotency and counters

A completed listening session is counted at most once for policy purposes. Unique decision scope combines server-verified account/profile/session and policy version; replays return a consistent result. Premium activation invalidates pending eligible decisions. Count updates and emitted events should be durable/auditable under a transaction/outbox as needed.

## 6. Child safety controls

- No personal profiling or behavioral ad targeting using child data.
- No unsafe deep links, deceptive close buttons, manipulative urgency or reward pressure.
- Parent controls and opt-outs, where required by law or policy, take precedence.
- Age-appropriate creative vetting and placement restrictions are independently testable.
- Ad-providing vendor must document data flows, SDK permissions and retention.
- If creative review or compliance metadata is missing, fail **closed** to no ad.

## 7. Tests and monitoring

| Test | Required result |
|---|---|
| Feature flag off | Always ineligible; provider SDK not initialized for child flow |
| Premium activates after count threshold | Pending eligible decision suppressed |
| Mid-story session event | No ad authorization |
| Duplicate completion event | No extra counter increment |
| Unsupported country/consent | No ad |
| Forged decision token | Denied; no impression count |
| Provider outage | Story playback unaffected; safe no-ad fallback |
| Offline mode | No third-party tracking; pending state not exploited |

Audit metrics: eligibility outcomes, consent blocks, provider failure, rejected tokens, unreviewed creative attempts and reported impressions with privacy-minimized aggregation.

## 8. Non-implementation note

This blueprint intentionally does not select an ad SDK or finalize the advertised frequency/duration as a legally compliant policy. No ad integration should be activated until [DEC-004](../00_Project/DECISION_REGISTER.md) is accepted and Security Testing includes the chosen vendor.
