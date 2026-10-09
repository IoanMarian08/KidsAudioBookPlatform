# Engineering conventions

Version: 1.0  
Status: Documentation navigation

## Start here

Defines how humans and AI produce understandable, testable code and documentation. These are process standards, not evidence that an application is already implemented.

**Recommended first document:** [Coding_Standards.md](Coding_Standards.md).

## Files

| Document | What it answers |
|---|---|
| [Coding_Standards.md](Coding_Standards.md) | Java, Flutter, conventions and security rules |
| [Documentation_Standards.md](Documentation_Standards.md) | Document ownership, organization and review |
| [Git_Workflow.md](Git_Workflow.md) | Branches, commits and PR lifecycle |
| [Branching_Strategy.md](Branching_Strategy.md) | Branch naming and integration |
| [Code_Review.md](Code_Review.md) | Review expectations and quality gates |
| [Definition_of_Ready.md](Definition_of_Ready.md) | Criteria before implementation |
| [Definition_of_Done.md](Definition_of_Done.md) | Feature and release completion |
| [AI_Development_Guide.md](AI_Development_Guide.md) | Safe AI-assisted coding and verification |

## How to use this area

Before coding, verify that requirements and decisions are settled. After coding, provide contract, migration, test and security evidence. PRs follow the [Contribution Guide](../../CONTRIBUTING.md).

## Review rules

- Requirements, architecture and test evidence should remain linked, not duplicated.
- Proposed or sample configurations must be marked as such.
- Update the owner document, impacted contracts and references together.
- Record conflicting assumptions in the [Decision Register](../00_Project/DECISION_REGISTER.md).
