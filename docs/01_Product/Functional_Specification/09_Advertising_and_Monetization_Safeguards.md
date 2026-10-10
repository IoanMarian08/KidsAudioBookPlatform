# 09 — Child-Safe Advertising and Monetization Safeguards

**Release state:** [GATED / DISABLED BY DEFAULT]. This chapter documents optional product intent, NOT approval to serve ads to children.
**Relevant:** Product Bible section 18; PRD-13; [Advertising blueprint](../../07_Blueprints/07_Advertising_Eligibility.md).
**Owner:** advertising-policy-service, only when approved; playback-service supplies validated completion, billing-service supplies entitlements.

## 1. Policy and safety gate

Product Bible describes a possible maximum of one post-session ad after two completed listening sessions, roughly 15 seconds duration, only for eligible Free accounts. Those are intended candidate rules; actual activation requires Product/Legal/Security/store review by market and advertising partner [OPEN: DEC-004]. Until then, advertising stays off, SDKs need not load in Child World, and the app plays normal authorized content.

**FS-AD-001** No ad may interrupt a story, appear over player controls, trick a child into clicking, use aggressive countdown/reward pressure or create unrestricted external links.

**FS-AD-002** No child-behavior-based targeting, personal-profile export, sensitive data sharing or unreviewed creative is permitted. The parent controls applicable consent/settings where required.

**FS-AD-003** Premium verified entitlement suppresses advertising, including decisions already queued but not delivered. Child cannot change advertising policy in Child World.

**FS-AD-004** Unknown consent, unavailable eligibility authority, unsupported country or unapproved provider must fail closed to no ad, not a guessed eligible placement.

## 2. Eligibility decision and counter flow

If and only if activated, an ad can be considered AFTER a qualified completed session:
1. Playback has recorded server-accepted completion, not arbitrary UI event.
2. Advertising policy confirms account/profile ownership and deduplication of this session.
3. Feature enabled for approved country, platform and parental consent state.
4. Verified Free entitlement (Premium suppresses).
5. Completed-session counter/cooldown and age/creative controls satisfy active policy.
6. Issue a short-lived, single-use decision token for eligible placement.
7. Client displays only an approved creative and sends outcome result once.

Current API: POST /advertising/decisions and POST /advertising/decisions/{decisionToken}/result; no other ad endpoint is implied.

**FS-AD-005** Duplicate story completion events do not increment the ad counter twice. Seeking to story end, looping ambient audio or abandoning a session is not automatically qualified completion.

**FS-AD-006** A token must be scoped to adult account, child profile, completed playback session and policy version, with replay prevention. A child cannot fabricate or reuse another profile's token.

**FS-AD-007** If a provider cannot display safely, choose no ad and return to normal Child World; playback remains available without ad dependencies.

## 3. Parent-facing monetization

Premium upsell in Parent Zone may explain ad-free benefits and plan differences. In Child World, gentle non-pressuring messages can direct an adult to Parent Zone; no immediate checkout/deep link to third-party ad landing pages.

**FS-AD-008** Paid upgrade messaging must avoid misleading claims about number of ads, trial eligibility, cancellation or already-paid features.

**FS-AD-009** If an ad-free promise is shown for Premium, the backend and client both respect it immediately after a verified upgrade, not on a guessed local subscription flag.

**FS-AD-010** If the legal/policy owner rejects child-directed advertising, the feature stays disabled and the product remains functional with Free stories and premium subscriptions.

## 4. Outcome and failure states

| Condition | Required outcome |
|---|---|
| Advertising disabled | No SDK behavior or eligibility decision affecting the child |
| Premium account | Ineligible even if earlier Free counter threshold met |
| Provider offline | No ad; continue listening/discovery normally |
| Consent missing/withdrawn | No ad and no child data transfer |
| Creative not approved | No presentation |
| Duplicate completion | One logical count |
| Forged token/result | Denied/audited |
| Country disallowed | No ad |
| Parent settings block placement | No ad |
| Ambient track finishes | Not treated as a story session completion |

## 5. Given / When / Then

- **AD-AT-01:** Given the feature is disabled, when any story finishes, then no advertising provider requests or child ad UI appear.
- **AD-AT-02:** Given verified Premium, when post-session eligibility is requested, then the decision is ineligible.
- **AD-AT-03:** Given a partial session or invalid completion, when ad decision is requested, then no eligible token is issued.
- **AD-AT-04:** Given the same completed session event is replayed, then it contributes at most once to counters.
- **AD-AT-05:** Given a valid token used already, when reporting another impression, then replay is rejected.
- **AD-AT-06:** Given an unapproved creative/vendor/country, then eligibility fails closed and story usage continues.
- **AD-AT-07:** Given the parent activates verified Premium after an eligible token was created, then the ad is suppressed.

## 6. Mandatory sign-offs

Product owner must select or reject ads; Legal/Privacy must validate the children's app regulatory position and consent; Security must review SDK data collection and payloads; Content/editorial must approve creative categories; mobile platform reviewers must verify store policies and child experience; QA must test in real supported markets. **Do not turn this chapter into a mandate to ship advertising.**
