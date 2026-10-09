# Motion and Animation Guidelines

Version: 2.0.0  
Status: Active guidance; values subject to device testing  
Owner: UX/UI and Mobile

## 1. Principle

Motion should convey location, state and gentle story-world atmosphere. It must not create urgency, reward pressure, flashing stimuli or keep a child scrolling. Bedtime and low-power modes reduce motion by default.

## 2. Proposed motion tokens

| Token | Duration | Easing | Use |
|---|---:|---|---|
| immediate | 0–100 ms | linear | Press feedback |
| quick | 120–180 ms | ease-out | Icon state transitions |
| standard | 200–280 ms | ease-in-out | Card/select transitions |
| deliberate | 300–450 ms | ease-in-out | Screen/shared-element transition |
| ambient | 2–8 s | very subtle continuous | Nonessential environmental scene only |

Values are illustrative; validate with frame-budget measurements and motion-sensitive user research. Never animate text readability or progress truth.

## 3. Allowed patterns

- Small press-state feedback and unobtrusive selection emphasis.
- Gentle crossfades between day/evening/night backgrounds.
- Skeleton placeholders, if reduced-motion alternative exists.
- Progress/queue indicators tied to real backend or player state.
- Mascot greeting with bounded duration and opt-out.
- Playback cue changes driven by audio timeline; no fast flash during seeks.

## 4. Forbidden patterns

- Autoplay surprise animations/audio, infinite confetti, shaking upgrade buttons.
- Streak urgency, timers designed to coerce children, attention traps.
- Strobing, high-frequency color changes, unreadable blur transitions.
- Motion required to understand premium, error or safety messages.
- Long loading animations when the app is actually blocked without recovery.

## 5. Reduced motion and low power

Honor platform Reduce Motion settings. Replace camera pans, parallax and bouncing transitions with immediate state or short crossfade. In low-power/battery-saver modes, disable ornamental continuous animation; playback controls and progress remain functional. Stop animations when the route is offscreen.

## 6. State machine example

~~~mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Pressed: user tap
    Pressed --> Loading: request accepted
    Loading --> Success: content ready
    Loading --> RecoverableError: timeout or offline
    RecoverableError --> Loading: retry
    Success --> Idle: leave screen
~~~

Animation reflects this state machine. It must never create a fake success state before the backend/player confirms it.

## 7. Implementation and testing

Flutter animations should use built-in transitions and bounded AnimationControllers; dispose controllers correctly. Do not trigger costly image decoding on every frame. Measure 16.7 ms frame budget at 60 Hz (and platform-specific refresh targets) on low-tier test devices. Review jank, battery consumption and interruption behavior while background audio plays.

**Checklist:** reduced motion honored, no flashing, all infinite loops justified, time-of-day transitions subtle, no animation blocking screen readers, low-power friendly, failure/empty/offline states correct.

Related: [Mascot](Mascot.md), [UI Design System](UI_Design_System.md), [UX Guidelines](UX_Guidelines.md).
