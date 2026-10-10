# User Stories and Acceptance Criteria

Version: 2.0.0  
Status: Initial prioritized backlog  
Owner: Product

## 1. Story policy

Each story maps to an FR-ID and PRD objective. Stories are sized so they can be delivered and validated independently. Acceptance criteria use Given/When/Then, explicitly covering ownership, safety, network failure and idempotency where relevant. Priority P0 blocks MVP; P1 may ship later.

## 2. Parent and Identity

### US-001 (P0): Verified parent registration
As a parent, I want to create and verify an account so I can safely manage a child's experience.

- Given valid registration data, when I submit, then a limited verification flow begins without leaking existing-account status.
- Given an expired or reused token, when I verify, then access is denied.
- Given verification succeeds, when I sign in, then an authenticated session is issued with rotation/revocation support.
- Trace: FR-ID-001/002; test: account integration + security.

### US-002 (P0): Parent Zone protection
As a parent, I want billing and safety settings protected so my child cannot alter them.

- Given the child interface, when a parent-only deep link opens, then elevation is required.
- Given an expired elevated session, when saving controls, then the API rejects the write and prompts re-authentication.
- Given another account's profile ID, when editing, then the API rejects it without revealing its details.
- Trace: FR-PR-004, FR-ID-005.

### US-003 (P0): Multiple child profiles
As a parent, I want separate profiles so each child has an independent experience.

- Given two profiles, when switching, then progress/favorites/history reflect only the selected child.
- Given a deleted or foreign profile, when requesting its content, then access is denied.
- Trace: FR-PR-001/003.

## 3. Child discovery and playback

### US-004 (P0): Calm curated home
As a child, I want easy, understandable story choices so I can listen independently.

- Given a valid child profile, when opening home, then only approved stories for its locale/age are displayed.
- Given an empty catalog or offline network, when loading home, then a safe empty/cached state appears.
- Trace: FR-CA-001/002.

### US-005 (P0): Story playback
As a child, I want to listen and pause stories easily.

- Given an entitled published story, when I tap play, then audio streams via an authorized URL.
- Given a withdrawn story or expired entitlement, when requesting a new stream, then playback authorization is denied safely.
- Given app backgrounding, when resuming, then player state remains coherent.
- Trace: FR-PL-001/002.

### US-006 (P0): Continue listening
As a child, I want to resume where I left off.

- Given saved position, when returning to a story, then it resumes at accepted position.
- Given stale/offline updates, when syncing, then newer valid completion is not overwritten by an old event.
- Trace: FR-PL-003/004.

### US-007 (P1): Offline library
As a parent, I want authorized stories downloadable for travel.

- Given a download right, when download completes, then playback works offline within the grant validity window.
- Given insufficient storage or corrupt media, when downloading, then failure is visible and recoverable.
- Given a revoked grant, when authorization is checked, then the client obeys expiry/revocation policy.
- Trace: FR-PL-005.

### US-008 (P1): Synchronized illustrations and text
As a child, I want illustrations and optional text timed to narration.

- Given time cues, when seeking/pausing/speed changing, then visual state follows audio position.
- Given missing timing metadata, when opening a story, then audio-only playback remains available.
- Trace: FR-CA-007, FR-PL-007.

## 4. Premium and services

### US-009 (P0): Verified premium purchase
As a parent, I want to buy or restore premium access reliably.

- Given an App Store/Play purchase, when confirmation arrives, then the backend verifies it before granting rights.
- Given duplicate or out-of-order provider events, when consumed, then no duplicate subscription or extra grant appears.
- Given refund/expiry, when reconciled, then access reflects verified provider state.
- Trace: FR-SU-002/003/004.

### US-010 (P1): Parent notification preferences
As a parent, I want to manage reminders and transactional notifications.

- Given preference opt-out, when a marketing event occurs, then no marketing push is sent.
- Given a transactional message, when sent, then it avoids exposing personal child data in the preview.
- Trace: FR-NO-001/002.

## 5. Editorial and operations

### US-011 (P0): Safe story publication
As an editor, I want to review and publish audio stories with confidence.

