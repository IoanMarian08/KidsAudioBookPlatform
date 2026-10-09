# Testing and verification

Version: 1.0  
Status: Documentation navigation

## Start here

Shows how to prove product behavior and safety across pure domain logic, real persistence/integrations, mobile journeys, performance, recovery and adversarial security scenarios.

**Recommended first document:** [Testing_Strategy.md](Testing_Strategy.md).

## Files

| Document | What it answers |
|---|---|
| [Testing_Strategy.md](Testing_Strategy.md) | Test pyramid, traceability and release coverage |
| [Unit_Testing.md](Unit_Testing.md) | Deterministic domain and widget tests |
| [Integration_Testing.md](Integration_Testing.md) | Testcontainers, DB, APIs, messages and billing |
| [Acceptance_Testing.md](Acceptance_Testing.md) | Critical Given/When/Then parent/child journeys |
| [Performance_Testing.md](Performance_Testing.md) | Latency, throughput, CDN and load profiles |
| [Security_Testing.md](Security_Testing.md) | Authorization, billing, upload and child-data threats |

## How to use this area

Every P0 user story needs positive and negative acceptance tests. Security, child privacy and entitlement correctness are release blockers irrespective of numerical coverage.

## Review rules

- Requirements, architecture and test evidence should remain linked, not duplicated.
- Proposed or sample configurations must be marked as such.
- Update the owner document, impacted contracts and references together.
- Record conflicting assumptions in the [Decision Register](../00_Project/DECISION_REGISTER.md).
