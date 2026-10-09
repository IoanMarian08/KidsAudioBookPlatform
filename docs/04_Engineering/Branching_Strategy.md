# Branching Strategy

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owner | Engineering |
| Last Updated | 2026-07-15 |
| Scope | Repository branch lifecycle and protection |

---

## 1. Purpose

This document defines the branch model for KidsAudioBookPlatform. It explains which branches exist, how they are named, where they start, how they are validated, and when they are deleted.

The strategy favors a lightweight trunk-based workflow with short-lived branches. It avoids permanent environment branches and avoids Git Flow complexity unless the project later demonstrates a clear need for it.

---

## 2. Principles

1. `main` is the single long-lived integration branch.
2. `main` must always remain releasable.
3. Development happens on short-lived branches.
4. Every change reaches `main` through a pull request.
5. Branches represent one coherent purpose.
6. Long-running divergence is avoided.
7. Feature flags are preferred over long-lived feature branches.
8. Releases are identified by immutable tags, not permanent release branches.
9. Hotfixes use the smallest safe branch from the production baseline.
10. Branch protection and CI are mandatory quality controls.

---

## 3. Long-Lived Branches

### 3.1 `main`

`main` is the canonical source branch.

It must contain:

- reviewed code;
- passing CI;
- compatible migrations;
- current documentation;
- changes that satisfy Definition of Done.

Rules:

- direct pushes are prohibited;
- force pushes are prohibited;
- branch deletion is prohibited;
- pull requests require status checks;
- required review rules apply;
- stale approvals should be dismissed after material changes;
- unresolved review conversations block merge;
- the merge commit or squash title must be meaningful.

### 3.2 Environment Branches

Permanent branches such as `develop`, `staging`, `qa`, or `production` are not used by default.

Environments deploy immutable builds produced from commits or tags. Configuration differences belong in environment configuration, not in divergent source branches.

An environment branch may be introduced only through an ADR demonstrating why commit- or tag-based promotion is insufficient.

---

## 4. Short-Lived Branch Types

### 4.1 Feature Branch

Used for new product or technical capability.

Pattern:

```text
feature/<issue>-<short-description>
```

Example:

```text
feature/KABP-123-add-playback-progress
```

Base: latest `main` unless an approved dependency requires another branch.

### 4.2 Bugfix Branch

Used for non-production defect corrections.

Pattern:

```text
fix/<issue>-<short-description>
```

Example:

```text
fix/KABP-245-prevent-duplicate-favorites
```

### 4.3 Hotfix Branch

Used for urgent production corrections.

Pattern:

```text
hotfix/<issue>-<short-description>
```

Example:

```text
hotfix/KABP-901-revoke-invalid-entitlements
```

Base: the currently deployed production tag or corresponding commit.

The hotfix must also be incorporated into `main`.

### 4.4 Documentation Branch

Used when a change affects documentation only.

Pattern:

```text
docs/<issue-or-topic>-<short-description>
```

Example:

```text
docs/architecture-foundation
```

### 4.5 Refactoring Branch

Used for behavior-preserving structural improvements.

Pattern:

```text
refactor/<issue>-<short-description>
```

Example:

```text
refactor/KABP-310-isolate-entitlement-policy
```

### 4.6 Test Branch

Used for test-only improvements.

Pattern:

```text
test/<issue>-<short-description>
```

### 4.7 Chore or Maintenance Branch

Used for maintenance that does not fit another category.

Pattern:

```text
chore/<issue-or-topic>-<short-description>
```

Examples:

```text
chore/update-java-toolchain
chore/KABP-402-remove-unused-dependency
```

### 4.8 CI or Build Branch

Patterns:

```text
ci/<issue-or-topic>-<short-description>
build/<issue-or-topic>-<short-description>
```

Use these only when the primary purpose is pipeline or build-system change.

---

## 5. Naming Rules

Branch names must:

- use lowercase except for the issue key where the tracker convention uses uppercase;
- use hyphens between words;
- contain no spaces;
- remain concise but meaningful;
- avoid personal names;
- avoid vague terms such as `changes`, `update`, `work`, or `test2`;
- include an issue key when one exists.

Preferred format:

```text
<type>/<issue-or-topic>-<imperative-or-noun-description>
```

Good examples:

```text
feature/KABP-118-add-child-profile-limit
fix/KABP-221-handle-expired-download-manifest
docs/engineering-coding-standards
```

Bad examples:

```text
ioan-work
new-branch
fix-stuff
final-version
feature/many-things
```

---

## 6. Branch Lifecycle

### 6.1 Creation

