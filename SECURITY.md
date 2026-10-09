# Security Policy

## Project maturity

KidsAudioBookPlatform currently contains extensive architecture and product documentation; working production services are not yet claimed. Security findings may still matter, including accidental credentials, unsafe examples, authorization design errors and privacy risks.

## Private disclosure

**Do not open a public GitHub issue for suspected vulnerabilities**, exposed credentials, potentially identifying data about children, or working exploit details. Use the repository's private GitHub security-advisory reporting feature if enabled (Security → Advisories → Report a vulnerability). If private reporting is not enabled, ask the repository owner for a private reporting channel **without posting exploit details publicly**. No unverified email address or response SLA is promised here.

When safely reporting, include: affected files/commit, reproduction conditions (without publishing secrets), expected vs. observed behavior, impact on account/child privacy, and any mitigation you already applied. Do not test against real users or production systems without explicit authorization.

## Security baseline

- Parent Zone, child profile ownership and subscription/entitlement decisions are server-side boundaries.
- No sensitive tokens, passwords, PINs, signed URLs or real children's PII in source, logs, fixtures or screenshots.
- Uploaded media stays private pending malware/rights/editorial review; media access uses short-lived authorization.
- All admin actions use least privilege and an audit trail.
- CI should include secret scanning, dependency scanning and security regression checks.

See [Security Architecture](docs/03_Architecture/Security_Architecture.md), [Security Testing](docs/06_Testing/Security_Testing.md) and [Decision Register](docs/00_Project/DECISION_REGISTER.md).

## Coordinated resolution

The maintainer should acknowledge a credible private report, assess severity and child impact, prevent disclosure, develop a fix, test regressions, and publish an advisory when appropriate. Any handling of personal data must follow applicable privacy and incident obligations. Exact SLA, disclosure timelines and support contact remain decisions for the repository owner.
