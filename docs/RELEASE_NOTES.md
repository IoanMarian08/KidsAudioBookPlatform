# Product Release Notes

Version: 1.0.0  
Status: Template — **no customer-facing release is asserted by this document**  
Owner: Product and Release Engineering

## Purpose

This file records real application releases once production/mobile-store deployments are performed. Documentation commits on the architecture-foundation branch do **not** constitute shipped app releases.

## Release entry template

~~~markdown
## vX.Y.Z — YYYY-MM-DD

**Platforms:** Android / iOS / Backend / Admin
**Release owner:**
**Application commit(s):**
**Artifacts / digests:**
**App store build numbers:**
**Deployment environment and timestamp:**

### For parents and children
- New features:
- Improvements:
- Bug fixes:

### Technical changes
- Backend/API compatibility:
- Database migrations:
- Event schema changes:
- Content catalog changes:
- Feature flag changes:

### Safety and privacy
- Parent Zone / authorization changes:
- Child content moderation and age policy:
- Data handling / retention / consent changes:

### Verification
- Acceptance / E2E testing:
- Security scan and approval:
- Performance/SLO result:
- Restore and rollback readiness:

### Known limitations
- Known issue / impact / workaround / owner:

### Rollout and rollback
- Gradual rollout plan:
- Health metrics and on-call:
- Rollback trigger and procedure:
~~~

## Release policy

1. Publish only after deployment/build identity is verified.
2. Customer notes must be comprehensible and should not expose exploit or internal security details.
3. Distinguish mobile-store release from backend-only releases and feature-flag enablement.
4. Release notes and migrations must be traceable to tested PRs/requirements.
5. Pricing, subscriptions, privacy and age-safety changes need explicit Product/Legal review.
6. Keep historical release entries immutable except clearly marked corrections.

Related: [Deployment](05_DevOps/Deployment.md), [CI/CD](05_DevOps/CI_CD.md), [Product Roadmap](01_Product/Roadmap.md), [Documentation Changelog](PROJECT_CHANGELOG.md).
