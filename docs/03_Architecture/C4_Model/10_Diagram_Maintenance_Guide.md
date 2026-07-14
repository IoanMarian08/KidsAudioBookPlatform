# Diagram Maintenance Guide

This document defines how C4 diagrams are versioned, reviewed, updated and kept synchronized with implementation.

## Goals
- Keep architecture diagrams aligned with code.
- Define ownership.
- Establish review cadence.

## Rules
- Every architecture change updates the relevant diagram.
- Every new bounded context requires Context, Container and Component updates.
- Diagram changes require ADR references.
- Mermaid syntax must remain GitHub-compatible.

## Review Checklist
- Naming consistency
- Boundary validation
- External systems
- Security boundaries
- Data ownership
- Cross-document references
