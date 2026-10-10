# Project Documentation Changelog

Version: 2.0.0  
Status: Active  
Note: This log covers **documentation**; it does not imply an application release.

## 2026-10-10 — Full-documentation microservices consistency sweep

Following ADR-0015, reviewed all 138 Markdown documents for stale monolith-first wording and corrected residual statements in accepted ADRs, C4 policies, data ownership, integration contracts, Engineering and DevOps. Historical superseded decisions remain preserved for traceability. See [Documentation Audit](00_Project/DOCUMENTATION_AUDIT.md) for scope and limitations. This is documentation, not executable microservice code.

## 2026-10-10 — Owner-approved microservices-first architecture

The owner explicitly changed the implementation direction to **independently deployable microservices from the first release**, superseding the earlier modular-monolith choice in ADR-0001. New [ADR-0015](00_Project/ADR/ADR-0015-microservices-from-first-release.md) defines current service ownership, logical database separation, REST/RabbitMQ integration, data consistency, resiliency and delivery gates.

- Updated Software/Backend/Database architecture and C4 container/component/code/deployment views.
- Added [Microservices Architecture](03_Architecture/Microservices_Architecture.md) and [Microservices Contracts](03_Architecture/Microservices_Contracts_and_Flows.md).
- Replaced monolith-era roadmap/extraction guidance with independent-service build and future boundary migration.
- Updated project charter, goals, PRD, tech stack, infrastructure, CI/CD, deployment and blueprint references.
- This is a **documentation decision/change**, not a claim that code or infrastructure has been deployed.

## 2026-10-10 — Documentation clarity and coherence audit

The post-merge audit was conducted against main. Work is isolated on branch docs/documentation-audit-2026-10 pending review/merge.

- Added entry-point root README, substantive contributing/security guidance, Product/Legal decision register and auditable remediation list.
- Reconciled legacy three-digit ADRs with the active four-digit decisions, including superseding the obsolete microservices-first choice.
- Clarified that Product Bible commitments are not silently removed by P1 prioritization in the PRD.
- Added directory navigation pages for Product, UX/UI, Architecture, Engineering, DevOps and Testing; expanded the C4 supplemental reference index.
- Added docs/07_Blueprints for Identity, Catalog, Playback/Offline, Billing/Entitlements, Notifications, Privacy/Deletion and gated Advertising Policy.
- Corrected a real notification contract mismatch: Notifications.md now uses the API Specification's POST mark-read and DELETE dismiss, without assuming an uncontracted unread-count endpoint.
- Added Python standard-library Markdown link checker, GitHub Actions quality workflow and PR template.

**Validation status:** GitHub commits were created on the audit branch; programmatic link checks should pass in PR CI. External sites, fragment IDs, Mermaid diagrams and code examples require separate review. No production code delivery is implied.

## 2026-10-10 — Complete remaining documentation placeholders

The documentation foundation branch received detailed replacements for previously brief template files:

| Area | Documents | Git commit |
|---|---:|---|
| Product requirements, functional/NFR, stories, flows and roadmap | 6 | [b5ccdb4](https://github.com/IoanMarian08/KidsAudioBookPlatform/commit/b5ccdb4a10aa27996784f16d53f23f7f3a055ed8) |
| UX/UI, component design, typography, colors, illustration and mascot | 7 | [2230aac](https://github.com/IoanMarian08/KidsAudioBookPlatform/commit/2230aac46ca4f4f0dde9e25baf2735e3bd54f57a) |
| Infrastructure and DevOps runbooks | 7 | [94eea5f](https://github.com/IoanMarian08/KidsAudioBookPlatform/commit/94eea5f1c5edc197f39aa031b10600f53f61218b) |
| Testing strategy and five supporting test guides | 6 | [86f12be](https://github.com/IoanMarian08/KidsAudioBookPlatform/commit/86f12bee5e98d8bd710bed31f2c5a686e9eec6e2) |
| Docker Compose example interpolation correction | 1 correction | [add50b3](https://github.com/IoanMarian08/KidsAudioBookPlatform/commit/add50b3d7d31d74f5c9f1a63fe40c63fa51eed4c) |

### Outcomes

- Requirement IDs, priorities and behavior-driven acceptance criteria connect product intent to QA evidence.
- Child/parent authorization, account isolation and verified billing are consistently treated as release blockers.
- UX documents align with the Product Bible's rabbit mascot, watercolor illustration, calm palette and preferred typography.
- Runbooks describe environment isolation, CI gates, production deployments, metrics and restore.
- Test plans cover domain, persistence/messaging, end-to-end, security and performance.
- Explicit unresolved product, legal, design and infrastructure assumptions remain marked for human decision.

## Contribution rules

Add new entries for important architectural decisions, major specification changes or release process changes. Every entry includes date, scope, affected documents, link to PR/commit and known migration consequences. Avoid duplicate notes for trivial formatting changes.

## Historical context

Earlier work on the architecture-foundation branch established the Product Bible, high-level architecture, specialized architecture documents and the C4 view set. Consult Git history for the canonical sequence and authorship rather than relying on unverified summary claims.
