# 18 — Privacy-Safe Product Analytics, Feature Flags and Controlled Rollouts

**Audience:** Product, Privacy, Backend, Mobile, QA and Operations.
**Purpose:** Measure whether children can listen safely and parents can manage their family, without turning children into tracked advertising profiles.
**Sources:** [Product Bible](../../00_Project/Product_Bible.md), [NFRs](../Non_Functional_Requirements.md), [Feature Flag ADR](../../00_Project/ADR/ADR-0011-feature-flags.md), [Security Architecture](../../03_Architecture/Security_Architecture.md).

## 1. Analytics principles

**FS-ME-001** Any telemetry used for product improvement must have a defined purpose, approved retention and minimal attributes. Aggregate anonymized counters are preferred over individual-level child listening timelines.

**FS-ME-002** Never include child names, birth dates, precise age, account credentials, PINs, raw receipts, sensitive medical data, story transcript text, precise location or private media URLs in analytics or advertising SDK payloads.

**FS-ME-003** Analytics must not be a hidden dependency for story playback, Parent Zone controls, account deletion or safe offline use. Failed analytics delivery never blocks essential features.

**FS-ME-004** Consent requirements vary by launch market. If a data use requires consent, absence/withdrawal must disable that collection and not silently continue through another analytics provider [DEC-007/008].

**FS-ME-005** Device and per-profile identifiers are pseudonymous, scoped and not shared for child behavioral targeting; cross-device identity linkage requires documented privacy purpose.

## 2. Practical product metrics

| Journey | Aggregate measure | Safe interpretation | Guardrail |
|---|---|---|---|
| Adult onboarding | Sign-up completion and verification failure rate | Onboarding friction | Never log passwords or verification codes |
| First play | Time from verified account to first successful story | Product learnability | Ignore/segment network outages honestly |
| Catalog browsing | Approved story detail-to-Play ratio | Discovery effectiveness | No child-specific ad ranking |
| Playback | Qualified start, buffering, crash-free listening, completed session | Technical listening quality | No manipulative streak optimization |
| Continue Listening | Successful return to last position | Progress reliability | No sibling data joins |
| Downloads | Transfer/verify success, offline licensed play success | Travel reliability | Do not log media object secrets |
| Store purchase | Verified paid entitlement activation delay and restore success | Billing correctness | Provider data minimized |
| Parent controls | Successful saved setting, unauthorized attempt blocked | Safety usability | Never expose PIN/proof payload |
| Moderation | Review/takedown response time | Content safety | Private editorial info restricted |
| Notifications | Parent opt-out adoption and safe delivery failure | Consent effectiveness | No tracking child open behavior for ads |
| Account deletion | Request-to-completion and stalled saga count | Privacy fulfillment | Only aggregate operational identifiers |

**FS-ME-006** Metric events distinguish attempted, verified and denied actions; a button tap alone cannot count as a completed purchase, downloaded file, qualified story completion or successfully deleted account.

## 3. Event ownership and naming policy

User-visible product metrics are distinct from integration/domain events. A RabbitMQ event used by services for entitlement and deletion authority is not automatically safe to forward to an analytics provider. Each product metric must be approved separately for consent, attributes, retention and grouping.

A measurement schema record should identify:
- stable event name, version and high-level business purpose;
- source service or Flutter action;
- allowed attributes and prohibited PII;
- collection consent/legal basis by market;
- aggregation grain and retention policy;
- deduplication and sampling approach;
- business interpretation and misuse risks;
- owner and review date.

Do not use an implementation event schema as a shortcut around child privacy review.

## 4. Feature flag classes

| Type | Example | Default and safeguards |
|---|---|---|
| Operational release | Gradual new catalog screen | Off until tested, scoped by platform and approved rollout |
| Compatibility | New API schema consumer | Version-compatible; independently deployed service safe |
| Product configuration | Editorial home module order | Approved values and safe fallback |
| Commercial offer | Trial eligibility display | Only approved provider/market policy |
| Privacy-sensitive | Additional telemetry or notification channel | Off until market/consent review |
| Child-directed advertising | Advertising-policy-service eligibility | **Hard off** until DEC-004 approved |
| Emergency kill switch | Suspended media/unsafe content distribution | Must stop new grants regardless of stale client flag |