- Given incomplete metadata, unscanned media or insufficient rights evidence, when publishing, then publication is blocked.
- Given a valid reviewed story, when publishing, then it appears in the eligible catalog and transition is audited.
- Given a safety takedown, when suspending, then search/cache and future media authorizations reflect suspension.
- Trace: FR-CA-004/005.

### US-012 (P0): Auditable admin operation
As a support administrator, I want each privileged action attributable and limited by role.

- Given insufficient role, when invoking a protected endpoint, then it returns a forbidden response.
- Given authorized update, when completed, then an audit record captures actor, action, entity and timestamp, excluding secrets.
- Trace: FR-AD-001/002.

## 6. Backlog expansion template

~~~text
Story ID:
Persona / goal / benefit:
FR/PRD links:
Priority:
Preconditions and data:
Happy-path Given / When / Then:
Authorization and privacy negative paths:
Offline/timeout/idempotency paths:
Metrics and audit events:
API, database, feature flag dependencies:
QA test IDs:
Done criteria:
~~~

## 7. Prioritization and dependencies

Critical delivery chain: US-001 -> US-003 -> US-004 -> US-005 -> US-006. Editorial upload/publication US-011 is required for live content; US-002 and US-009 gate monetization. Build P0 capabilities before P1 polish. Child safety, entitlement integrity and operational readiness are non-negotiable.

Related: [Functional Requirements](Functional_Requirements.md), [PRD](Product_Requirements_Document.md), [Definition of Ready](../04_Engineering/Definition_of_Ready.md).


## 8. Expanded behavior-driven backlog

The stories below expand the existing US-001..US-012. They reference the stable FS rule IDs; any example threshold is intentionally omitted when Product/Legal has not decided it. Story IDs are unique and should not be reused.

### US-013 (P0): Secure session rotation and revocation
As a parent I want account sessions to be secure and individually revocable so a lost device cannot continue using my account.

- Given a valid session, when its refresh token rotates, then the previous refresh token cannot issue a new session.
- Given I revoke a session, when that device requests a protected account/profile endpoint, then it is denied.
- Given a different parent account, when I try to view its sessions by ID, then I receive no private session details.
- Related: FS-ID-007..011; FR-ID-002; SCR-ID-08.

### US-014 (P0): Safe sibling switching
As a parent of two children I want each child to have completely separate listening state.

- Given profile A has a favorite and a partially listened story, when selecting B, then A's data is removed from B's view before B's own content loads.
- Given a cached foreign profile ID, when requesting its details, then backend rejects it.
- Related: FS-PR-003/007/008/016; FR-PR-003; SCR-PR-01.

### US-015 (P0): Content eligibility after changing parental settings
As a parent I want content restrictions to apply even to saved links.

- Given a story is eligible, when I block its category for profile A, then new playback for A is rejected.
- Given profile B remains eligible, when opening the same story under B, then B's own independent policy applies.
- Related: FS-PZ-008..011, FS-CA-001/016; FR-PR-005.

### US-016 (P0): Publisher refuses unsafe media
As an editorial reviewer I want scanning and rights to be mandatory before publication.

- Given an audio scan is pending or failed, when Publish is requested, then the story stays unavailable to children.
- Given an editor lacks approval permission, when invoking Approve directly, then the operation fails and an audit reason is recorded.
- Related: FS-AM-008..015, FS-CQ-001..010; FR-CA-004/005.

### US-017 (P0): Playback interrupted gracefully
As a young listener I want to return to a story without losing my place.

- Given a story is playing, when the phone receives an audio focus interruption, then the player pauses/ducks safely and the UI matches audible state.
- Given network fails then returns, when retrying, then the last authorized position is available without duplicate completion.
- Related: FS-PL-005..011/021; FR-PL-002/003.

### US-018 (P1): Synchronized images and narration
As a child beginning to read I want displayed text and pictures to follow the audio accurately.

- Given segments are published, when seeking between them, then the highlighted text and illustration match the new audio time.
- Given an optional image is missing, then narration stays usable with an approved fallback.
- Related: FS-PL-012..016; FR-PL-007.

### US-019 (P1): Verified offline library
As a parent I want eligible downloads to work on a trip without internet.

