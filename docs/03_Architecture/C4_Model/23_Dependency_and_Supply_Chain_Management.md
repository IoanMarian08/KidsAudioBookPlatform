# Dependency and Supply Chain Management

Version: 1.0.0  
Status: Active Draft  
Owners: Architecture, Backend Engineering, Mobile Engineering, DevOps, Security  
Last reviewed: 2026-07-15

## 1. Purpose

This document defines how KidsAudioBookPlatform selects, approves, upgrades, verifies, and retires third-party dependencies, build tools, container images, plugins, SDKs, and external provider libraries.

The objective is to reduce supply-chain risk without blocking delivery. Every dependency must have a clear purpose, owner, upgrade path, licensing status, and security posture.

## 2. Scope

This policy applies to:

- Java and Maven dependencies;
- Flutter and Dart packages;
- frontend and admin-dashboard packages;
- base container images;
- GitHub Actions and reusable workflows;
- Gradle, Maven, Flutter, Node, and code-generation plugins;
- native iOS and Android SDKs;
- payment, notification, analytics, storage, and media-provider SDKs;
- operating-system packages installed in runtime or build images;
- generated code and downloaded binaries used during builds.

## 3. Principles

1. Prefer the smallest dependency set that solves the requirement.
2. Prefer mature, actively maintained, widely reviewed libraries.
3. Pin versions deterministically.
4. Never download mutable or unauthenticated binaries during production deployment.
5. Security and licensing checks are part of CI.
6. Critical dependencies require a documented replacement strategy.
7. Transitive dependencies are treated as real dependencies.
8. Every dependency must have an accountable owning team.
9. Upgrades are continuous work, not an occasional project.
10. Removing an unused dependency is preferred over carrying dormant risk.

## 4. Dependency classification

| Class | Description | Examples | Review level |
|---|---|---|---|
| Critical | Executes in security, payment, identity, storage, or deployment paths | Spring Security, JWT library, store SDK, base image | Architecture and Security |
| Core | Used broadly across application runtime | Spring Boot, PostgreSQL driver, Riverpod | Architecture owner |
| Feature | Supports a bounded feature | audio player, image processing, email adapter | Feature owner |
| Development | Used only for build, tests, linting, or local tooling | Testcontainers, Mockito, linters | Engineering owner |
| Experimental | Time-bounded evaluation dependency | prototype SDK | Explicit expiry and owner |

Experimental dependencies must not reach production without reclassification.

## 5. Approval criteria

Before introducing a dependency, the pull request must document:

- the problem being solved;
- why existing platform capabilities are insufficient;
- maintenance activity and release history;
- known security advisories;
- license and redistribution implications;
- transitive dependency impact;
- runtime, startup, binary-size, and memory impact where relevant;
- data or telemetry sent outside the platform;
- failure behavior;
- alternatives considered;
- owner and replacement approach.

Critical dependencies require explicit architecture approval.

## 6. Source and provenance rules

Approved sources are:

- Maven Central or an approved internal proxy;
- pub.dev through an approved dependency workflow;
- official Apple and Google package channels;
- approved container registries;
- source-controlled GitHub Actions pinned to immutable commit SHAs;
- vendor repositories approved by Security and DevOps.

Dependencies must not be fetched from personal repositories, shortened URLs, file-sharing services, or mutable release links.

Git dependencies are allowed only when a released package is unavailable and the commit SHA is pinned. They require an owner and removal plan.

## 7. Version pinning

- Maven dependencies use explicit versions through dependency management.
- Flutter and Dart lockfiles are committed.
- Node lockfiles are committed and immutable in CI.
- Container images are pinned by digest for release environments.
- GitHub Actions are pinned to full commit SHAs.
- Toolchain versions are declared in repository configuration.
- Floating tags such as `latest` are prohibited in production.

Automated update tooling may open pull requests, but updates are never merged solely because a newer version exists.

## 8. Software bill of materials

Every release candidate must generate an SBOM covering:

- application dependencies;
- transitive dependencies;
- container operating-system packages;
- native SDKs where tooling permits;
- dependency versions and package identifiers;
- license metadata;
- build and source revision.

The SBOM is retained with release artifacts and must be queryable during incident response.

## 9. Vulnerability management

CI scans dependencies and images against current vulnerability databases.

| Severity | Default response |
|---|---|
| Critical, exploitable | Block release and remediate immediately |
| High, exploitable | Block production promotion unless formally excepted |
| Medium | Schedule remediation within the normal maintenance window |
| Low | Track and address through routine upgrades |