**FS-ME-007** A feature flag does not replace authorization. A child cannot enable Premium, content restrictions, a Parent Zone action or ads through modified client settings.

**FS-ME-008** If feature-flag infrastructure is unavailable, critical authorization and unapproved monetization functions fail closed; core approved safe browsing/playback should degrade according to explicit business policy.

**FS-ME-009** Every flag has an owner, creation reason, expected cleanup date, rollout environments, test matrix, monitoring and rollback/disable path. Expired temporary flags cannot accumulate indefinitely.

## 5. Safe rollout process

1. Product owner approves behavior and verifies DEC gates.
2. Engineering builds contract-compatible changes for independent services and Flutter.
3. QA tests enabled and disabled variants, including negative auth/profile/privacy cases.
4. DevOps configures observed, reversible rollout; no unreviewed country is silently enabled.
5. Monitor safety/security and availability guardrails before broader expansion.
6. If regression occurs, disable the feature and verify that existing user state remains consistent.
7. Record release decision and remove temporary flags when rollout stabilizes.

For a feature changing subscription, content publication or deletion semantics, rollback is more than switching UI: ensure backend authority and database/event state remain valid.

## 6. Experiments and user research

**FS-ME-010** Experiments in Child World must not make safety, comprehension, accessibility or consent optional. A/B testing cannot weaken Parent Zone proof, increase manipulative advertising, withhold necessary safety controls or collect additional child PII without review.

**FS-ME-011** Research with parents or children needs approved ethical/privacy process, clear consent, data minimization and age-appropriate methods. Do not silently record audio from child devices.

**FS-ME-012** Success should emphasize parent trust, qualified playback reliability, calm discovery, access to story catalog and content quality rather than excessive session duration or addictive engagement.

## 7. Failure and anti-abuse checks

| Fault | Required behavior |
|---|---|
| Analytics endpoint unavailable | Playback and account controls remain usable |
| Consent withdrawn | Optional collection stops under approved policy |
| Parent logs out | Old family telemetry context is cleared |
| Child switches profile | No cross-child identity collision |
| Ad flag accidentally on | Server legal/market allowlist still denies without approval |
| Stale Premium UI flag | Billing-service re-verifies entitlements |
| Schema field contains sensitive payload | Reject/redact; alert owner |
| Event replay | Dedup prevents inflated conversion/completion |
| Feature disabled mid-workflow | Persisted operations reconcile safely |
| Unsafe experiment variant | Emergency off, review and audit |

## 8. Acceptance scenarios

- **ME-AT-01:** Given an analytics provider is unreachable, when child starts an eligible story, then playback still succeeds.
- **ME-AT-02:** Given optional telemetry consent is denied, then nonessential collection stops as required by market policy.
- **ME-AT-03:** Given child profile A is replaced by B, then A-specific attributes are not emitted in B's events.
- **ME-AT-04:** Given a purchase screen emits a tap, then verified purchase conversion is not counted until billing-service confirms it.
- **ME-AT-05:** Given a duplicate completion event, then aggregate qualified completion remains deduplicated.
- **ME-AT-06:** Given advertising feature flag accidentally enabled with no approved DEC-004, then server still refuses eligibility.
- **ME-AT-07:** Given release flag provider outage, then Parent Zone authorization cannot fail open.
- **ME-AT-08:** Given an experiment reduces tap target accessibility, then it is blocked by design/QA review.
- **ME-AT-09:** Given a security incident requires a kill switch, then affected new grants stop, and the system shows a safe user state.

## 9. Handoff checklist

Every new metric/experiment requires Product+Privacy+Security approval, event schema, allowed attributes, consent/retention data map, backend owner, purpose, launch-market policy, opt-out handling, QA test and deletion behavior. Feature flags require default, activation gate, rollout/rollback and cleanup. No child-targeted ad tracking is enabled by default.
