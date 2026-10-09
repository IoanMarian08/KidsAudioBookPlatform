# Blueprint 02 — Curated Catalog, Media and Editorial Workflow

Version: 1.0  
Status: Implementation blueprint / unimplemented  
Owners: Catalog, Media, Administration, Content Operations

## 1. Purpose

Publish safe, rights-cleared narrated stories and deliver age/locale-appropriate catalog views through a secured media pipeline. Authoring is privileged; children can only browse approved published content.

**Existing authority:** [Product Bible](../00_Project/Product_Bible.md), [API Spec](../03_Architecture/API_Specification.md) §§24–29 and admin §§46–48, [Database Design](../03_Architecture/Database_Design.md) §§9–10, [Event Catalog](../03_Architecture/Event_Catalog.md) §§9–10, [Security Architecture](../03_Architecture/Security_Architecture.md).

## 2. Bounded contexts

- **Catalog** owns story/series/episode metadata, age suitability, language variants, editorial versions, categories, collection visibility and publication lifecycle.
- **Media** owns upload authorization, assets and renditions, scan/transcode state, object storage references and authorized delivery.
- **Administration** owns role-based author/reviewer permissions, moderation decisions and auditable privileged actions.
- **Entitlements** answers access tier for premium content; Catalog must not duplicate billing state.
- **Profiles** defines age/locale and parental restrictions; Catalog queries via a stable public contract, not direct profile table reads.

## 3. Required API surfaces

**Consumer:** GET /stories, /stories/{storyId}, /stories/{storyId}/related, /series, /series/{seriesId}, /series/{seriesId}/episodes, /episodes/{episodeId}, /categories, /collections, /search, /child-profiles/{profileId}/home.

**Admin:** GET/POST /admin/stories; GET/PATCH /admin/stories/{storyId}; POST /admin/stories/{storyId}/submit-review, /approve, /reject, /schedule-publication, /publish, /unpublish, /archive; PUT /admin/stories/{storyId}/localizations/{locale}; POST /admin/media/uploads.

Do not add a second public upload API without changing the canonical API Specification.

## 4. Data ownership

- **catalog.series, catalog.stories, catalog.story_localizations, catalog.episodes**, category/collection relationships and **catalog.content_revisions**.
- **media.media_assets, media.media_variants, media.content_media_links, media.processing_jobs**.
- Audit trails and moderation under **admin** schema.
- Binary files in private object storage; PostgreSQL holds metadata, version, checksum, processing status and permission state only.

## 5. Publication state model

~~~mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> InReview: Submit review
  InReview --> Approved: Editorial approval
  InReview --> Draft: Request changes
  Approved --> Scheduled: Set publish date
  Approved --> Published: Publish
  Scheduled --> Published: Time reached + readiness check
  Published --> Suspended: Safety / rights takedown
  Published --> Archived: Retire
  Suspended --> Draft: Rework
  Draft --> Archived: Discard
~~~

Exact enum labels and transition guards must match Database Design and API Spec; this diagram is the **business workflow**, not a new enum contract. No transition to Published unless required locales/assets, rights metadata and safety review are valid.

## 6. Media upload pipeline

~~~mermaid
sequenceDiagram
  actor Editor
  participant AdminAPI
  participant Media
  participant Storage
  participant Worker
  participant Catalog
  Editor->>AdminAPI: POST /admin/media/uploads
  AdminAPI->>Media: Check role and media constraints
  Media-->>Editor: Short-lived scoped upload URL
  Editor->>Storage: Upload original bytes directly
  Storage-->>Media: Object event / upload confirmation
  Media->>Worker: Scan, checksum, transcode, generate variants
  Worker-->>Media: Asset status + rendition metadata
  Editor->>Catalog: Submit story for review
  Catalog->>Media: Verify safe asset readiness
  Catalog-->>Editor: Approved/published or validation error
~~~

Use idempotent jobs, exponential backoff and dead-letter handling. Never publish or hand out media URLs based solely on client-reported upload completion.

## 7. Domain events and cache invalidation

Use existing [Event Catalog](../03_Architecture/Event_Catalog.md) names, including StoryDraftCreated, StoryVersionSubmittedForReview, StoryVersionApproved, StoryPublished, StoryUnpublished, MediaUploaded, MediaScanCompleted, MediaProcessingCompleted and MediaProcessingFailed. Business mutation + outbox insert in one transaction; events idempotently invalidate catalog/search/CDN decisions.

**Takedown is a security operation**: future playback grants must refuse suspended stories even if stale cached catalog entries exist. Existing signed URLs expire by design; emergency CDN invalidation capability is an operational requirement.

## 8. Acceptance and resilience tests

| Test | Expected result |
|---|---|
| Unpublished or suspended story fetched via ID | Invisible or denied according to API policy |
| Story published with scan pending | Transition rejected |
| Non-editor attempts publication | Permission denied + audit signal |
| Wrong locale / blocked age | Results filtered server-side |
| Duplicate media event | One processing state transition |
| Upload malware or invalid MIME | Quarantine, no child access |
| Replay StoryPublished event | No duplicate search rows/notifications |
| Stale card cached after takedown | API playback authorization still denies |
| Audio/image rendition missing | Fallback/error but app remains navigable |

## 9. Acceptance checklist

- Story/series/episode lifecycle migrations and optimistic locking.
- Metadata, localization, category and stable publication identifiers.
- Role/approval separation, content rights documentation, malware scanning and integrity hash.
- Admin audit records with actor and transition reason.
- CDN/signed URL safety and caching/versioning policies.
- Catalog integration tests with real PostgreSQL and object storage-compatible test environment.
- Child-safe UX states for unpublished/missing assets.
- Editorial readiness measured: upload-to-approval time, processing DLQ, takedown latency.

**Product decisions still open:** language coverage, licensed asset inventory and ~50 free story launch target ([DEC-001](../00_Project/DECISION_REGISTER.md)).
