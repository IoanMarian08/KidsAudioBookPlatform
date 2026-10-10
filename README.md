# KidsAudioBookPlatform

> A calm, parent-controlled audio-story world for children aged 0–7.

**Repository status:** documentation-first foundation. The backend, Flutter app, admin dashboard and deployment manifests are not yet production applications; directories may contain placeholders. This README explains the intended architecture, not a shipped service.

## Start here

| Your goal | Read first |
|---|---|
| Understand product and audience | [Product Bible](docs/00_Project/Product_Bible.md) |
| Understand the complete app behavior | [Product Bible](docs/00_Project/Product_Bible.md), [Complete Functional Specification](docs/01_Product/Functional_Specification/README.md) and [PRD](docs/01_Product/Product_Requirements_Document.md) |
| Understand system shape | [Software Architecture](docs/03_Architecture/Software_Architecture.md) and [C4 views](docs/03_Architecture/C4_Model/README.md) |
| Implement backend APIs | [Backend Architecture](docs/03_Architecture/Backend_Architecture.md), [API Specification](docs/03_Architecture/API_Specification.md), [Coding Standards](docs/04_Engineering/Coding_Standards.md) |
| Implement Flutter | [Mobile Architecture](docs/03_Architecture/Mobile_Architecture.md) and [UX Design System](docs/02_UX_UI/UI_Design_System.md) |
| Work on security and children's privacy | [Security Architecture](docs/03_Architecture/Security_Architecture.md) |
| Deploy and operate | [DevOps](docs/05_DevOps/Infrastructure.md) and [CI/CD](docs/05_DevOps/CI_CD.md) |
| Validate features | [Testing Strategy](docs/06_Testing/Testing_Strategy.md) |
| Find unresolved questions | [Decision Register](docs/00_Project/DECISION_REGISTER.md) |
| See documentation findings | [Documentation Audit](docs/00_Project/DOCUMENTATION_AUDIT.md) |

**Full documentation navigation:** [docs/README.md](docs/README.md).

## Product in one minute

KidsAudioBookPlatform provides curated narrated stories, timed text and illustrations, child profiles, progress and continue-listening, bedtime ambience, offline listening and a protected Parent Zone. The parent owns the account and subscriptions. Children do not have unrestricted accounts, purchases or social interaction.

Safety boundaries are enforced **server-side**, never by merely hiding UI elements. Media uses private object storage and authorized CDN delivery; entitlements use verified store/provider records.

**Current architecture:** independent backend microservices with service-owned databases and REST/RabbitMQ contracts; read the [Microservices Architecture](docs/03_Architecture/Microservices_Architecture.md) before starting backend work.

## Intended technology baseline

| Surface | Current documented choice |
|---|---|
| Mobile | Flutter / Dart |
| Backend | Java 21, Spring Boot, independently deployed microservices and service-owned workers |
| Administrative web | React / TypeScript |
| Data | PostgreSQL; Redis for reconstructible cache/coordination |
| Messaging | RabbitMQ, transactional outbox, idempotent consumers |
| Media | Private object storage and CDN |
| Quality | JUnit, integration/contract/E2E testing, SAST/SCA and observability |

These are architecture decisions, **not evidence that this repository currently builds these applications**. Consult [accepted ADRs](docs/00_Project/ADR/README.md), especially [ADR-0015 microservices-first](docs/00_Project/ADR/ADR-0015-microservices-from-first-release.md). The former modular-monolith ADR is superseded.

## Getting involved

1. Read the [Product Bible](docs/00_Project/Product_Bible.md) and the [Decision Register](docs/00_Project/DECISION_REGISTER.md).
2. Choose a requirement ID in [Functional Requirements](docs/01_Product/Functional_Requirements.md), then inspect its exact behavior in [Complete Functional Specification](docs/01_Product/Functional_Specification/README.md).
3. Identify the owning bounded context, API/event contracts, threat model and acceptance tests.
4. Follow [Contribution Guidelines](CONTRIBUTING.md), [Definition of Ready](docs/04_Engineering/Definition_of_Ready.md), and [Definition of Done](docs/04_Engineering/Definition_of_Done.md).
5. Link changed docs, ADRs and test evidence in the pull request.

## Documentation quality

Documentation changes are reviewed like code. Relative links should resolve, examples must be labelled illustrative until verified, and no secret or sensitive child data may appear in examples. The documentation quality workflow checks local links on pull requests. See [Documentation Standards](docs/04_Engineering/Documentation_Standards.md).

## Safety and security

The project is child-directed. Follow [SECURITY.md](SECURITY.md) for responsible disclosure, never commit secrets or real child personal data, and do not enable child-targeted monetization without explicit product, privacy and platform-policy approval.

## License

A definitive licensing policy must be selected by the repository owner. Do not infer permission to redistribute this project from the presence of an incomplete [LICENSE](LICENSE) file.
