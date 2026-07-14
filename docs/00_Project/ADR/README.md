# Architecture Decision Records

This directory contains the significant architecture decisions for KidsAudioBookPlatform.

## Status Values

- Proposed
- Accepted
- Superseded
- Deprecated
- Rejected

## Naming Convention

`ADR-XXXX-short-title.md`

Example: `ADR-0001-modular-monolith-first.md`

## Required Structure

Each ADR must include:

1. Title
2. Status
3. Date
4. Context
5. Decision
6. Consequences
7. Alternatives Considered
8. Follow-up Actions

## Rules

- ADRs are immutable historical records after acceptance, except for typo corrections.
- A changed decision requires a new ADR that supersedes the previous one.
- Every important platform, persistence, communication, security, or deployment decision should reference an ADR.
- Pull requests that introduce a new architectural direction must include or update the relevant ADR.

## Initial ADR Set

- ADR-0001: Start with a modular monolith
- ADR-0002: Use PostgreSQL as the primary system of record
- ADR-0003: Use REST for synchronous APIs and RabbitMQ for asynchronous events
- ADR-0004: Use Flutter for the mobile applications
- ADR-0005: Use short-lived access tokens and rotating refresh tokens