- Given Premium verified access and sufficient space, when requesting a download, then an authorized scoped grant is created.
- Given bytes are incomplete or corrupt, when transfer ends, then the item is not Ready.
- Given offline license expired, then behavior follows an approved rights policy instead of perpetual access.
- Related: FS-OF-010..015; FR-PL-005; DEC-013.

### US-020 (P0): Cross-device progress reconciliation
As a parent I want a child’s completed story to remain completed even when an offline device syncs stale data.

- Given device B completed a story online, when device A later sends an older partial position, then Completed is not replaced.
- Given the same offline operation is sent twice, then backend records one logical mutation.
- Related: FS-OF-016..020; FR-PL-004; DEC-014.

### US-021 (P0): Verified Premium purchase and restoration
As a parent I want to know whether the store verified my paid rights.

- Given a purchase callback but no server verification, then Premium remains Pending.
- Given a verified purchase, when restoring from a second approved device on the same account, then rights are restored without granting another account access.
- Given refund, when requesting new Premium media, then the grant is denied.
- Related: FS-SU-004..015; FR-SU-002..005.

### US-022 (P1): Parent controls notification preferences
As a parent I want to choose nonessential notification types.

- Given optional marketing is turned off, when its event is produced, then no optional marketing message is delivered.
- Given push delivery fails, then the in-app inbox can still record the event without blocking audio.
- Related: FS-NO-001..008; FR-NO-001..003.

### US-023 (P1): Adult requests account data deletion
As a parent I want a safe, understandable deletion process.

- Given I have no valid adult challenge, when requesting deletion, then it is rejected.
- Given a deletion job is still processing in one microservice, then the application never displays Completed.
- Given an offline device reconnects after completed deletion, then it does not restore deleted account data.
- Related: FS-PV-004..008; FR-ID-004; DEC-008/017.

### US-024 (P0): Content takedown wins over caching
As a content moderator I want a withdrawn story to stop being newly playable promptly.

- Given the story was previously visible, when it is suspended, then its search visibility and new media grants are denied.
- Given a delayed publish event arrives, then the current suspended state remains authoritative.
- Related: FS-CA-004/016, FS-AM-015, FS-CQ-005; PRD-08.

### US-025 (GATED): Noninterruptive optional ad
As a parent I want any advertising to respect my child's attention and data privacy.

- Given advertising has no legal/store approval, when a story completes, then no ad SDK or ad placement is activated.
- Given verified Premium, then post-session ad eligibility is denied.
- Given a repeated completion, then only one qualified session is counted.
- Related: FS-AD-001..010; PRD-13; DEC-004.

### US-026 (P0): Parent Zone cannot be bypassed
As a parent I want all sensitive settings protected even if someone opens a direct link.

- Given the adult session is authenticated but elevated proof has expired, when changing profile restrictions, then the service denies the update.
- Given repeated invalid PIN input, then server-enforced throttling/lockout follows approved policy.
- Related: FS-PZ-001..007; FR-PR-004.

### US-027 (P1): Calm accessible controls
As a child with limited reading or motor ability I want to find and play a story with recognizable, accessible controls.

- Given reduced motion enabled, then navigation/player remain fully functional without animated cues.
- Given screen reader enabled, then controls have meaningful labels and focus order.
- Given low connectivity, then offline and empty states are not confused.
- Related: FS-GL-001..014; PRD-14.

### US-028 (P1): Safe editorial localization
As an editor I want voice, text, illustrations and metadata to remain coherent across languages.

- Given localized narration is not ready, when attempting locale-specific publication, then the workflow refuses an inconsistent release.
- Given a published audio rendition is replaced, then synchronized text/illustrations must be reverified.
- Related: FS-CQ-004..010; FR-CA-007; DEC-007.

## 9. Story completeness template

Every story delivered to development includes:
- PRD + FR + FS cross references and affected SCR screen IDs;
- approved actor and eligibility rules;
- acceptance tests including foreign-account and invalid-input cases;
- exact API/contract and owning microservice;
- offline, concurrency, retry and content/entitlement transitions where applicable;
- localization, accessibility and privacy impacts;
- product decisions marked OPEN/GATED, not guessed;
- release flag and QA evidence.

Unapproved plan prices, profile limits, ad vendor and trial eligibility are not valid acceptance criteria until decided.
