# ADR-0004: Use Flutter for the Mobile Applications

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Product, Architecture, Mobile Engineering

## Context

KidsAudioBookPlatform must support iOS and Android with a highly visual child experience, audio playback, offline downloads, local persistence, push notifications, animations, parental controls, subscriptions, biometrics, media controls, and app-store distribution.

The product should minimize duplicated feature logic, visual implementation, testing, and release coordination while retaining access to native platform capabilities where required.

The mobile application also has security-sensitive requirements. Subscription enforcement, profile ownership, parental controls, offline entitlements, and account operations cannot be trusted solely to client-side code.

## Decision

Use Flutter and Dart for the iOS and Android applications.

The initial product uses one shared Flutter codebase with platform-specific adapters where native behavior is required. The goal is to share product logic, design components, navigation, networking, persistence, and most tests without pretending that iOS and Android are identical platforms.

## Architectural Style

The application uses a feature-first structure with explicit layers:

```text
lib/
  app/
  core/
  features/
    authentication/
      presentation/
      application/
      domain/
      data/
    profiles/
    catalog/
    playback/
    downloads/
    subscriptions/
    notifications/
    parent_zone/
    settings/
```

Responsibilities:

- **Presentation:** widgets, screens, navigation bindings, user interaction, and state rendering.
- **Application:** use cases, orchestration, commands, queries, and feature-level workflows.
- **Domain:** entities, value objects, policies, and business rules that are meaningful on the client.
- **Data:** API clients, local persistence, repositories, platform adapters, serialization, and synchronization.

Features must not reach directly into another feature's data implementation.

## State Management and Dependency Injection

Use Riverpod for dependency injection and state management.

Rules:

- providers have explicit ownership and lifecycle;
- asynchronous state exposes loading, success, empty, and failure states;
- business workflows live in application services or controllers, not in widget build methods;
- global mutable singletons are avoided;
- side effects are isolated and testable;
- provider invalidation is deliberate and observable;
- long-lived state is minimized to prevent stale profile, entitlement, or account context.

A different state-management framework requires a new ADR or a superseding decision.

## Navigation

Use GoRouter for declarative navigation.

Navigation rules:

- authentication and onboarding routes are guarded;
- Parent Zone routes require active parent elevation;
- child mode cannot deep-link around parental gates;
- profile context is validated before feature access;
- unsupported or expired routes fall back safely;
- deep links are allow-listed and tested;
- navigation state is not treated as authorization.

The backend remains authoritative even when the client route guard passes.

## API Integration

- API clients are generated from or validated against OpenAPI.
- Network DTOs remain separate from domain and local persistence models.
- Standard error codes map to typed client failures.
- Correlation IDs are preserved for diagnostics.
- Timeouts are explicit.
- Retries are bounded and limited to transient, safe, or idempotent operations.
- Write operations that may be retried use idempotency keys.
- Authentication refresh is coordinated to avoid duplicate refresh storms.
- Clients tolerate unknown optional response fields.

## Local Persistence

The app uses a local database for:

- profile and account-scoped read models;
- catalog and story metadata cache;
- playback progress;
- durable offline operation queue;
- download manifests and asset metadata;
- notification state;
- synchronization cursors;
- safe non-sensitive configuration.

Rules:

- local schema changes are versioned and migrated;
- account or profile switches isolate or purge incompatible state;
- sensitive credentials are not stored in the content database;
- logout and account deletion trigger defined cleanup;
- cached data has freshness and ownership metadata;
- corruption recovery has a safe reset path.

## Secure Storage

Use platform-secure storage for refresh credentials and device-bound sensitive values.

Never store in plaintext preferences or logs:

- access or refresh tokens;
- parent PINs;
- biometric secrets;
- payment credentials;
- private signing material;
- raw child-related personal data beyond documented necessity.

Access tokens should remain memory-resident where practical and short-lived according to ADR-0005.

## Offline Behavior

Offline synchronization follows ADR-0014.

The app maintains:

- a durable operation queue;
- idempotency keys;
- transactionally updated local read models;
- synchronization cursors;
- bounded retries with backoff;
- conflict handling based on domain-specific rules;
- visible degraded states when server authority is required.

