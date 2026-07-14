# Documentation Standards

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owners | Engineering and Architecture |
| Last Updated | 2026-07-15 |
| Scope | Product, architecture, engineering, API, testing, DevOps and operational documentation |

---

## 1. Purpose

This document defines how documentation is created, structured, reviewed, maintained and retired in KidsAudioBookPlatform.

Documentation is a first-class project artifact. Important behavior, decisions, contracts and operational knowledge must not exist only in source code, chat history or personal memory.

---

## 2. Documentation Principles

1. Write for a clearly identified audience.
2. Prefer explicit rules over assumptions.
3. Keep one authoritative source for each subject.
4. Update documentation in the same change as implementation.
5. Separate decisions, requirements and implementation guidance.
6. Use examples to clarify contracts, not to replace rules.
7. Mark status, ownership and version consistently.
8. Remove or archive obsolete guidance.
9. Avoid duplicating large sections across documents.
10. Treat generated documentation as reviewable source material.

---

## 3. Documentation Hierarchy

The project documentation is organized by purpose:

| Area | Purpose |
|---|---|
| `00_Project` | Vision, goals, product identity, project-wide completion criteria and ADRs |
| `01_Product` | Product requirements, functional behavior, user stories, flows and roadmap |
| `02_UX_UI` | Design system, visual language, interaction and accessibility guidance |
| `03_Architecture` | System structure, contracts, data, security, performance and architecture operations |
| `04_Engineering` | Coding, Git, review, readiness, completion and AI-assisted development rules |
| `05_DevOps` | Infrastructure, environments, CI/CD, deployment, monitoring and recovery |
| `06_Testing` | Test strategy and test-type-specific practices |

A document must be placed according to its primary audience and authority.

---

## 4. Authority Rules

When documents overlap, use this precedence:

1. accepted ADR;
2. active project foundation document;
3. architecture contract or specification;
4. engineering or operational standard;
5. implementation guide;
6. examples and historical notes.

A lower-level document must not contradict a higher-level source.

Conflicts must be resolved explicitly, not silently.

---

## 5. Required Metadata

Substantial Markdown documents should begin with:

```markdown
| Field | Value |
|---|---|
| Version | 1.0.0 |
| Status | Draft |
| Owners | Team or role |
| Last Updated | YYYY-MM-DD |
| Scope | Short scope statement |
```

Allowed statuses:

- `Draft` — incomplete or under active definition;
- `Review` — ready for stakeholder review;
- `Active` — approved current guidance;
- `Deprecated` — retained temporarily but should not guide new work;
- `Archived` — historical reference only.

Accepted ADRs use ADR-specific status values.

---

## 6. Versioning

Use semantic document versions:

- `MAJOR` for substantial restructuring, changed policy or incompatible guidance;
- `MINOR` for meaningful new sections or expanded scope;
- `PATCH` for corrections, wording improvements and non-material clarification.

Version changes are required for active foundation, architecture and engineering documents. Small generated references may rely on Git history when explicitly documented.

---

## 7. File Naming

Use descriptive English filenames with underscores where the repository already follows that convention.

Examples:

```text
Coding_Standards.md
API_Specification.md
Security_Architecture.md
```

Rules:

- avoid spaces;
- avoid vague names such as `Notes.md` or `Other.md`;
- preserve established naming conventions inside a folder;
- use numeric prefixes only where ordering is meaningful;
- rename carefully and update all references.

---

## 8. Document Structure

A substantial document should normally contain:

1. title and metadata;
2. purpose;
3. scope;
4. principles or context;
5. normative rules;
6. examples or workflows;
7. exceptions and failure behavior where relevant;
8. checklist or validation criteria;
9. related documents.

Not every document needs every section, but readers must be able to identify intent, authority and required action quickly.

---

## 9. Heading Rules

- Use one `#` heading for the document title.
- Use `##` for major sections.
- Use `###` for subsections.
- Avoid skipping levels.
- Keep headings descriptive and stable.
- Do not create headings solely for visual spacing.

A table of contents is useful for long documents but optional when navigation remains simple.

---

## 10. Writing Style

Documentation must be:

- direct;
- precise;
- professional;
- understandable by the intended audience;
- explicit about mandatory versus optional behavior.

Use:

- `must` for mandatory requirements;
- `should` for recommended behavior with valid exceptions;
- `may` for optional behavior.

Avoid ambiguous phrases such as:

- "as needed" without criteria;
- "properly" without defining expected behavior;
- "etc." where the omitted items affect implementation;
- "obvious" or "simple" for complex behavior.

---

## 11. Terminology

Use project terminology consistently.

Examples:

- `Parent Zone`, not alternating with unrelated names;
- `child profile`, not `child account` unless a distinct authenticated account is introduced;
- `story`, `series` and `episode` according to the domain model;
- `modular monolith` for the initial backend deployment model;
- `bounded context` or `module` according to the architectural meaning.

New important terms should be added to the project glossary or defined locally.

---

## 12. Links and References

Use relative repository links for internal documents where practical.

Rules:

- link to the authoritative document rather than duplicating content;
- verify paths after renames;
- use meaningful link text;
- avoid links to temporary local files;
- include external links only when they provide durable primary information;
- do not depend on inaccessible private chat links for project knowledge.

---

## 13. Code Examples

Code examples must:

- use fenced code blocks with a language identifier;
- compile or represent valid syntax where intended;
- exclude real secrets and personal data;
- be minimal enough to explain the rule;
- remain consistent with current project conventions;
- state when pseudocode is used.

Example:

```java
public interface StoryRepository {
    Optional<Story> findById(StoryId id);
}
```

Do not copy large production classes into documentation when a focused excerpt is sufficient.

---

