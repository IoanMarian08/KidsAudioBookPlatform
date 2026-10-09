# AI Development Guide

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owners | Engineering and Architecture |
| Last Updated | 2026-07-15 |
| Scope | AI-assisted analysis, implementation, review, testing and documentation |

---

## 1. Purpose

This document defines how AI coding assistants, including Codex-style agents and conversational assistants, may be used safely and effectively in KidsAudioBookPlatform.

AI tools accelerate development, but they do not own requirements, architecture, security decisions or production accountability. Every generated change remains the responsibility of the human contributor who reviews and commits it.

---

## 2. Core Principles

1. Repository documentation and accepted ADRs are the source of truth.
2. AI must inspect before modifying.
3. Generated output must be reviewed line by line.
4. AI must not invent files, APIs, requirements or completed work.
5. Security and child privacy take priority over delivery speed.
6. Small, reviewable changes are preferred.
7. Tests and evidence are required for behavioral changes.
8. AI-generated code follows the same standards as human code.
9. Secrets and production data must never be provided to an AI tool.
10. The final human author accepts full responsibility for the result.

---

## 3. Allowed Uses

AI tools may assist with:

- repository orientation;
- requirement clarification;
- implementation planning;
- code generation;
- refactoring;
- test generation;
- documentation drafting;
- API and event contract review;
- migration planning;
- pull request summaries;
- static review suggestions;
- debugging from approved logs;
- identifying missing edge cases;
- generating safe synthetic test data.

AI assistance should reduce repetitive effort while preserving human control over important decisions.

---

## 4. Prohibited Uses

AI tools must not be used to:

- receive or process production secrets;
- receive real passwords, tokens, private keys or connection strings;
- receive unnecessary child personal data;
- make autonomous production deployments;
- approve their own code as the only reviewer;
- bypass security or quality gates;
- invent successful test results or commit SHAs;
- silently change architecture decisions;
- generate or introduce dependencies without review;
- copy unverified proprietary or incompatible code;
- make legal, privacy or compliance decisions without responsible review.

---

## 5. Repository Context Order

Before implementing a task, an AI agent should inspect relevant sources in this order:

1. task or issue;
2. `docs/00_Project/Product_Bible.md`;
3. `docs/00_Project/Project_Goals.md`;
4. accepted ADRs;
5. architecture documents;
6. product and UX requirements;
7. engineering standards;
8. testing and DevOps guidance;
9. existing implementation and tests.

The exact subset depends on the task, but an agent must not code from the prompt alone when repository contracts are available.

---

## 6. Mandatory Pre-Implementation Analysis

Before changing code, the agent must identify:

- requested outcome;
- affected module or bounded context;
- existing implementation;
- relevant contracts and documentation;
- security and privacy impact;
- database, API and event impact;
- compatibility requirements;
- expected tests;
- risks and unknowns.

The agent should state assumptions explicitly. Material uncertainty must not be hidden behind confident wording.

---

## 7. Task Scope Rules

AI changes must remain within the requested scope.

The agent must not:

- refactor unrelated code;
- rename broad areas without necessity;
- create duplicate abstractions;
- introduce new infrastructure for convenience;
- change public contracts silently;
- rewrite working modules only to match personal preferences;
- mix formatting-only changes with functional changes.

When adjacent issues are discovered, they should be reported or tracked separately unless they block the requested work.

---

## 8. Architecture Compliance

AI-generated changes must preserve:

- modular-monolith boundaries;
- domain ownership;
- dependency direction;
- server-side authority for security and entitlement decisions;
- PostgreSQL as the business system of record;
- Redis as non-authoritative cache or coordination state;
- reliable event publication;
- explicit API and event contracts;
- object storage ownership for binary media;
- Parent Zone and Child Experience separation.

An AI tool may propose an architecture change, but it must not implement one that conflicts with an accepted ADR without an approved replacement decision.

---

## 9. Backend Generation Rules

For Java and Spring Boot work, AI-generated code must:

- use Java 21 and approved Spring Boot conventions;
- keep domain code free of infrastructure dependencies;
- use explicit application use cases;
- avoid direct repository access across modules;
- validate authorization and ownership server-side;
- use typed domain concepts where valuable;
- define transaction boundaries deliberately;
- avoid generic exception swallowing;
- use the standard error catalog;
- preserve idempotency for retried commands;
- avoid leaking JPA entities through API contracts;
- include relevant tests.

The agent must inspect existing package and naming conventions before creating classes.

---

## 10. Flutter Generation Rules

For Flutter work, AI-generated code must:

