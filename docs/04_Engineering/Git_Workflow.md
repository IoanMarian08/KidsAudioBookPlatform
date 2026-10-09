# Git Workflow

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owner | Engineering |
| Last Updated | 2026-07-15 |
| Scope | All repository contributors |

---

## 1. Purpose

This document defines the practical Git workflow used by KidsAudioBookPlatform from task selection to merge and release. It complements `Branching_Strategy.md`, which defines branch types and lifecycle rules.

The workflow is designed to provide:

- small and reviewable changes;
- traceability from requirement to code;
- stable protected branches;
- reliable CI validation;
- simple rollback and diagnosis;
- safe collaboration with human and AI contributors.

---

## 2. Core Rules

1. Never commit directly to `main`.
2. Start work from the latest intended base branch.
3. One branch should represent one coherent change.
4. Keep commits intentional and understandable.
5. Do not mix unrelated formatting, refactoring, and feature work.
6. Push frequently enough to avoid losing work, but never use remote branches as a substitute for local validation.
7. Every production change enters through a pull request.
8. CI must pass before merge.
9. Required reviews must be completed before merge.
10. Secrets, credentials, generated binaries, local environment files, and personal data must never be committed.

---

## 3. Standard Workflow

### Step 1 — Understand the Task

Before changing code:

- read the issue, requirement, or documentation;
- identify affected modules and contracts;
- confirm acceptance criteria;
- check related ADRs and architecture documents;
- identify security, migration, compatibility, and testing impact;
- split oversized tasks before implementation.

A task is not ready for implementation until it satisfies `Definition_of_Ready.md` or has an explicit exception.

### Step 2 — Synchronize the Base Branch

```bash
git switch main
git pull --ff-only origin main
```

For work based on another approved integration branch, replace `main` with that branch.

`--ff-only` prevents accidental local merge commits.

### Step 3 — Create the Work Branch

```bash
git switch -c feature/KABP-123-add-playback-progress
```

Use the naming rules in `Branching_Strategy.md`.

### Step 4 — Implement Incrementally

During implementation:

- make small logical changes;
- run relevant tests frequently;
- keep generated files and unrelated changes out of the branch;
- update documentation and contracts with the code that requires them;
- inspect `git diff` before staging.

Useful commands:

```bash
git status
git diff
git diff --staged
```

### Step 5 — Stage Intentionally

Prefer selective staging:

```bash
git add path/to/file
git add -p
```

Avoid blindly running `git add .` when the working tree contains unrelated or generated files.

### Step 6 — Commit

Commit messages use this format:

```text
<type>(<scope>): <imperative summary>
```

Examples:

```text
feat(listening): persist playback progress
fix(auth): revoke refresh token family on reuse
docs(engineering): complete git workflow
test(subscription): cover expired entitlement
refactor(catalog): isolate publication validation
```

Allowed common types:

- `feat`
- `fix`
- `docs`
- `test`
- `refactor`
- `perf`
- `build`
- `ci`
- `chore`
- `revert`

Rules:

- use imperative mood;
- keep the first line concise;
- describe what changed, not what you did;
- include issue references in the body or footer when available;
- explain non-obvious decisions in the body;
- never include secrets or personal data.

Example with body:

```text
feat(downloads): add resumable offline package transfer

Persist byte-range progress and verify checksum before marking the
package ready. Corrupted partial files are deleted before retry.

Refs: KABP-321
```

### Step 7 — Validate Locally

Before pushing, run the checks relevant to the change.

Backend examples:

```bash
mvn test
mvn verify
```

Flutter examples:

```bash
flutter analyze
flutter test
```

Admin-dashboard examples depend on the selected frontend toolchain but must include linting, tests, and a production build.

Also verify:

- formatting;
- generated contracts;
- database migrations;
- Docker or configuration changes;
- documentation links;
- no accidental sensitive files.

### Step 8 — Reconcile with the Base Branch

Before opening or finalizing the pull request:

```bash
git fetch origin
git rebase origin/main
```

Resolve conflicts carefully and rerun validation.

Do not rebase a shared branch without coordinating with collaborators.

### Step 9 — Push

First push:

```bash
git push -u origin feature/KABP-123-add-playback-progress
```

After a private branch rebase:

```bash
git push --force-with-lease
```

Never use plain `--force`. `--force-with-lease` protects against overwriting remote work you have not seen.

### Step 10 — Open a Pull Request

The pull request must include:

- problem and context;
- solution summary;
- affected modules;
- testing evidence;
- security and privacy impact;
- migration or deployment impact;
- screenshots or recordings for UI changes;
- related issue and documentation;
- known limitations or follow-up work.

Draft pull requests are encouraged for early collaboration, but they must be marked ready only after the author checklist is complete.

### Step 11 — Address Review Feedback

- Respond to every actionable comment.
- Make requested changes in focused commits.
- Explain when a suggestion is not applied.
- Do not resolve another reviewer’s thread unless the concern is addressed or agreement is explicit.
- Rerun tests after changes.
- Request re-review when substantial changes are made.