Create a branch from the latest correct base:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/KABP-123-add-playback-progress
```

### 6.2 Active Development

Branches should remain short-lived and synchronized frequently.

Target expectations:

- most branches should live for hours or a few days;
- branches lasting more than one working week should be reviewed for splitting;
- branches lasting more than two weeks require an explicit reason and integration plan.

A long-lived branch increases:

- merge conflicts;
- integration risk;
- stale assumptions;
- review difficulty;
- hidden unfinished work.

### 6.3 Synchronization

Prefer rebasing a private work branch onto the latest `main`:

```bash
git fetch origin
git rebase origin/main
```

Do not rebase a shared branch without coordination.

Use:

```bash
git push --force-with-lease
```

after a private branch rebase. Plain force push is prohibited.

### 6.4 Pull Request

Open a pull request early when feedback is useful. Use draft status while the branch is not review-ready.

A branch is ready for full review when:

- the change is coherent;
- local validation passes;
- required documentation is updated;
- the pull request description is complete;
- known limitations are stated;
- no unrelated files are present.

### 6.5 Merge

Default merge method: squash merge.

Benefits:

- one coherent commit on `main` per pull request;
- simpler history;
- removal of temporary WIP commits;
- easier revert.

Rebase merge or merge commit may be used only when preserving individual commits or merge topology has clear value.

### 6.6 Deletion

Delete the branch after merge unless it serves an explicitly documented ongoing purpose.

Local cleanup:

```bash
git branch -d <branch-name>
```

Remote branches should be deleted automatically after merge where repository settings allow it.

---

## 7. Feature Flags and Incomplete Features

Incomplete functionality must not remain hidden in a long-lived branch when it can be safely integrated behind a feature flag.

Feature flags are appropriate when:

- the code can be deployed safely while disabled;
- incremental integration reduces risk;
- production validation or staged rollout is required;
- mobile and backend release timing differs.

A feature flag must have:

- an owner;
- a purpose;
- a default state;
- an expiry or removal condition;
- tests for enabled and disabled behavior;
- monitoring where relevant.

Feature flags must not conceal insecure or incomplete database migrations.

---

## 8. Dependent Branches

Stacked or dependent branches should be avoided when independent pull requests are possible.

When necessary:

- clearly document the dependency;
- base the second branch on the first;
- open pull requests in dependency order;
- retarget or rebase after the dependency merges;
- avoid unrelated work in the stack.

Example:

```text
feature/KABP-500-add-download-domain
feature/KABP-501-add-download-api
```

The second branch may temporarily depend on the first, but each pull request must remain understandable.

---

## 9. Release Tags

Releases are identified using annotated semantic-version tags:

```text
vMAJOR.MINOR.PATCH
```

Examples:

```text
v0.1.0
v1.0.0
v1.2.3
```

Example command:

```bash
git tag -a v1.0.0 -m "KidsAudioBookPlatform 1.0.0"
git push origin v1.0.0
```

Tags are immutable. If a release is faulty, create a corrected release with a new version rather than moving the existing tag.

Pre-release tags may use:

```text
v1.0.0-rc.1
v1.0.0-beta.2
```

---

## 10. Release Branches

Release branches are not part of the default workflow.

A temporary release branch may be used only when:

- a stabilization period is required while new development continues;
- multiple supported production versions require parallel maintenance;
- mobile-store approval creates a significant release freeze;
- the reason and lifecycle are documented.

Pattern:

```text
release/<version>
```

Example:

```text
release/1.0.0
```

Rules:

- keep the branch temporary;
- accept only release-critical fixes;
- merge accepted fixes back into `main`;
- tag the final release commit;
- delete the release branch after the support need ends.

---

## 11. Hotfix Process

A hotfix branch starts from the production tag or deployed commit.

Required steps:

1. identify and document the production impact;
2. create the hotfix branch;
3. implement the smallest safe correction;
4. add a regression test where practical;
5. run critical validation;
6. open an expedited pull request;
7. obtain required approval;
8. deploy from an immutable commit or tag;
9. merge or cherry-pick the correction into `main`;
10. document follow-up prevention work.

Emergency work must not bypass auditability, authorization, or secret-handling controls.

---

## 12. Branch Protection

Recommended `main` protections:

- require pull requests;
- require at least one approval;
- require CODEOWNERS review for sensitive paths;
- require passing CI checks;
- require conversation resolution;
- dismiss stale approvals when new commits materially change the diff;
- block force pushes;
- block deletion;
- restrict direct pushes;
- require signed commits if the project later adopts that policy;
- allow emergency bypass only for explicitly authorized maintainers with audit trail.

Sensitive paths include:

- authentication and authorization;
- subscription and entitlement logic;
- Parent Zone security;
- database migrations;
- CI/CD and infrastructure;
- security policy;
- production configuration;
- payment-provider integration.

---

## 13. Documentation Branch Exception

For large documentation foundations, a longer-lived documentation branch may be acceptable when:

- changes are isolated from runtime code;
- each document is committed separately;
- the branch is kept synchronized with `main`;
- the final pull request remains reviewable;
- document status and ownership are explicit.

The current `docs/architecture-foundation` branch follows this exception. It must still be merged and deleted once the documentation foundation is approved.

---

## 14. Prohibited Practices

- Direct commits to `main`.
- Permanent personal branches.
- Plain force pushes.
- Reusing one branch for unrelated tasks.
- Keeping merged branches indefinitely.
- Environment-specific source branches by default.
- Hiding months of work in an unreviewed branch.
- Creating release tags before required validation.
- Moving or deleting published release tags.
- Merging a hotfix only into production and forgetting `main`.
- Using a branch name that exposes secrets, customer data, or incident-sensitive details.

---

## 15. Decision Guide

Use this mapping:

| Change | Branch type |
|---|---|
| New user capability | `feature/` |
| Defect before production | `fix/` |
| Urgent production defect | `hotfix/` |
| Documentation only | `docs/` |
| Behavior-preserving restructure | `refactor/` |
| Tests only | `test/` |
| Pipeline change | `ci/` |
| Build/dependency packaging | `build/` |
| General maintenance | `chore/` |

---

## 16. Related Documents

- `Git_Workflow.md`
- `Code_Review.md`
- `Definition_of_Ready.md`
- `Definition_of_Done.md`
- `Coding_Standards.md`
- `../00_Project/ADR/ADR-0011-feature-flags.md`
- `../00_Project/ADR/ADR-0013-versioning-strategy.md`