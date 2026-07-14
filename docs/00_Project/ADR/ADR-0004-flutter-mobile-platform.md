# ADR-0004: Use Flutter for the Mobile Applications

Status: Accepted
Date: 2026-07-14

## Context

KidsAudioBookPlatform must support iOS and Android with a highly visual child experience, audio playback, offline downloads, local persistence, push notifications, animations, parental controls, and platform purchase integrations. The project should minimize duplicated product logic and design implementation while retaining access to native capabilities.

## Decision

Flutter and Dart will be used for the mobile applications. The initial product will use one shared Flutter codebase with platform-specific adapters where required.

The mobile architecture will follow these rules:

- feature-first organization;
- explicit presentation, application, domain, and data responsibilities;
- Riverpod for dependency injection and state management;
- GoRouter for declarative navigation and guarded routes;
- typed API clients generated or validated against OpenAPI;
- secure storage for refresh credentials and sensitive device-bound data;
- a local database for profiles, catalog cache, progress queue, download manifests, and notification state;
- platform adapters for subscriptions, biometrics, media controls, background execution, and notifications;
- no business entitlement decisions trusted solely to the client;
- accessibility and child-safe interaction requirements included in every feature definition of done.

## Consequences

### Positive

- Shared implementation across iOS and Android.
- Consistent design system and animation behavior.
- Strong fit for custom child-oriented UI.
- Reduced development cost compared with two separate native applications.
- Good testability for widgets and state logic.

### Negative

- Some advanced audio, purchase, and background features require native integration.
- Platform plugin quality must be evaluated carefully.
- Application size and performance must be monitored on lower-end devices.
- Developers need Dart and Flutter-specific expertise.

## Alternatives Considered

### Separate native Swift and Kotlin applications

Rejected for the initial release because it doubles most feature implementation, testing, and UI maintenance work. It remains an option for isolated native components if required.

### React Native

Rejected because Flutter provides stronger rendering consistency for the highly customized visual experience and avoids depending on a JavaScript runtime for the core child interface.

### Progressive Web Application

Rejected because the product depends on reliable background audio, offline encrypted media, subscriptions, notifications, biometrics, and app-store distribution.

## Follow-up Actions

- Establish a supported-device and operating-system matrix.
- Run playback and memory tests on representative low-, mid-, and high-range devices.
- Validate purchase, download, and background audio plugins before implementation depends on them.
- Maintain golden tests for critical child-facing screens.
- Document all native platform code and keep it behind explicit adapters.