Offline mode must not bypass subscription, parental, privacy, or security policy.

## Audio Playback

Playback is implemented behind a platform-neutral application interface with native adapters where required.

Requirements include:

- foreground and background audio;
- lock-screen and headset controls;
- interruption handling;
- audio focus management;
- resume after process suspension where supported;
- progress checkpointing;
- playback speed controls if product-approved;
- local and streamed media sources;
- safe handling of expired signed URLs;
- telemetry without raw child-sensitive data.

Playback state must survive ordinary navigation and app lifecycle transitions without creating duplicate sessions.

## Downloads and Media Protection

Downloads require a server-authorized manifest.

The client validates:

- content version;
- checksum;
- expected size;
- entitlement requirements;
- expiry behavior;
- available device storage.

Partial downloads are resumable. Corrupted assets are removed. Expired or revoked content becomes unavailable according to server policy. Platform file protection and application-level controls are used where appropriate, but the client does not claim absolute DRM protection.

## Platform Adapters

Native or plugin-backed capabilities are isolated behind explicit interfaces:

- Apple and Google subscriptions;
- biometrics;
- secure storage;
- push notifications;
- background execution;
- audio sessions and media controls;
- connectivity;
- file system and storage capacity;
- app version and device information;
- analytics and crash reporting.

Feature code must not depend directly on plugin APIs when an adapter can preserve testability and replacement.

## Plugin Selection

A plugin is accepted only after reviewing:

- maintenance activity;
- supported OS versions;
- license;
- security posture;
- issue backlog;
- native implementation quality;
- lifecycle and background behavior;
- testability;
- migration and replacement risk.

Critical plugins require a documented fallback or ownership plan.

## Design System

The shared codebase owns a coherent design system containing:

- typography;
- spacing;
- shapes;
- motion guidance;
- child and parent themes;
- semantic colors;
- component states;
- accessibility behavior;
- responsive layout rules.

Feature screens use design-system components rather than duplicating visual primitives.

## Accessibility and Child Safety

Every child-facing feature definition of done includes:

- readable type and contrast;
- large, clear touch targets;
- screen-reader semantics where applicable;
- reduced-motion behavior;
- no manipulative purchase patterns;
- no accidental exit into external content;
- predictable navigation;
- clear differentiation between child and parent actions;
- localization-safe layouts;
- safe handling of interruptions and errors.

Parental gates must be effective without being deceptive or inaccessible to adults.

## Performance Budgets

The application defines measurable budgets for:

- cold and warm startup;
- frame rendering and jank;
- memory usage during playback and image-heavy browsing;
- local database query time;
- network payload size;
- download throughput and battery impact;
- application package size;
- background activity.

Images are resized and cached appropriately. Lists use lazy rendering. Expensive work is moved away from the UI thread. Performance is tested on representative low-, mid-, and high-range devices.

## Lifecycle and Background Execution

The app must handle:

- foreground, background, suspended, and terminated states;
- interrupted authentication or purchase flows;
- operating-system process termination;
- network changes;
- audio interruptions;
- insufficient storage;
- expired sessions;
- pending offline operations;
- notification navigation.

Background execution is designed around platform limits rather than assuming unrestricted timers or services.

## Security Boundaries

The mobile app is an untrusted client from the backend perspective.

Therefore:

- entitlement decisions are verified server-side;
- profile ownership is verified server-side;
- Parent Zone elevation is verified server-side;
- API authorization does not rely on hidden UI;
- local data may be inspected or modified on compromised devices;
- secrets are not embedded in the application;
- certificate or application integrity controls may add defense in depth but are not the sole security mechanism.

## Observability

Mobile telemetry includes:

- crash-free sessions;
- startup time;
- screen and API latency;
- playback-start success;
- playback interruption and failure categories;
- download success and corruption;
- synchronization queue depth and failures;
- purchase-flow outcomes;
- push notification handling;
- app version and supported OS distribution.

Telemetry must avoid unnecessary child-related information, raw content, PINs, tokens, and private payloads.

