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
