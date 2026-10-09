# Documentation Audit — Baseline Findings

Version: 1.0  
Status: Audit findings and remediation tracking  
Source revision: main at c3d699723f1f76d0d7ad5348f648185cd86346a4  
Scope: all 119 Markdown documents + repository file tree at baseline

## Method

The audit enumerated the repository's Git tree, reviewed the Markdown files for local relative-link targets and inspected architecture, product, ADR, DevOps and testing documents for actionable contradictions and usability issues. External URLs and Mermaid rendering were **not** independently validated; code examples have **not** been compiled against an implemented application.

**Do not equate a present Markdown document with an implemented feature.**

## Confirmed findings

| ID | Severity | Finding | Remediation |
|---|---|---|---|
| AUD-001 | High | Root README contained only a title, obscuring the substantial documentation | Replace with audience-oriented entry point and onboarding sequence |
| AUD-002 | High | Legacy ADR-002 accepted immediate Spring Boot microservices, conflicting with accepted ADR-0001 modular-monolith-first | Label legacy decision superseded and explain current authority |
| AUD-003 | Medium | Four other legacy short ADRs overlap current four-digit ADRs or modern docs | Add legacy decision crosswalk without deleting decision history |
| AUD-004 | High | Product Bible's expected MVP contains ads, trial, offline and synchronized media; staged PRD marks some P1/gated, without explicit scope reconciliation | Introduce signed-off decision register and clarify sequencing versus product promise |
| AUD-005 | Medium | docs/README names a no-longer-existing branch while docs now reside on main | Make entry point branch-neutral and link current authority |
| AUD-006 | Medium | Root CONTRIBUTING and SECURITY files consisted of headings only | Supply actionable contribution and private disclosure policies |
| AUD-007 | Medium | Operational examples and quality standards exist, but application directories are currently scaffolds | Clearly label examples as blueprints and add implementable module plans/contracts before claiming readiness |
| AUD-008 | Medium | Diagram collection contains many supplemental governance documents; the C4 index covers only a subset | Add task-based navigation to distinguish core diagrams from supplemental policies |
| AUD-009 | Low | Repository includes empty historical document-de-proba scaffolding and skeletal LICENSE | Defer removal/license change to owner; document maturity honestly |
| AUD-010 | Medium | Docs have no tested automated local-link quality gate in source tree | Add lightweight checker and PR CI workflow |

## Link review caveats

A path-based Markdown scan found no confirmed missing **file targets** in existing Markdown. Seven directory references in docs/README are valid folder navigation, not broken file paths. In-document anchor fragments and external links require a separate validation pass. The automated checker should understand directory/README targets and provide reproducible CI output.

## Priority remediation plan

### P0 — Documentation trust
- [ ] Improve root README, contribution policy and security reporting.
- [ ] Reconcile legacy ADR statuses (do not erase history).
- [ ] Register Product Bible/PRD release scope decisions.
- [ ] Add link/heading checks to CI and fix any actual diagnostics.

### P1 — Implementation precision
- [ ] Prepare bounded-context blueprints: Identity/Parent Zone, Catalog/Media, Playback/Progress/Offline, Subscriptions/Entitlements.
- [ ] Add OpenAPI JSON/YAML examples that match API Specification, versioned event payloads and error semantics.
- [ ] Add field-level privacy mapping and entitlement/download state tables.
- [ ] Bind important FR/US requirements to architecture, test plans and owners.

### P2 — Usability and governance
- [ ] Add clear architecture reference map and label supplemental C4 governance.
- [ ] Capture environment setup commands **after** code modules are added.
- [ ] Review repeated policy text to remove inconsistent copies, not to maximize page count.
- [ ] Define review cadence and documentation owner for every active area.

## Acceptance criteria for completed documentation

- A new contributor knows what to build, where to start, and what is not yet implemented.
- No pair of current accepted decisions conflicts without an explicit superseding link.
- Important requirements trace to exact permissions, contracts, data owner, errors, tests and operations.
- All relative links pass CI; external docs and Mermaid are reviewed manually until an automatic checker is introduced.
- Unapproved child safety, billing and privacy assumptions are marked as gated and do not ship by accident.

This audit records verified baseline findings and planned changes, not a claim that every diagram and contract is fully validated.
