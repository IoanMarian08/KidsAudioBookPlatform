# C4 Model

Version: 1.0.0  
Status: Draft

## Purpose

This folder contains the official C4 architecture views for KidsAudioBookPlatform. The diagrams are implementation-oriented and must stay synchronized with `Software_Architecture.md`, `Backend_Architecture.md`, `Mobile_Architecture.md`, `Admin_Dashboard.md`, `Database_Design.md`, and `API_Specification.md`.

## Diagram Set

1. System Context — actors, external systems, and platform boundary.
2. Container View — mobile app, admin dashboard, backend services, databases, messaging, cache, object storage, observability.
3. Component View — internal components of the backend application and their responsibilities.
4. Code View — representative module/package structure for implementation.

## System Context

```mermaid
flowchart LR
    Parent[Parent or Guardian]
    Child[Child Listener]
    Admin[Platform Administrator]
    Store[Apple App Store / Google Play]
    FCM[Firebase Cloud Messaging]
    Email[Email Provider]
    CDN[CDN / Object Storage]
    Platform[KidsAudioBookPlatform]

    Parent -->|creates account, manages profiles, subscriptions, settings| Platform
    Child -->|discovers and listens to stories| Platform
    Admin -->|publishes content, manages users, campaigns, support| Platform
    Platform -->|validates purchases and entitlements| Store
    Platform -->|sends push notifications| FCM
    Platform -->|sends transactional emails| Email
    Platform -->|delivers audio and images| CDN
```

## Container View

```mermaid
flowchart TB
    Mobile[Flutter Mobile Application]
    AdminUI[Admin Dashboard]
    API[Spring Boot Backend]
    Worker[Async Workers]
    PG[(PostgreSQL)]
    Redis[(Redis)]
    MQ[(RabbitMQ)]
    Object[(MinIO / S3)]
    Obs[Prometheus / Grafana / Loki]
    Push[Firebase Cloud Messaging]
    Stores[Apple / Google Billing]

    Mobile -->|HTTPS REST| API
    AdminUI -->|HTTPS REST| API
    API --> PG
    API --> Redis
    API --> MQ
    API --> Object
    Worker --> MQ
    Worker --> PG
    Worker --> Object
    Worker --> Push
    API --> Stores
    API --> Obs
    Worker --> Obs
```

## Backend Component View

```mermaid
flowchart LR
    Controllers[REST Controllers]
    Auth[Identity & Access]
    Profiles[Child Profiles]
    Catalog[Story Catalog]
    Playback[Playback & Progress]
    Billing[Subscriptions & Entitlements]
    Notifications[Notifications]
    Admin[Administration]
    Media[Media Management]
    Events[Event Publishing / Consumption]
    Persistence[Repositories & Persistence]

    Controllers --> Auth
    Controllers --> Profiles
    Controllers --> Catalog
    Controllers --> Playback
    Controllers --> Billing
    Controllers --> Notifications
    Controllers --> Admin
    Admin --> Media
    Catalog --> Media
    Auth --> Persistence
    Profiles --> Persistence
    Catalog --> Persistence
    Playback --> Persistence
    Billing --> Persistence
    Notifications --> Persistence
    Auth --> Events
    Profiles --> Events
    Catalog --> Events
    Playback --> Events
    Billing --> Events
    Events --> Notifications
```

## Code View

```text
backend/
  bootstrap/
  common/
    api/
    security/
    logging/
    events/
    validation/
  identity/
  profiles/
  catalog/
  playback/
  subscriptions/
  notifications/
  administration/
  media/

Each bounded context follows:
  api/
  application/
  domain/
  infrastructure/
```

## Diagram Rules

- A diagram must have a clear owner and purpose.
- Names must match code modules and API terminology.
- External systems must be visually separated from platform-owned components.
- Relationships must state protocol or intent where useful.
- C4 diagrams describe structure, while `System_Flows.md` describes behavior.
- Significant changes require an ADR and a diagram update in the same pull request.

## Review Checklist

- Does every container have one primary responsibility?
- Are data ownership boundaries explicit?
- Are synchronous and asynchronous interactions distinguishable?
- Are trust boundaries visible?
- Are external dependencies represented?
- Does the diagram still match the repository structure?
