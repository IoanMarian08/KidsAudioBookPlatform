# Decision Register — Product, Delivery and Compliance

Version: 1.0  
Status: **Working register — unresolved entries are not approved specifications**  
Owner: Product + Architecture  
Review trigger: before MVP sprint planning, store submission, and any pricing/safety change

## Why this exists

Several documents correctly describe the **intended product**, while some engineering roadmaps label the same capability P1 or require legal approval before shipping. A developer must not infer from an implementation priority that the Product Bible has been superseded. This register separates decisions that are already canonical, decisions proposed for sequencing, and launch blockers requiring explicit approval.

**Source precedence:** [Product Bible](Product_Bible.md) → explicit approved change in Product docs → accepted [ADRs](ADR/README.md) for architecture → implementation examples. When sources disagree, stop and record a decision; do not use whichever file was edited last.

## Confirmed direction

| Topic | Current canonical direction | Evidence |
|---|---|---|
| Target audience | Children 0–7; parent is authenticated principal | [Product Bible](Product_Bible.md) |
| App/platform | Flutter for iOS and Android; protected Parent Zone | [Product Bible](Product_Bible.md), [ADR-0004](ADR/ADR-0004-flutter-mobile-platform.md) |
| Backend MVP | Java 21/Spring Boot **modular monolith with workers**, not service-per-context from day one | [ADR-0001](ADR/ADR-0001-modular-monolith-first.md) |
| Content | Curated audio, synchronized text, illustrations, bedtime/ambient features | [Product Bible](Product_Bible.md) |
| Monetization intent | Free and Premium; monthly/annual; proposed three-day trial; free-tier ad policy | [Product Bible](Product_Bible.md) |
| Safety | Parent-held billing and controls, no behavioral child ad targeting | [Security Architecture](../03_Architecture/Security_Architecture.md) |

## Launch decisions still requiring sign-off

| ID | Decision required | Why it matters | Current handling / owner |
|---|---|---|---|
| DEC-001 | Exact free catalog size and launch content rights (Bible suggests ~50) | Rights, editorial effort, store listing accuracy | Product + Content / **OPEN** |
| DEC-002 | Country/currency-specific monthly & annual price and tax presentation | Store compliance and entitlement UX | Product + Billing / **OPEN** |
| DEC-003 | Trial availability, eligibility, duration by storefront and anti-abuse policy | Bible suggests three days; availability cannot be assumed | Product + Billing + Legal / **OPEN** |
| DEC-004 | Advertising activation, vendor, age suitability, country restrictions and reward mechanisms | Child-directed ad law/store policy and safety risk | Product + Legal + Security / **GATED** |
| DEC-005 | Profile limits for free vs Premium and migration on downgrade | Entitlement decisions and data preservation | Product + Billing / **OPEN** |
| DEC-006 | MVP definition for offline downloads, synchronized text, illustrations, ambient sound and notifications | Product Bible includes them; PRD marks some P1 as delivery order | Product / **OPEN: align release gates** |
| DEC-007 | Supported countries, languages, consent flow and privacy notices | Legal requirements depend on launch markets | Product + Legal / **OPEN** |
| DEC-008 | Precise child age representation (age band vs birth date) and retention/deletion periods | Data minimization and parental consent | Product + Privacy / **OPEN** |
| DEC-009 | Production provider choices, hosting region, operational RTO/RPO and budgets | Actual deployment/runbook design | Architecture + DevOps / **OPEN** |
| DEC-010 | Final mascot name, font licenses and brand hex tokens | Currently proposed, not approved UI assets | Product + Design / **OPEN** |
| DEC-011 | Root repository licensing and private vulnerability-reporting contact | Contributors require safe rules | Owner / **OPEN** |
| DEC-012 | Supported mobile versions and backwards-compatibility window | Client rollouts are delayed in app stores | Mobile + Backend / **OPEN** |

## Required decision record

For each OPEN/GATED item, document: owner, options with trade-offs, explicit chosen behavior, target markets/platforms, date, acceptance criteria, dependent FR/PRD IDs, rollout defaults, privacy impact and linked approval PR. Mark **Accepted** only after human approval; then update the Product Bible (if product scope changed), relevant PRD/FR docs, API, data model, and tests.

## Safe implementation defaults while unresolved

1. **Do not activate child-directed advertising**, even if policy logic and feature flags are implemented.
2. **Never grant unverified purchases**; billing sandbox test is not a pricing or legal approval.
3. Prefer minimal age-band data over a birth date unless Product/Privacy require otherwise.
4. Leave trial pricing, profile quotas, supported countries and deletion periods **configurable**, not hard-coded based on assumptions.
5. Build tested P0 foundations now; treat the Bible's other MVP capabilities as committed *product intent* until DEC-006 resolves release sequencing.
6. Architecture examples are illustrative until built and tested; never describe them as deployed or certified.

## Decision workflow

~~~mermaid
flowchart TD
  A[Find unresolved assumption] --> B[Identify owner and options]
  B --> C[Evaluate child safety, privacy, cost, UX]
  C --> D{Approved?}
  D -->|No| E[Remain open or gated]
  D -->|Yes| F[Record explicit outcome and date]
  F --> G[Update canonical product/ADR/contract docs]
  G --> H[Add acceptance tests and release gate]
~~~

Related: [PRD](../01_Product/Product_Requirements_Document.md), [Roadmap](../01_Product/Roadmap.md), [Security Architecture](../03_Architecture/Security_Architecture.md).
