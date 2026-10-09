# Product Delivery Roadmap

Version: 2.0.0  
Status: Outcome-based roadmap (dates intentionally uncommitted)  
Owner: Product and Engineering

## 1. Planning rules

Roadmap stages are ordered by dependency and evidence, not arbitrary calendar dates. Each stage has an exit gate; a stage is not complete merely because tickets are merged. Scope changes require product impact assessment and revised acceptance evidence.

## 2. Stages

| Stage | Goal | Deliverables | Exit criteria |
|---|---|---|---|
| 0. Foundation | Safe, testable platform skeleton | CI, modules, schema, environment, secrets, metrics, threat model | Repeatable local build + staging deploy + baseline security controls |
| 1. Parent & profiles | Trustworthy account ownership | Registration, verification, Parent Zone, child profiles | Auth/IDOR tests pass, auditable controls |
| 2. Catalog & editorial | Publish high-quality safe content | Stories/series, moderation states, uploads, CDN | Reviewed story playable, takedown reliable |
| 3. Playback core | Deliver first-value experience | Flutter player, streaming, progress, child home | First-play/resume functional; measured playback SLI |
| 4. Commercial readiness | Enforce paid access correctly | Store verification, subscriptions, entitlements, restore | Refund/expiry/duplicate webhook tests pass |
| 5. MVP release | Operable public experience | Accessibility, observability, store submissions, legal reviews | P0 DoD/PRR and release gates satisfied |
| 6. Retention & offline | Improve travel/bedtime experience | Downloads, ambient sound, synced text, preferences | Offline grant and sync conflict scenarios pass |
| 7. Scale and localization | Broaden reach without safety regressions | More locales, editorial tooling, performance/cost | SLOs measured, incident/backup runbooks rehearsed |
| 8. Exploratory | Validate new ideas safely | Curated recommendations, optional AI-assisted internal tools | User research, privacy/security/ADR approval |

## 3. Dependency map

~~~mermaid
flowchart LR
    A[Platform foundation] --> B[Accounts and parent gates]
    B --> C[Child profiles]
    A --> D[Editorial and media pipeline]
    C --> E[Child catalog and home]
    D --> E
    E --> F[Playback and progress]
    B --> G[Verified entitlements]
    F --> H[MVP readiness]
    G --> H
    H --> I[Offline and ambient audio]
    H --> J[Localization and scale]
~~~

## 4. Priorities and feature gates

**P0**: child safety, ownership, curated content, streaming, progress, authentication, protected Parent Zone, entitlement correctness, security and production monitoring.

**P1**: safe downloads, synchronized text/illustrations, ambient audio, push preferences, search, accessibility improvements; any launch market can elevate P1 with explicit rationale.

**P2 / research**: algorithmic recommendations, author self-service, AI-generated content, social/community mechanics (currently out of scope). These require evidence and independent safety review.

## 5. Release readiness

A milestone may advance only if:
1. Acceptance scenarios for associated PRD/FR IDs pass.
2. Security/privacy/child-safety controls are demonstrated and reviewed.
3. API, migration, documentation and ADR changes are committed.
4. Observability, restore and incident runbooks support the deployed feature.
5. Performance tests meet targets against representative workloads.
6. Product owner accepts user experience and content editorial standards.
7. Store and legal constraints have been reviewed for that release scope.

## 6. Risk watchlist

| Risk | Early signal | Mitigation |
|---|---|---|
| Store billing uncertainty | Sandbox errors or inconsistent notifications | Reconciliation worker, signed provider proof and trials in sandbox |
| Content supply bottleneck | Catalog below launch threshold | Editorial pipeline and rights tracking first |
| Excessive engineering scope | Slow P0 throughput | Defer AI/microservices, favor modular monolith |
| Child safety violation | Unexpected route or asset exposure | Parent-gate and catalog authorization suites |
| Audio egress cost | CDN cost per play exceeds forecast | Bitrate policies, cache hit monitoring, capacity model |
| Poor offline synchronization | Frequent conflict/support incidents | Versioned progress events and device tests |

## 7. Success measurement

Track staged progression via verified feature completion, crash-free playback, time-to-first-play, editorial turnaround, purchase reconciliation correctness, incident volume and parent satisfaction. No stage uses child engagement as an incentive to override safe defaults.

## 8. Updating this roadmap

Maintain a quarterly product review (or earlier on major change). Each roadmap revision lists shipped, deferred, cancelled features and reason, with linked tickets and ADRs where applicable. Uncommitted ideas remain explicitly exploratory.

Related: [PRD](Product_Requirements_Document.md), [Product Bible](../00_Project/Product_Bible.md), [Implementation Roadmap](../03_Architecture/Implementation_Roadmap.md).
