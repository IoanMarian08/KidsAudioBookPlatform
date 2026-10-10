# Documentation Quality Audit — Microservices Platform

Version: 2.0
Status: Active quality register
Owner: Architecture and Engineering
Reviewed: 2026-10-10

## Current architecture

**KidsAudioBookPlatform is microservices-first.** From its initial implementation the backend consists of independently deployable Java 21/Spring Boot services: identity, profiles, catalog, media, playback, billing, notifications and admin. Advertising policy is separately feature-gated. Services own distinct logical PostgreSQL databases and credentials, independent Flyway migrations, REST/OpenAPI contracts and RabbitMQ outbox/inbox workflows.

The authoritative source is [ADR-0015](ADR/ADR-0015-microservices-from-first-release.md), supported by [Microservices Architecture](../03_Architecture/Microservices_Architecture.md) and [Service Contracts and Flows](../03_Architecture/Microservices_Contracts_and_Flows.md).

## Audit coverage

Documentation file tree, README navigation, ADR index, requirements and architecture, C4 levels and supplementary references, platform contracts, Engineering, DevOps, Testing and implementation blueprints have been reviewed for architecture consistency. A GitHub Actions workflow runs local Markdown path validation on pull requests.

**A file being present is not evidence that its code or infrastructure is running.** OpenAPI/event schema artifacts, concrete deployment files, Mermaid rendering, full external links, app-store providers and operational SLOs still require implementation or independent validation.

## Quality gates

| ID | Requirement | Status |
|---|---|---|
| DOC-001 | Root README provides clear onboarding and links to authoritative docs | Documented |
| DOC-002 | ADR-0015 is the sole architecture-style baseline and ADR index lists current decisions | Documented |
| DOC-003 | Each microservice has a named data and runtime owner | Documented |
| DOC-004 | API ownership and synchronous REST/RabbitMQ integration paths are explicit | Documented; executable contracts pending |
| DOC-005 | C4 container/component/deployment views show independent services and databases | Documented; diagram rendering review pending |
| DOC-006 | Product Bible / PRD scope and launch decisions are traceable | Open decisions tracked |
| DOC-007 | Service-level CI/testing, observability, recoverability and security standards defined | Documented; runtime verification pending |
| DOC-008 | Repository-relative Markdown links checked in CI | Automated |
| DOC-009 | Parent Zone, profile ownership, child-safety and paid access are enforced in domain contracts | Documented; integration/security tests pending |
| DOC-010 | Each service has deployable source, per-service Flyway migrations, probes and release pipeline | **Not yet implemented** |
| DOC-011 | Cloud/provider, region, RTO/RPO and service-to-service workload identity agreed | **Decision pending** |

## Remaining implementation work

1. Create actual service executables and individually deployable images in the repository.
2. Add machine-readable public/internal OpenAPI definitions and JSON/event schema versions.
3. Build gateway routes, service-to-service identity, deadlines, per-service databases/migrations, outbox/inbox and cross-service test suites.
4. Choose cloud, orchestrator, region, hosting and production secrets management.
5. Test per-service deployment/rollback, tracing, database privilege isolation and restore.
6. Resolve product/legal/privacy launch choices in the [Decision Register](DECISION_REGISTER.md).

## Contributor checklist

- [ ] Describe a feature using its requirement and user-story ID.
- [ ] Name the owning microservice and logical database.
- [ ] Specify peer REST/event contracts, authorization and failure behavior.
- [ ] Include positive/negative tests, migrations, observability and recovery.
- [ ] Update all affected C4, API, data, operational and product documentation.
- [ ] Verify local Markdown links and cross-service compatibility.

Active quality is measured by correctness, traceability and implementation evidence rather than document count.
