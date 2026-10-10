# System architecture

Version: 1.0  
Status: Documentation navigation

## Start here

Defines the technical system, runtime boundaries, data ownership and security. **Microservices are independently deployed from the first release** under [ADR-0015](../00_Project/ADR/ADR-0015-microservices-from-first-release.md). Start with the [Microservices Architecture](Microservices_Architecture.md) and [Service Contracts](Microservices_Contracts_and_Flows.md); C4 supplements provide views and governance, not alternate sources of truth.

**Recommended first document:** [Software_Architecture.md](Software_Architecture.md).

## Files

| Document | What it answers |
|---|---|
| [Software_Architecture.md](Software_Architecture.md) | Architecture overview and bounded contexts |
| [Microservices_Architecture.md](Microservices_Architecture.md) | Canonical deployable service inventory, database boundaries and infrastructure |
| [Microservices_Contracts_and_Flows.md](Microservices_Contracts_and_Flows.md) | API ownership, REST/event integration and distributed workflows |
| [Architecture_Principles.md](Architecture_Principles.md) | Mandatory architecture constraints |
| [Backend_Architecture.md](Backend_Architecture.md) | Java/Spring Boot modules and internal dependency rules |
| [Mobile_Architecture.md](Mobile_Architecture.md) | Flutter structure and offline architecture |
| [Admin_Dashboard.md](Admin_Dashboard.md) | Admin roles, workflows and interface |
| [API_Specification.md](API_Specification.md) | REST contracts and versioning |
| [Database_Design.md](Database_Design.md) | PostgreSQL schema and ownership |
| [Event_Catalog.md](Event_Catalog.md) | Asynchronous event contracts |
| [System_Flows.md](System_Flows.md) | Cross-system sequences and behavior |
| [Security_Architecture.md](Security_Architecture.md) | Child/parent/admin security and privacy |
| [Error_Catalog.md](Error_Catalog.md) | Error codes and failure behavior |
| [Technology_Stack.md](Technology_Stack.md) | Approved technologies |
| [Performance_Guidelines.md](Performance_Guidelines.md) | SLI/SLO and performance engineering |
| [Logging_Monitoring.md](Logging_Monitoring.md) | Observability architecture |
| [Notifications.md](Notifications.md) | Notification design |
| [Implementation_Roadmap.md](Implementation_Roadmap.md) | Implementation order |
| [C4_Model/README.md](C4_Model/README.md) | Structural diagrams and related governance |

## How to use this area

Feature owners first identify the bounded context, then API/event contract, data owner, threats, tests and rollout. Read [active ADRs](../00_Project/ADR/README.md) before creating new deployment components. Implement by following the [bounded-context blueprints](../07_Blueprints/README.md), which remain drafts until matched to working code.

## Review rules

- Requirements, architecture and test evidence should remain linked, not duplicated.
- Proposed or sample configurations must be marked as such.
- Update the owner document, impacted contracts and references together.
- Record conflicting assumptions in the [Decision Register](../00_Project/DECISION_REGISTER.md).
