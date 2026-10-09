# KidsAudioBookPlatform — Documentation Index

Version: 2.0.0  
Status: Active documentation foundation  
Branch: see the current repository branch (documentation is maintained on main)  
Last validated: 2026-10-10

## 1. Start here

KidsAudioBookPlatform is a parent-controlled audio-story platform for children initially ages 0–7. Product, safety, engineering, design, deployment and testing must remain mutually consistent. The canonical [Product Bible](00_Project/Product_Bible.md) takes precedence on product identity; implementation-level choices follow approved architecture and ADRs.

**Recommended reading order for a new contributor:**
1. [Product Bible](00_Project/Product_Bible.md) and [Project Charter](00_Project/Project_Charter.md).
2. [Product Requirements](01_Product/Product_Requirements_Document.md), [Functional Requirements](01_Product/Functional_Requirements.md), [Nonfunctional Requirements](01_Product/Non_Functional_Requirements.md).
3. [Software Architecture](03_Architecture/Software_Architecture.md), [Backend Architecture](03_Architecture/Backend_Architecture.md), [API Specification](03_Architecture/API_Specification.md).
4. [Coding Standards](04_Engineering/Coding_Standards.md), [Git Workflow](04_Engineering/Git_Workflow.md), [Definition of Done](04_Engineering/Definition_of_Done.md).
5. [Testing Strategy](06_Testing/Testing_Strategy.md) and [CI/CD](05_DevOps/CI_CD.md).

For **proposed launch policies** and decisions awaiting approval, consult the [Decision Register](00_Project/DECISION_REGISTER.md). The [Documentation Audit](00_Project/DOCUMENTATION_AUDIT.md) tracks baseline gaps and remediation work. Implementation packages are not yet a running production system.

## 2. Documentation map

| Area | Contents | Audience |
|---|---|---|
| [00_Project](00_Project/) | Charter, goals, vision, glossary, Product Bible, ADRs | Everyone |
| [01_Product](01_Product/) | PRD, requirements, stories, journeys, roadmap | Product/QA/engineering |
| [02_UX_UI](02_UX_UI/) | Design system, colors, typography, animation, illustration, mascot, UX | Design/mobile/content |
| [03_Architecture](03_Architecture/) | Software/backend/mobile/admin, API, data, security, events, flows, C4 | Architects/engineering |
| [04_Engineering](04_Engineering/) | Code/documentation standards, branching, review, DoR/DoD, AI usage | Developers/reviewers |
| [05_DevOps](05_DevOps/) | Infrastructure, Docker, Compose, CI/CD, deployment, monitoring, recovery | Platform/SRE |
| [06_Testing](06_Testing/) | Unit, integration, acceptance, performance and security | QA and engineering |

The [C4 Model](03_Architecture/C4_Model/README.md) is an architecture *view set*, not an independent competing source of business rules.

## 3. Authority and conflict resolution

1. Product behavior and child-safety intent: Product Bible + approved PRD/requirements.
2. Technical deployment and ownership: Architecture + accepted ADRs.
3. Interface semantics: API/Event Catalog and versioned machine-readable schemas.
4. Coding/testing process: Engineering/Testing standards.
5. Operational runbooks: DevOps, validated against deployed infrastructure.

If documents conflict, record the conflict in a tracking issue; do not silently choose an interpretation. Changes affecting security, pricing, children, data retention or architecture require named approval and linked review evidence.

## 4. Build-ready requirement checklist

A feature is ready for implementation only when its business purpose, FR/US IDs, acceptance criteria, role/ownership model, API/data/event changes, failure behavior, observability, rollout and tests are agreed. A feature is done when code, tests, migrations, security evidence, documentation, deployment procedure and product sign-off meet the relevant [Definition of Done](04_Engineering/Definition_of_Done.md).

## 5. Local engineering workflow

Read [Docker Compose](05_DevOps/Docker_Compose.md) for local dependency examples, [Docker](05_DevOps/Docker.md) for image guidance and [Integration Testing](06_Testing/Integration_Testing.md) for ephemeral test environments. These documents are blueprints; actual command paths and module names must follow the implemented repository.

## 6. Child safety and privacy baseline

Parent Zone is protected separately from Child World. The backend is authoritative for accounts, profile ownership, publication and paid access. A child-facing UI must not expose transactional controls or unrestricted messaging. Optional monetization or AI features require explicit product/legal/security review before introduction.

## 7. Change discipline

- Every important feature references its requirement IDs and acceptance tests.
- New architecture decisions use ADRs and update affected diagrams/contracts.
- Do not introduce duplicate policies in multiple files without a canonical cross-reference.
- Documentation PRs must check links, examples, scope and assumption labels.
- Architecture and implementation docs should move together when behavior changes.
- Record significant document changes in [Project Changelog](PROJECT_CHANGELOG.md).
- Product/app releases are documented separately in [Release Notes](RELEASE_NOTES.md).

## 8. Current scope and open decisions

The current design is a modular monolith with Spring Boot/Java 21, Flutter, PostgreSQL, Redis, RabbitMQ, object storage/CDN and background workers. Deployment specifics, final brand token values, billing offer/trial eligibility, country-specific legal requirements and operational RTO/RPO need explicit review and confirmation before launch. Proposed targets are not production certification.

## 9. Finding the right depth

Begin with product requirements and the primary software/API/data documents. Use C4 levels 1–4 to understand the system. The additional C4_Model files are specialized operational or governance references, not independent competing architectural decisions. Refer to the [ADR index](00_Project/ADR/README.md) for accepted choices and supersessions.

## 10. Onboarding acceptance

New contributors should be able to trace a user story to architecture, an endpoint/event, a persistence model, a test and a deployment gate without relying on tribal knowledge. When they cannot, the owner should improve the relevant canonical document rather than start an unlinked page.
