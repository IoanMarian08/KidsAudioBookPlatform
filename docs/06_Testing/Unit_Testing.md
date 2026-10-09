# Unit Testing Guidelines

Version: 2.0.0  
Status: Active baseline  
Owner: Backend and Mobile Engineering

## 1. Boundary

Unit tests exercise a class/function's **business contract** without booting the full application or contacting databases, brokers, file systems, HTTP or real store providers. JUnit 5 and Mockito may be used for Java 21; Flutter uses flutter_test.

Prefer testing through stable public behavior rather than private methods or implementation order.

## 2. Java test style

Use Given / When / Then for names or DisplayName matching the repository convention. Test each observable business branch directly. Avoid helpers that hide the entire scenario or overcomplicated parameterization for only a few test cases.

~~~java
@Test
@DisplayName("Given an expired entitlement, when requesting premium playback, then access is denied")
void deniesExpiredEntitlement() {
    // Given
    var policy = new PlaybackAccessPolicy();
    var entitlement = Entitlement.expired();

    // When
    boolean allowed = policy.canPlayPremium(entitlement);

    // Then
    assertThat(allowed).isFalse();
}
~~~

This illustrates intent rather than prescribing the concrete production API; adapt entity types and imports to actual domain classes.

## 3. Essential unit categories

- Value object invariants: IDs, timestamps, locale, age bands, monetary units.
- Permission policies: owner, selected profile and Parent Zone scope.
- Entitlement state: active, expired, cancelled, refunded, grace, provider pending.
- Story publication: draft, review, scheduled, published, suspended, archived.
- Progress: zero, boundaries, completion, revisions, stale/duplicate write.
- Offline grant eligibility and expiry.
- Retry policy/idempotency key computation.
- DTO validation, mapping and rejection of malformed inputs.
- Cache key versioning and invalidation decision logic.
- Correct event construction without sending messages.

## 4. Mocking policy

Mock external collaborators, not the class under test. Limit mocking chains and interactions; assert actual output/state first. Use realistic clocks injected via Clock rather than waiting for real time. Deterministic UUID/ID generation and fixed seeds make failures reproducible.

## 5. Flutter unit/widget testing

Test player view-model state (idle/buffering/playing/paused/error), progress formatting, theme/locale switching, user-friendly errors and eligibility presentation. For widget tests validate semantics, disabled actions and navigation boundaries. Do not rely solely on golden pixel tests to prove accessibility.

## 6. Negative cases

Every permission-related function needs tests for missing credentials, foreign owner, archived profile, expired elevation and invalid inputs. Every billing policy needs forged/stale/unverified provider state tests. Do not test only the branch that returns true.

## 7. Anti-patterns

Avoid tests that depend on execution order, sleep(), random data without seed, HTTP calls to production, implementation-specific private method invocation, overly broad @SpringBootTest for pure policies, and asserting only that no exception was thrown.

## 8. Ready checklist

[ ] Tests readable and deterministic  
[ ] No external I/O  
[ ] Negative and boundary cases covered  
[ ] Domain language matches business requirements  
[ ] Changes in behavior fail a meaningful assertion  
[ ] Test names and failure output diagnose the rule  

Related: [Integration Testing](Integration_Testing.md), [Testing Strategy](Testing_Strategy.md), [Coding Standards](../04_Engineering/Coding_Standards.md).
