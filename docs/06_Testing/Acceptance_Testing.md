# Acceptance Testing and User Journey Verification

Version: 2.0.0  
Status: Release-critical acceptance catalog  
Owner: QA / Product

## 1. Policy

Acceptance tests prove that a parent and child can safely accomplish product goals on realistic devices and staging backend. Every test references a PRD/FR/US ID, setup, data, expected result, environment and release milestone.

## 2. Core Given / When / Then scenarios

### AT-001: Parent registration
**Given** an unverified adult account, **when** verification succeeds within token TTL, **then** the account becomes eligible for authenticated Parent Zone access; reused/expired tokens are rejected.

### AT-002: Child profile separation
**Given** two sibling profiles, **when** switching between them, **then** favorites, listening progress and history remain strictly separated. Attempting another account's profile ID is rejected by the backend.

### AT-003: Child cannot access purchase controls
**Given** the child home, **when** a billing or settings deep link is opened, **then** Parent Zone elevation is required, including after app restart or expired session.

### AT-004: Published eligible content
**Given** a published story suitable for the active profile's age/locale, **when** browsing and tapping play, **then** signed media authorization succeeds and player starts without exposing storage credentials.

### AT-005: Suspended editorial content
**Given** a story moved to suspended state, **when** a child requests its details or a new playback grant, **then** it is hidden/denied according to API policy; old cached listings refresh safely.

### AT-006: Playback interruptions and progress
**Given** an in-progress story, **when** headphones disconnect, device locks or audio focus changes, **then** the player responds correctly and progress can resume.

### AT-007: Offline travel
**Given** a valid authorized offline download, **when** the device loses network access, **then** audio remains available inside grant policy; a non-downloaded story has a recoverable offline state.

### AT-008: Premium restore and refund
**Given** a parent who has bought a plan, **when** restoring purchases, **then** entitlement follows provider-verified data. Refund/revoke events remove unauthorized future grants, and duplicate events remain idempotent.

### AT-009: Editorial workflow
**Given** incomplete or unscanned media, **when** an editor requests publication, **then** publication is blocked and the cause is shown. A reviewed asset publishes with audit records.

### AT-010: Privacy and deletion
**Given** a parent-authenticated deletion request, **when** approved and processed, **then** credentials are revoked and affected data follows documented deletion/retention policy with audit evidence.

## 3. Device and state coverage

Matrix: representative low/mid-tier Android and iOS, phone/tablet layouts as supported, portrait/landscape, large text, reduced motion, screen reader, day/night themes, fast/slow/offline network, first-time/repeat parent, free/trial/premium/expired entitlement.

## 4. Test evidence requirements

Each execution records build SHA, device/OS, environment, synthetic user IDs, test data seed, screenshots/video only where useful, backend trace/correlation ID and defect link. Never store live tokens or unnecessary child information in QA attachments.

## 5. Exit criteria

- All P0 user journeys pass.
- No open critical child-safety, data-isolation or entitlement integrity defect.
- Accessibility and offline/error states validated.
- Product owner signs off intended behavior.
- Any accepted P1 defect has severity, mitigation, owner and due date.

Related: [User Stories](../01_Product/User_Stories.md), [User Flows](../01_Product/User_Flows.md), [Testing Strategy](Testing_Strategy.md).
