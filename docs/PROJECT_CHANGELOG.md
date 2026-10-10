# Project Documentation Changelog

Version: 3.0
Status: Active
Note: This is a documentation change log, not an application release announcement.

## 2026-10-10 — Complete product functional specification

- Expanded [Product Bible](00_Project/Product_Bible.md) with end-to-end product promises, functional cross-references, common recovery behavior and launch policy gates.
- Added [Complete Functional Specification](01_Product/Functional_Specification/README.md) with 15 linked chapters for adult onboarding, child profiles, catalog/search, synchronized player, progress/offline, Parent Zone, verified billing, gated ads, notifications/privacy, admin/editorial and QA acceptance.
- Added a [Screen Inventory](01_Product/Functional_Specification/13_Screen_Inventory_and_UX_Handoff.md), [State Matrices](01_Product/Functional_Specification/14_State_Matrices_and_Behavioral_Edge_Cases.md) and [Content Quality](01_Product/Functional_Specification/15_Content_Quality_and_Editorial_Acceptance.md).
- Extended PRD, Functional Requirements, User Stories and User Flows with FS-ID traceability and additional negative and interrupted journeys.
- Registered open decisions for offline licensing, playback completion, parent timers, notifications, export/support and editorial approval; did not assert legal or pricing approval.
- This work is a **detailed product specification**, not app/backend implementation or production release.

## 2026-10-10 — Microservices-first documentation baseline

- Confirmed [ADR-0015](00_Project/ADR/ADR-0015-microservices-from-first-release.md) as the architecture baseline.
- Defined independently deployable Spring Boot services with isolated logical PostgreSQL databases, service-owned migrations, authenticated REST contracts and versioned RabbitMQ events.
- Updated Software/Backend/Database Architecture and C4 context, container, component, code, security and deployment views.
- Added [Microservices Architecture](03_Architecture/Microservices_Architecture.md) and [Service Contracts and Flows](03_Architecture/Microservices_Contracts_and_Flows.md).
- Aligned PRD, Charter, project goals, roadmap, implementation blueprints, DevOps, Engineering and Testing.
- Streamlined architecture decision navigation to display the microservices design, ownership rules and current contracts.
- Added service-specific resilience, outbox/inbox, role isolation, deployment and disaster-recovery requirements.
- Automated local Markdown link checks via GitHub Actions.

## 2026-10-10 — Documentation structure and blueprints

- Added navigable root README, contributing and security guidance, document owner/review conventions and folder indexes.
- Added [Decision Register](00_Project/DECISION_REGISTER.md) for product, privacy, billing, operational and release choices requiring explicit approval.
- Added [Documentation Quality Audit](00_Project/DOCUMENTATION_AUDIT.md) with validation scope and remaining implementation gates.
- Added [seven implementation blueprints](07_Blueprints/README.md) covering Identity, Catalog, Playback, Billing, Notifications, Privacy/Deletion and approved-only Advertising Policy.
- Aligned Notifications API paths with [API Specification](03_Architecture/API_Specification.md).
- Documented DevOps/Testing standards, recovery, CI/CD, design system and operational checks.

## Validation boundaries

Documentation decisions do **not** imply implemented microservices or deployed infrastructure. Production readiness requires executable API/event contracts, code, per-service integration tests, security verification, deployment manifests, backup restore evidence and product/legal decisions.

The repository Git history records individual contributions and commit details. This index intentionally presents only the current microservices-based documentation baseline.