### Step 12 — Merge

The default merge method is squash merge unless repository policy or release needs require another method.

The final squash commit must have a meaningful Conventional Commit-style title.

A pull request may merge only when:

- required CI checks pass;
- required approvals are present;
- review conversations are resolved;
- the branch is current enough to merge safely;
- migrations and compatibility are reviewed;
- documentation is updated;
- the change satisfies the Definition of Done.

### Step 13 — Clean Up

After merge:

```bash
git switch main
git pull --ff-only origin main
git branch -d feature/KABP-123-add-playback-progress
```

Delete the remote branch unless it is intentionally retained.

---

## 4. Commit Design

A good commit:

- represents one logical unit;
- builds and tests where practical;
- can be reviewed independently;
- does not contain unrelated cleanup;
- has a message that explains intent.

Avoid:

```text
fix
updates
changes
wip
final final
misc
```

Temporary local WIP commits may be used during development but should be squashed or rewritten before review when they reduce clarity.

Do not rewrite commit history after review has started unless necessary and clearly communicated.

---

## 5. Pull Request Size

Prefer small pull requests.

A pull request should be split when it combines:

- unrelated modules;
- infrastructure and product behavior without necessity;
- broad formatting with functional changes;
- multiple independent migrations;
- several user stories;
- large generated changes that hide handwritten logic.

Large changes require:

- an implementation plan;
- clear commit structure;
- staged review when possible;
- explicit rollout and rollback notes.

---

## 6. Database Changes

Database changes must:

- include a Flyway migration;
- preserve backward compatibility during rolling deployment where required;
- use expand-and-contract for destructive changes;
- include migration tests;
- document backfill and rollback behavior;
- avoid editing an already-applied migration.

Schema changes and the application code that depends on them should be coordinated in the same pull request or an explicitly sequenced set of pull requests.

---

## 7. API and Event Contract Changes

When changing APIs or events:

- update OpenAPI or event schemas;
- document compatibility impact;
- add or update contract tests;
- preserve supported clients;
- follow deprecation rules;
- avoid changing the meaning of existing fields;
- include versioning when the change is breaking.

---

## 8. Documentation Changes

Documentation follows the same review and commit rules as source code.

For substantial documentation work:

- one document per commit is preferred;
- update version, status, owner, and date metadata;
- verify links and terminology;
- avoid duplicating authoritative content;
- link to the canonical document rather than copying large sections.

---

## 9. Hotfix Workflow

A production hotfix must:

1. start from the current production branch or tag;
2. contain the smallest safe correction;
3. include a regression test where practical;
4. pass accelerated but complete critical validation;
5. receive required approval;
6. include rollback instructions;
7. be merged back into the normal development line.

Example:

```bash
git switch main
git pull --ff-only origin main
git switch -c hotfix/KABP-901-fix-entitlement-revocation
```

Emergency status does not justify bypassing security, review, or audit requirements.

---

## 10. Revert Workflow

Use `git revert` for changes already shared or merged:

```bash
git revert <commit-sha>
```

Do not erase shared history to hide a faulty change.

A revert pull request must explain:

- the user or operational impact;
- the commit or PR being reverted;
- whether data correction is required;
- the follow-up plan.

---

## 11. AI-Assisted Changes

AI-assisted contributors must follow the same workflow.

Before commit:

- inspect every changed file;
- verify no files outside the requested scope changed;
- run relevant tests;
- confirm dependencies and APIs actually exist;
- remove speculative or unnecessary abstractions;
- validate security-sensitive behavior;
- document AI limitations when relevant.

AI tools must never be given or instructed to commit secrets, private keys, production data, or raw credentials.

---

## 12. Prohibited Actions

- Direct push to protected branches.
- Plain `git push --force` on shared branches.
- Committing `.env` files with real secrets.
- Bypassing required status checks.
- Editing shared history without coordination.
- Mixing unrelated changes in one pull request.
- Approving one’s own change when independent approval is required.
- Disabling tests or security checks merely to obtain a green build.
- Committing generated binaries or local IDE state unless explicitly required.
- Using merge conflict resolution without understanding both sides.

---

## 13. Author Checklist

Before requesting review:

- [ ] The branch has a clear purpose and correct name.
- [ ] The diff contains no unrelated files.
- [ ] Commits are understandable.
- [ ] Formatting and static analysis pass.
- [ ] Relevant tests pass.
- [ ] New behavior has tests.
- [ ] API, events, migrations, and documentation are updated.
- [ ] Security and privacy impact were reviewed.
- [ ] Logs contain no sensitive data.
- [ ] Rollout and rollback are documented where relevant.
- [ ] The pull request description is complete.
- [ ] The change satisfies Definition of Done.

---

## 14. Related Documents

- `Branching_Strategy.md`
- `Code_Review.md`
- `Coding_Standards.md`
- `Definition_of_Ready.md`
- `Definition_of_Done.md`
- `Documentation_Standards.md`
- `AI_Development_Guide.md`