## 14. Diagrams

Mermaid is preferred for diagrams stored in Markdown.

Diagrams must:

- have a clear purpose;
- use names consistent with current architecture;
- show relevant boundaries and direction;
- avoid decorative complexity;
- be updated when the described structure changes;
- include supporting text because diagrams alone are not sufficient contracts.

C4 diagrams must follow the maintenance guide in `../03_Architecture/C4_Model/10_Diagram_Maintenance_Guide.md`.

---

## 15. Tables

Use tables for concise comparisons, matrices and structured inventories.

Avoid tables when:

- cells contain long paragraphs;
- ordering or nested relationships matter more than comparison;
- the content is easier to scan as headings and lists.

Every table should have stable column meanings and consistent terminology.

---

## 16. API Documentation

API documentation must define:

- endpoint purpose;
- method and route;
- authentication and authorization;
- request and response schema;
- validation;
- error codes;
- idempotency;
- pagination and filtering;
- versioning;
- examples;
- compatibility and deprecation behavior.

OpenAPI is the canonical machine-readable contract. Markdown explains business context and behavior not fully captured by the schema.

---

## 17. Event Documentation

Every documented event must include:

- event name;
- producer;
- consumers or intended audience;
- trigger;
- schema version;
- envelope;
- payload fields;
- ordering assumptions;
- idempotency expectations;
- retry and dead-letter behavior;
- privacy classification;
- compatibility rules.

The Event Catalog is the authoritative event inventory.

---

## 18. Database Documentation

Database documentation must describe:

- ownership;
- entities and relationships;
- constraints;
- important indexes;
- lifecycle and status transitions;
- retention;
- migration strategy;
- backfill requirements;
- privacy and deletion behavior.

Do not document a production schema only through generated diagrams. Explain business meaning and invariants.

---

## 19. ADR Standards

An ADR must include:

- title and identifier;
- status;
- date;
- decision owners;
- context;
- decision;
- alternatives;
- consequences;
- implementation or validation notes where relevant.

An accepted ADR is immutable as a historical decision record except for corrections and explicit status updates. A changed decision should normally create a new ADR that supersedes the previous one.

---

## 20. Operational Documentation

Operational guides must include:

- purpose and owner;
- prerequisites;
- step-by-step procedure;
- verification steps;
- failure and rollback behavior;
- escalation path;
- safety warnings;
- last validation date.

A runbook that has never been exercised must not be treated as proven.

---

## 21. Security and Privacy in Documentation

Documentation must never contain:

- real passwords;
- access or refresh tokens;
- API keys;
- private keys;
- production connection strings;
- raw payment credentials;
- real child personal data;
- unredacted sensitive screenshots;
- internal secrets embedded in example commands.

Use placeholders such as:

```text
${DATABASE_URL}
<REDACTED_TOKEN>
example-child-profile-id
```

Security-sensitive architecture may be documented, but operational secrets must remain in approved secret-management systems.

---

## 22. Screenshots and Media

Screenshots must:

- exclude personal and secret data;
- show only relevant UI;
- include context in accompanying text;
- be updated when the interface materially changes;
- use synthetic accounts and content.

Prefer text and diagrams for rules that change frequently.

---

## 23. Review Requirements

Documentation changes must be reviewed for:

- correctness;
- consistency with authoritative sources;
- completeness;
- clarity;
- terminology;
- broken links;
- security and privacy exposure;
- operational usability.

Architecture, security and product policy changes require review by the relevant owner.

---

## 24. Documentation in Pull Requests

A pull request must update documentation when it changes:

- public or internal contracts;
- architecture;
- database schema or ownership;
- configuration;
- deployment behavior;
- security behavior;
- user-visible functionality;
- operational procedures;
- supported versions;
- known limitations.

Documentation updates should normally be included in the same pull request as the code change.

---

## 25. Maintenance and Review Cadence

Active documents should be reviewed:

- when related implementation changes;
- before major release milestones;
- after incidents exposing missing or incorrect guidance;
- when dependencies or supported platforms change;
- periodically according to ownership and risk.

The `Last Updated` field is not proof of correctness. Owners remain responsible for validation.

---

## 26. Deprecation and Archival

When a document becomes obsolete:

1. identify the authoritative replacement;
2. change status to `Deprecated`;
3. add a prominent replacement link;
4. update incoming references;
5. archive or remove only when historical value and Git history are sufficient.

Do not leave two active documents giving conflicting instructions.

---

## 27. AI-Generated Documentation

AI tools may help draft, summarize or restructure documentation.

The author must verify:

- every factual statement;
- filenames and links;
- architecture and product assumptions;
- code and command validity;
- absence of invented features or contracts;
- absence of secrets or personal data;
- consistency with current repository decisions.

AI output is never authoritative until reviewed and committed by a responsible contributor.

---

## 28. Documentation Completion Checklist

- [ ] Audience and purpose are clear.
- [ ] Metadata is present and accurate.
- [ ] Status and version are correct.
- [ ] Mandatory rules use precise language.
- [ ] Terminology is consistent.
- [ ] Examples are valid and safe.
- [ ] Links work.
- [ ] No secret or personal data is present.
- [ ] Related authoritative documents are referenced.
- [ ] Contradictory or obsolete guidance was removed.
- [ ] Relevant owner reviewed the change.
- [ ] The document is discoverable from an index or related guide.

---

## 29. Related Documents

- `Coding_Standards.md`
- `Git_Workflow.md`
- `Code_Review.md`
- `Definition_of_Ready.md`
- `Definition_of_Done.md`
- `AI_Development_Guide.md`
- `../00_Project/README.md`
- `../00_Project/ADR/README.md`
- `../03_Architecture/Architecture_Principles.md`
