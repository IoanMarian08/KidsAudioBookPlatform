# Product specifications

Version: 1.0  
Status: Documentation navigation

## Start here

Defines what children and parents need, which behaviors are in scope, and how acceptance is measured. The [Product Bible](../00_Project/Product_Bible.md) remains canonical for product identity and the intended MVP. Priorities here describe delivery order; an explicit decision is required to remove a Product Bible commitment.

**Recommended reading:** [Product Bible](../00_Project/Product_Bible.md) (why/what) → [Complete Functional Specification](Functional_Specification/README.md) (how each user-visible feature behaves) → [PRD](Product_Requirements_Document.md), [Functional Requirements](Functional_Requirements.md), [User Stories](User_Stories.md) and [User Flows](User_Flows.md) (delivery/test traceability).

## Files

| Document | What it answers |
|---|---|
| [Functional_Specification/README.md](Functional_Specification/README.md) | **15 detailed linked chapters:** every screen, user action, valid state, error, offline rule, admin workflow and acceptance test |
| [Product_Requirements_Document.md](Product_Requirements_Document.md) | MVP scope, personas, acceptance and release gates |
| [Functional_Requirements.md](Functional_Requirements.md) | Stable feature IDs, permissions and observable behaviors |
| [Non_Functional_Requirements.md](Non_Functional_Requirements.md) | Reliability, performance, privacy, quality constraints |
| [User_Flows.md](User_Flows.md) | Step-by-step parent/child journeys and failure branches |
| [User_Stories.md](User_Stories.md) | Given/When/Then deliverable stories |
| [Roadmap.md](Roadmap.md) | Dependencies, stages and exit criteria |

## How to use this area

Start with a Product Bible concept, open the matching Functional Specification chapter and follow its FS rule IDs. Then find PRD/FR/US IDs and cross-check API/architecture, negative cases and QA evidence. Pricing, trial, ad activation and final MVP phasing require sign-off in the [Decision Register](../00_Project/DECISION_REGISTER.md).

## Review rules

- Requirements, architecture and test evidence should remain linked, not duplicated.
- Proposed or sample configurations must be marked as such.
- Update the owner document, impacted contracts and references together.
- Record conflicting assumptions in the [Decision Register](../00_Project/DECISION_REGISTER.md).