A vulnerability exception must record:

- affected component and version;
- exploitability analysis;
- compensating controls;
- business justification;
- accountable owner;
- expiry date;
- remediation target.

Expired exceptions block release.

## 10. License compliance

Allowed licenses must be maintained in an approved policy. Dependencies with unknown, custom, restrictive, source-disclosure, or incompatible licenses require legal review.

CI should detect license drift and newly introduced packages. Generated mobile-store notices must remain synchronized with shipped dependencies.

## 11. Dependency boundaries

A dependency must be introduced at the narrowest appropriate layer.

Examples:

- provider SDKs remain behind infrastructure adapters;
- serialization libraries do not leak into domain models;
- database-specific types do not appear in public application contracts;
- mobile platform plugins are wrapped behind feature-owned interfaces;
- analytics SDKs never become required for a core user journey.

This rule allows replacement without widespread refactoring.

## 12. External SDK data controls

Before integrating an external SDK, document:

- data collected;
- destinations and subprocessors;
- consent requirements;
- child-data implications;
- retention behavior;
- runtime permissions;
- network endpoints;
- disablement and deletion behavior.

Advertising or analytics SDKs must not initialize in child-facing contexts unless explicitly approved by privacy and security review.

## 13. Upgrade strategy

Dependencies are upgraded continuously through small, reviewable changes.

- patch updates should be evaluated frequently;
- minor updates require compatibility tests;
- major updates require migration notes and rollback planning;
- framework upgrades must not remain unsupported beyond the approved window;
- end-of-life dependencies are tracked as technical debt with deadlines.

Critical upgrades require smoke tests for authentication, subscriptions, playback, offline behavior, notifications, and administration.

## 14. Removal strategy

A dependency must be removed when:

- the feature no longer uses it;
- maintenance is abandoned;
- licensing becomes unacceptable;
- security risk exceeds its value;
- a platform-native capability replaces it;
- two libraries duplicate the same responsibility.

Removal includes deleting configuration, credentials, permissions, transitive overrides, documentation, dashboards, and provider resources.

## 15. Build integrity

Release builds must be reproducible from source and approved artifact repositories.

Required controls:

- isolated CI runners;
- least-privilege build credentials;
- protected release workflows;
- signed or attestable release artifacts where supported;
- immutable artifact storage;
- checksums for downloaded tools;
- no production secrets available to pull-request builds;
- separation between build and deployment permissions.

## 16. Container image policy

Runtime images must:

- use minimal supported bases;
- run as non-root;
- omit compilers and package managers where unnecessary;
- contain only required certificates and locale data;
- be scanned before promotion;
- be rebuilt regularly even when application code is unchanged;
- include source revision and build metadata labels.

## 17. Dependency inventory

The repository must maintain or generate an inventory with:

| Field | Description |
|---|---|
| Package | Canonical name |
| Version | Resolved version |
| Classification | Critical, core, feature, development, experimental |
| Owner | Responsible team |
| License | Detected license |
| Source | Approved registry or vendor |
| Latest review | Last security and maintenance review |
| Replacement | Alternative or removal path for critical packages |

## 18. CI quality gates

Pull requests introducing or upgrading dependencies must pass:

- deterministic dependency resolution;
- vulnerability scan;
- license policy check;
- unit and integration tests;
- architecture boundary tests;
- container scan when images change;
- generated-lockfile consistency;
- unused-dependency checks where supported.

## 19. Observability

Track:

- number of outdated critical dependencies;
- vulnerabilities by severity and age;
- average remediation time;
- dependency exceptions approaching expiry;
- unsupported framework versions;
- failed dependency scans;
- container image age;
- percentage of actions and images pinned immutably.

## 20. Incident response

When a dependency compromise is suspected:

1. identify affected versions and releases using the SBOM;
2. disable or isolate affected integrations where possible;
3. rotate exposed credentials and signing material;
4. rebuild from trusted sources;
5. deploy patched or removed versions;
6. validate logs for exploitation indicators;
7. document customer, privacy, and regulatory impact;
8. create follow-up actions and update approval rules.

## 21. Exceptions

Exceptions require a written risk acceptance containing scope, compensating controls, owner, and expiry. Permanent undocumented exceptions are prohibited.

## 22. Definition of done

A dependency change is complete only when:

- ownership is assigned;
- version and source are pinned;
- security and license checks pass;
- tests cover the affected integration;
- operational and privacy implications are documented;
- rollback or replacement is understood;
- the SBOM and lockfiles are updated.
