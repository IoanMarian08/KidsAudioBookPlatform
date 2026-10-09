# Contributing to KidsAudioBookPlatform

## Scope

This repository is currently primarily documentation and planning. Contributions must preserve child safety, server-side account and entitlement ownership, and the currently accepted architecture. New code must follow the engineering and quality documents once application modules are implemented.

## Before opening a pull request

1. Read the [Product Bible](docs/00_Project/Product_Bible.md), [PRD](docs/01_Product/Product_Requirements_Document.md) and [Decision Register](docs/00_Project/DECISION_REGISTER.md).
2. Identify relevant requirement IDs, bounded context, ownership/security implications and acceptance criteria.
3. Check the [ADR index](docs/00_Project/ADR/README.md); major decisions require an ADR.
4. Prefer a small cohesive PR. Do not generate broad, repetitive documents without adding a source of truth, example, contract or test.
5. Follow [Coding Standards](docs/04_Engineering/Coding_Standards.md), [Documentation Standards](docs/04_Engineering/Documentation_Standards.md) and [Code Review](docs/04_Engineering/Code_Review.md).

## Documentation rules

- Write in clear English. Use descriptive headings, concrete examples and short sections.
- State the owner, scope and status: **Accepted**, **Proposed**, **Pending validation**, **Illustrative**, or **Superseded**.
- Use repository-relative links; don't link to local machines, chat sessions or future files.
- Treat the [Product Bible](docs/00_Project/Product_Bible.md) as canonical for product intent, accepted ADRs for active technical decisions, and API/Event Catalog for interfaces.
- Record unresolved assumptions in the [Decision Register](docs/00_Project/DECISION_REGISTER.md); do not silently turn estimates into approved product policy.
- Maintain English terminology and stable ID references; avoid long duplicated summaries of documents that already exist.
- Add diagrams only when they explain boundaries or state transitions and update them when behavior changes.
- Never add real personal data, API secrets, store purchase tokens or private media keys.

## Pull request checklist

- [ ] The problem, scope and affected requirement IDs are clear.
- [ ] Child/parent access controls and privacy impact are considered.
- [ ] New decisions are captured and conflicting documents reconciled.
- [ ] Cross-references and local Markdown links work.
- [ ] Examples compile/run **or** are clearly marked as illustrative.
- [ ] Tests, migrations, contracts and observability are updated where relevant.
- [ ] Risky rollout or data changes explain recovery/rollback.
- [ ] Reviewers can understand and validate the change without private conversations.

## Pull request review and merging

Follow [Git Workflow](docs/04_Engineering/Git_Workflow.md) and [Branching Strategy](docs/04_Engineering/Branching_Strategy.md). Reviews should check behavior and safety before formatting. PR quality gates are defined in [CI/CD](docs/05_DevOps/CI_CD.md) and [Testing Strategy](docs/06_Testing/Testing_Strategy.md).

## Reporting issues

Use GitHub issues for reproducible non-sensitive bugs and documentation discrepancies. For security vulnerabilities or possible child-data disclosure, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.