- follow the approved feature-first structure;
- preserve presentation, application, domain and data responsibilities;
- use the selected state-management and navigation conventions;
- handle loading, empty, offline and failure states;
- keep sensitive values in platform-secure storage;
- avoid client-authoritative entitlement decisions;
- preserve Parent Zone route protection;
- support accessibility and child-safe interaction;
- dispose resources correctly;
- include widget or integration tests where appropriate.

The agent must not assume identical behavior across iOS and Android for platform APIs.

---

## 11. Admin Dashboard Generation Rules

AI-generated admin code must:

- treat backend authorization as authoritative;
- validate and sanitize input;
- avoid exposing sensitive account or child data;
- support pagination for large results;
- require confirmation for destructive actions;
- capture reasons for high-risk administrative operations;
- preserve auditability;
- handle partial failure in bulk operations;
- include relevant component and browser tests.

---

## 12. Database and Migration Rules

When generating database changes, the agent must:

- inspect current schema and ownership;
- create a new Flyway migration;
- never edit an applied versioned migration;
- consider rolling-deployment compatibility;
- avoid destructive one-step changes;
- define backfill behavior;
- evaluate locks and index creation impact;
- preserve data retention and deletion requirements;
- include migration tests or verification steps;
- explain forward-fix and recovery behavior.

Generated SQL must be reviewed for the actual PostgreSQL version and data volume assumptions.

---

## 13. API Generation Rules

For API changes, AI must verify:

- resource ownership;
- route naming;
- authentication and authorization;
- request validation;
- response and error schema;
- idempotency;
- pagination and filtering;
- versioning and compatibility;
- OpenAPI updates;
- contract tests;
- impact on supported mobile and admin clients.

The agent must not invent an endpoint without checking existing contracts and use cases.

---

## 14. Event Generation Rules

For asynchronous events, AI must:

- use past-tense fact names;
- identify producer and consumers;
- include the standard event envelope;
- minimize payload data;
- exclude secrets and unnecessary personal information;
- version schemas;
- preserve backward compatibility;
- use reliable publication where required;
- make consumers idempotent;
- define retry and dead-letter behavior;
- update the Event Catalog and tests.

Commands and events must not be confused.

---

## 15. Security Rules

AI-generated work must be reviewed for:

- broken access control;
- insecure direct object references;
- missing ownership validation;
- injection risks;
- unsafe deserialization;
- upload validation gaps;
- token or session weaknesses;
- secret exposure;
- excessive logging;
- insecure defaults;
- replay and idempotency issues;
- abuse of Parent Zone or admin operations.

AI tools may identify security issues, but findings must be verified and prioritized by a responsible engineer.

---

## 16. Privacy Rules

Never provide an AI tool with unnecessary real personal data.

Use:

- synthetic accounts;
- fictional child names;
- generated identifiers;
- redacted logs;
- sanitized payloads.

AI-generated analytics, logs and events must minimize child-related information and preserve retention and deletion requirements.

---

## 17. Dependency Rules

Before adding a dependency, the AI-assisted workflow must verify:

- the capability is not already available;
- maintenance activity;
- license compatibility;
- known vulnerabilities;
- supported runtime versions;
- transitive dependency impact;
- package size and mobile impact;
- operational implications;
- whether a simpler internal solution is appropriate.

An AI suggestion is not sufficient justification for a new dependency.

---

## 18. Testing Requirements

AI-generated behavioral changes must include tests appropriate to the risk:

- unit tests for domain behavior;
- integration tests for persistence and infrastructure;
- API or event contract tests;
- widget tests for UI components;
- mobile integration tests for critical journeys;
- regression tests for defects;
- migration tests for schema changes;
- security tests for sensitive paths.

The agent must not claim tests passed unless they were actually executed and results were observed.

---

## 19. Generated Test Quality

Generated tests must not merely mirror implementation details.

Tests should:

- express expected behavior;
- include failure and boundary cases;
- validate authorization and ownership;
- be deterministic;
- avoid excessive mocking;
- use realistic integrations where risk requires them;
- avoid production data;
- fail for the intended reason when behavior is broken.

---

## 20. Documentation Requirements

AI must update documentation when implementation changes:

- API contracts;
- event contracts;
- database schema or ownership;
- architecture;
- configuration;
- deployment behavior;
- security behavior;
- supported platforms;
- operational procedures;
- known limitations.

Generated documentation must be verified against the repository and must not include invented completion claims.

---

## 21. Prompt Construction

A useful engineering prompt should contain:

