# 11 — Administration, Story Editorial Workflow and Safe Content Operations

**Actors:** administrator, editor, reviewer, moderator, support operator; no child and no ordinary parent.
**Requirements:** PRD-08; FR-CA-004/005, FR-AD-001..003.
**Owners:** admin-service (RBAC/audit/support orchestration), catalog-service (publication/content metadata), media-service (private assets/workers), billing-service (subscription records).
**Contracts:** [API Specification](../../03_Architecture/API_Specification.md) sections 45–53, [Admin Dashboard](../../03_Architecture/Admin_Dashboard.md), [Catalog/Media blueprint](../../07_Blueprints/02_Catalog_Media.md).

## 1. Roles and least privilege

Staff access uses role/permission scopes. An editor may author material but not necessarily approve their own work; a reviewer may approve; a support operator may inspect necessary account status but not bypass billing truth or view child data without authorization; administrators can manage staff permissions under audit.

**FS-AM-001** Every admin request authenticates staff, checks permission/resource scope server-side and records high-risk actions with actor, target, timestamp, before/after or decision reason as appropriate.

**FS-AM-002** The administrative UI and its protected APIs remain inaccessible to parent/child roles; hiding menu tabs does not enforce permission.

**FS-AM-003** Editorial approval separation, support access breadth and sensitive override approval must have explicit role matrix and review before production. Avoid a blanket all-powerful shared credential.

## 2. Editorial entity authoring

Staff can create/edit stories, series, episodes, localizations, age metadata, classifications, collection associations and artwork/audio references. Each submitted story has an owner and version; drafts may be saved incomplete but cannot publish incomplete.

**FS-AM-004** GET/POST /admin/stories and GET/PATCH /admin/stories/{storyId} expose editable draft details to permitted staff. Concurrency must prevent an unseen edit from being overwritten without detection.

**FS-AM-005** Metadata validation covers title/description/locale, content rights, age suitability, status, duration, publication schedule, approved cover and matching audio rendition. Missing mandatory metadata rejects Submit/Publish with actionable editor-facing field errors.

**FS-AM-006** PUT /admin/stories/{storyId}/localizations/{locale} creates a versioned localized variant and cannot silently publish a mismatched audio/text language.

**FS-AM-007** Series/episode ordering and category/collection membership are stored as stable editorial decisions. Removing a category cannot accidentally publish an unreviewed item.

## 3. Media upload and processing

An editor requests a protected upload grant via POST /admin/media/uploads, uploads bytes directly to private object storage and confirms via POST /admin/media/uploads/{uploadId}/complete where the contract permits. GET /admin/media/assets/{assetId} shows asset state.

**FS-AM-008** Upload grant is short-lived, bound to editor role and approved MIME/size/intent. Completion is not proof of safety.

**FS-AM-009** Media remains private until integrity check, malware/security scan, rights/suitability review and required transcoding/manifest creation succeed. A processing failure must not create a public CDN grant.

**FS-AM-010** Duplicate storage events or processing retries are idempotent; asset state and job logs allow authorized staff to diagnose, reprocess or quarantine according to documented workflow.

**FS-AM-011** Editorial staff can preview only through authorized internal access, never through unrestricted public source-media URLs.

## 4. Review and publication state machine

Typical states: Draft -> In Review -> Approved -> Scheduled or Published -> Suspended/Unpublished -> Archived, with reviewed changes returning to Draft or In Review. Exact enum and transition conditions are authoritative in API/database documents.

**FS-AM-012** POST /admin/stories/{storyId}/submit-review validates completeness and marks review state. Approval may require a second authorized staff identity where separation of duties applies.

**FS-AM-013** POST /approve, /reject, /schedule-publication, /publish, /unpublish and /archive permit only valid role/status transitions. Rejection and suspension capture reason, and the audit trail cannot be overwritten silently.

**FS-AM-014** Scheduling uses a verified timezone and publication timestamp; a worker fires only if content remains approved, media ready, rights valid and publication window active. A stale scheduled event cannot republish a suspended story.

**FS-AM-015** Suspending/unpublishing must remove the story from new search/feeds and deny **new playback/media grants**, even when child devices have cached cards. Emergency takedown and signed URL invalidation must follow reviewed operational policy.

**FS-AM-016** Correcting a published story creates safe content revision, preserving stable story identity where appropriate and ensuring timing/audio/illustration consistency; older offline renditions follow content safety revocation policy.

## 5. Admin accounts, billing and support actions

The API specifies administrative account listing/details, suspension/restore/force logout, subscription listing/reconcile, entitlement overrides and campaign operations.

**FS-AM-017** Account suspension, restoration and force logout require permission and a meaningful audit reason. A suspended adult cannot retain private access through old refresh credentials.

**FS-AM-018** Billing overrides are exceptional, tightly scoped, time-bounded and auditable; they must not be a general workaround for failed Apple/Google verification. Approval policy and expiration are explicitly specified before enablement.

**FS-AM-019** Support staff see only minimum necessary account/ticket details, with access logs and no raw passwords, tokens, payment credentials or detailed child listening transcripts.

**FS-AM-020** Admin campaign creation/preview/schedule/cancel respects notification consent, localization, rate caps and child-specific marketing restrictions. Preview is not delivery; only approved channels can send.

**FS-AM-021** GET /admin/audit-events is restricted, filterable under access policy and protected from unauthorized modification or broad export.

## 6. Multi-service ownership

The admin dashboard can orchestrate operations via admin-service, but catalog-service owns published story state, media-service owns assets, billing-service owns entitlements and identity-service owns account credentials. No service may write another service's PostgreSQL logical database directly. REST/events are versioned, authorized, retry-safe and traceable.

**FS-AM-022** A remote timeout must not cause an admin screen to claim that a publication, suspension or refund finished when ownership service did not confirm it.

## 7. Acceptance matrix

| Case | Must prove |
|---|---|
| Editor attempts own prohibited approval | Denied; separation rules enforced |
| Missing scan/rights metadata | Publish rejected |
| Duplicate processing callback | One logical asset version |
| Unauthorized staff role | Protected endpoint denied |
| Scheduled story suspended before release | Remains unpublished |
| Published story taken down | New playback denied despite cache |
| Update concurrency conflict | No silent overwrite |
| Admin asks to change foreign DB data | Only owner's authenticated API controls mutation |
| Subscription override issued | Restricted permission, reason, TTL and audit |
| Push campaign preview | No unintended recipient delivery |
| Export attempted without scope | Denied/audited |

## 8. Given / When / Then

- **AM-AT-01:** Given a draft whose audio scan is pending, when Publish is requested, then it fails safely and no child can stream the asset.
- **AM-AT-02:** Given editor lacks reviewer permission, when Approve is invoked directly, then operation is denied and audited.
- **AM-AT-03:** Given two editors change one story revision, when the second saves against stale version, then an explicit conflict is returned.
- **AM-AT-04:** Given a scheduled approved story is suspended, when its scheduled time arrives, then it does not republish.
- **AM-AT-05:** Given story takedown, when a child uses a cached details card, then no new media grant succeeds.
- **AM-AT-06:** Given processing event redelivered, when media worker handles it, then no duplicate released rendition is created.
- **AM-AT-07:** Given a support account operator lacks billing override privilege, when creating an override, then it is denied and logged.
- **AM-AT-08:** Given a campaign in Preview, when confirmation is not provided, then no notification is dispatched.

**OPEN:** final staff role matrix, approval separation, editorial quality rubric, licensed launch inventory, campaign categories, audit retention and support workflow. Publication must satisfy child-safety review before shipping.