## Testing Strategy

Testing follows ADR-0010.

Required layers:

- unit tests for domain, repositories, use cases, and state controllers;
- widget tests for components and important states;
- navigation and route-guard tests;
- local database migration tests;
- API serialization and contract tests;
- integration tests for login, profiles, playback, downloads, offline synchronization, subscriptions, notifications, and Parent Zone;
- platform-adapter tests or fakes;
- golden tests for stable high-value screens;
- device-level tests for audio, purchases, biometrics, background behavior, and notifications.

Flaky tests require an owner, reason, and expiry if quarantined.

## Release Strategy

- iOS and Android builds use the same product version where practical.
- Platform-specific build numbers remain independent.
- Releases move through internal, test, staged, and production tracks.
- Feature flags reduce dependence on store-review timing.
- Backend compatibility supports older mobile versions during the documented support window.
- Forced upgrades are reserved for unsafe or incompatible clients.
- Store metadata, privacy declarations, permissions, and release notes are reviewed per release.

## Supported Platform Matrix

The project maintains a documented minimum and recommended OS version for iOS and Android.

Dropping an OS version requires:

- usage telemetry;
- security and plugin compatibility assessment;
- product approval;
- customer communication where necessary;
- release-note and support documentation updates.

## Failure and Degraded Modes

The app must provide deterministic behavior for:

- backend unavailable;
- stale catalog cache;
- expired credentials;
- refresh failure;
- RabbitMQ-driven backend work still pending;
- object storage or CDN unavailable;
- corrupted local database;
- insufficient storage;
- subscription provider unavailable;
- notification permission denied;
- unsupported app version.

Failures must not silently grant premium access, Parent Zone access, or profile ownership.

## Governance

A mobile architectural change requires review when it introduces:

- a new state-management framework;
- a new local database;
- a critical plugin;
- a broad native-code dependency;
- a second mobile codebase;
- embedded web application architecture;
- a new security authority on the client;
- a change to offline conflict rules.

Significant changes require an ADR and updates to `Mobile_Architecture.md` and relevant C4 views.

## Consequences

### Positive

- Shared implementation across iOS and Android.
- Consistent design system and animation behavior.
- Strong fit for custom child-oriented UI.
- Reduced feature and testing duplication compared with two native applications.
- Good testability for widgets, state, and application logic.
- Explicit adapter boundaries preserve access to native capabilities.
- One architecture for offline, security, and API behavior.

### Negative

- Advanced audio, purchase, notification, and background features require native integration.
- Plugin quality and platform differences create operational risk.
- Application size and performance require continuous monitoring.
- Developers need Dart and Flutter-specific expertise.
- Shared code can accumulate abstractions that obscure genuine platform differences.
- Native debugging remains necessary for critical flows.

## Alternatives Considered

### Separate native Swift and Kotlin applications

Rejected for the initial release because it duplicates most feature implementation, testing, design-system work, and release coordination. Native components remain appropriate behind adapters.

### React Native

Rejected because Flutter provides stronger rendering consistency for the highly customized visual experience and keeps the core child interface independent of a JavaScript runtime.

### Progressive Web Application

Rejected because the product depends on reliable background audio, offline protected media, subscriptions, notifications, biometrics, app-store distribution, and native media integration.

### Kotlin Multiplatform with native UIs

Deferred. It can share domain and networking code while preserving native UI, but increases the need to maintain two presentation layers and does not meet the initial delivery-efficiency goal as directly.

### Fully shared code without native adapters

Rejected because subscriptions, audio lifecycle, notifications, background work, and biometrics have material platform differences.

## Follow-up Actions

- Maintain a supported-device and operating-system matrix.
- Benchmark playback, startup, memory, battery, and scrolling on representative devices.
- Validate critical plugins before feature implementation depends on them.
- Establish platform-adapter contracts and test fakes.
- Maintain golden tests for stable child-facing screens.
- Document and review all native platform code.
- Define local-database migration and corruption recovery procedures.
- Establish mobile release, rollback, and forced-upgrade policies.
- Review this ADR before adopting a second mobile framework or separate native applications.