- objective;
- repository and branch;
- relevant files or modules;
- constraints;
- acceptance criteria;
- non-goals;
- required tests;
- output expectations;
- commit or change-scope rules.

Example:

```text
Implement playback progress update in the Listening module.
Preserve module boundaries and existing API behavior.
Use optimistic locking and idempotency for offline retries.
Add unit and PostgreSQL integration tests.
Do not modify unrelated modules.
Update OpenAPI only if the contract changes.
```

---

## 22. Agent Execution Workflow

The preferred workflow is:

1. inspect repository context;
2. summarize understanding;
3. identify assumptions and risks;
4. propose a focused plan;
5. modify the smallest necessary scope;
6. run formatting and static checks;
7. run relevant tests;
8. inspect the final diff;
9. update documentation;
10. report exact changes, test evidence and remaining risks.

For multiple documents or independent changes, use one commit per requested artifact when that rule is established for the task.

---

## 23. Tool and Commit Honesty

An AI agent must never claim that an action occurred unless the tool confirmed it.

This includes:

- file creation;
- file updates;
- test execution;
- build success;
- deployment;
- commit creation;
- push;
- pull request creation;
- review approval.

Commit SHAs, test results and URLs must be copied from actual tool output, never inferred or fabricated.

If an operation fails, the agent must state:

- what failed;
- whether any partial change occurred;
- what remains unchanged;
- the relevant error when safe to share.

---

## 24. Review of AI-Generated Code

The human reviewer must verify:

- requirements match implementation;
- no invented APIs or dependencies exist;
- architecture boundaries are preserved;
- error and failure behavior is safe;
- security and privacy requirements are met;
- tests are meaningful;
- documentation is accurate;
- the diff contains no unrelated change;
- generated code is understandable and maintainable.

The phrase "AI generated it" is never an acceptable explanation for unclear code.

---

## 25. AI-Assisted Code Review

AI review may be used to:

- summarize large diffs;
- detect missing tests;
- identify suspicious patterns;
- compare code with standards;
- surface potential compatibility issues;
- check documentation consistency.

It must not replace required human approval for security-sensitive, architecture-significant or production-critical changes.

---

## 26. Handling Uncertainty

When the AI lacks material information, it should:

- inspect additional repository context;
- state the uncertainty;
- use the safest reasonable assumption when progress is still possible;
- avoid destructive changes;
- preserve compatibility;
- record assumptions in the result.

The agent must not present guesses as established facts.

---

## 27. Refactoring Rules

AI-assisted refactoring must:

- preserve observable behavior unless explicitly requested otherwise;
- include regression tests;
- avoid broad rewrites without measurable benefit;
- maintain public contracts;
- preserve migration compatibility;
- keep commits reviewable;
- explain the reason and expected improvement;
- avoid mixing with unrelated feature work.

---

## 28. Incident and Debugging Use

When AI assists with incidents:

- provide redacted logs only;
- preserve timestamps, correlation IDs and error context;
- distinguish evidence from hypotheses;
- prioritize containment and data safety;
- avoid untested destructive commands;
- document commands before execution;
- validate recovery steps;
- create follow-up tests and documentation after stabilization.

---

## 29. Licensing and Attribution

Contributors must not ask AI tools to reproduce copyrighted source code from unrelated projects.

Generated output must be reviewed for:

- suspicious verbatim code;
- incompatible licenses;
- copied comments or attribution requirements;
- dependency licensing.

When provenance is uncertain, rewrite or replace the code.

---

## 30. AI Work Completion Checklist

Before accepting AI-assisted work, confirm:

- [ ] Relevant repository documents were inspected.
- [ ] Scope matches the requested task.
- [ ] Assumptions are explicit and valid.
- [ ] No unrelated files were changed.
- [ ] Architecture boundaries are respected.
- [ ] Security and privacy were reviewed.
- [ ] No secrets or real personal data were supplied.
- [ ] Dependencies and licenses were reviewed.
- [ ] Tests were added or updated appropriately.
- [ ] Tests claimed as passing were actually run.
- [ ] Documentation is accurate and current.
- [ ] The final diff was reviewed line by line.
- [ ] Tool actions and commit SHAs are reported honestly.
- [ ] A human accepts responsibility for the result.

---

## 31. Related Documents

- `Coding_Standards.md`
- `Git_Workflow.md`
- `Branching_Strategy.md`
- `Code_Review.md`
- `Definition_of_Ready.md`
- `Definition_of_Done.md`
- `Documentation_Standards.md`
- `../00_Project/Definition_of_Done.md`
- `../00_Project/ADR/README.md`
- `../03_Architecture/Architecture_Principles.md`
