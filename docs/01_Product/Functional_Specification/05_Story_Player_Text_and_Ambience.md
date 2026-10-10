# 05 — Story Audio Player, Synchronized Text, Illustrations and Ambience

**Actor:** Child through an approved profile, with parent configured restrictions.
**Requirements:** PRD-04/05/10/11; FR-PL-001..007 and FR-CA-007.
**Owners:** playback-service for sessions/progress, catalog-service for content metadata, media-service for approved renditions, billing-service for Premium entitlement.

## 1. Initiating playback

**FS-PL-001** Tapping Play opens a visible loading/authorizing state; POST /playback/sessions verifies account, selected profile ownership, age/category policy, story publication, and applicable entitlement before issuing a short-lived signed media URL.

**FS-PL-002** A cached cover, Free badge, downloaded manifest or stored session ID never replaces the current authorization decision for a new online stream.

**FS-PL-003** If authorization fails, the player cannot enter a misleading Playing state. It shows a child-safe reason (unavailable, connection or adult-only Premium action) without revealing internal rules or technical details.

**FS-PL-004** Repeated Play taps or a lost response use safe deduplication by the documented playback session mechanism; no duplicate completion or extra advertising counter may be generated.

## 2. Player surface and controls

The player shows story title, approved art, large Play/Pause, seek/progress control, elapsed and total duration, previous/next where editorially meaningful, child-safe exit, and optional text/illustration and ambience views. A series navigation action must open only the next approved published episode; next does not skip parental eligibility.

**FS-PL-005** Pause stops audio progression and reflects Paused immediately. Resume returns from the current valid position and reconstructs player state after transient interruption. Exit saves a checkpoint where possible.

**FS-PL-006** Seeking is bounded to [0, playable duration] and updates displayed text/illustration to the segment containing the new position. A seek past the end must not award unearned completion.

**FS-PL-007** Progress display is driven by decoded playback position, not a free-running visual animation. The app never assumes a story completed because the screen remained open.

**FS-PL-008** Background audio, lock-screen and headset controls must follow iOS/Android platform policies; OS audio focus may pause or duck playback, and audible state must match visible state after foregrounding.

**FS-PL-009** On interruption (call, device lock, headphones disconnected, another audio app), safe pause/duck policy is applied with recoverable position; no surprise loud audio is allowed after regain of focus.

**FS-PL-010** Parent-configured playback limits, if enabled, are enforced on server decisions where feasible and locally for immediate UI interaction; a child cannot bypass restrictions by restarting the app.

## 3. Playback state model

| State | Allowed transitions | UI meaning |
|---|---|---|
| Idle | Authorizing | Story selected; no media grant |
| Authorizing | Buffering / Denied / Error | Server eligibility decision pending |
| Buffering | Playing / Retryable error | Approved media fetching |
| Playing | Paused / Buffering / Completed / Stopped | Audio time advances; text/media sync |
| Paused | Playing / Stopped | Progress frozen |
| Recoverable error | Buffering / Stopped | Retry without losing stored position |
| Completed | Replay / Next eligible story / Exit | Completion recorded according to policy |
| Denied | Back / Adult challenge where applicable | No playable data exposed |

**FS-PL-011** UI state transitions reflect actual media player events and backend authorization. Repeated retries do not bypass denial.

## 4. Segment-synchronized text and illustrations

MVP requires segment-level synchronization. A segment has approved text, start and end time, optional illustration ID and optional speaker/scene metadata. Audio is the timing authority.

**FS-PL-012** For each seek, resume, pause and playback speed change (if speed control is supported), determine active segment from audio position; highlight only the applicable segment, not wall-clock progress.

**FS-PL-013** Missing optional illustration does not stop narration; show the last approved image or neutral safe background. Missing mandatory audio rendition prevents playback. Editorially unapproved image/text never appears.

**FS-PL-014** Voice, text and illustration locale must be compatible. Mixed language requires a deliberately approved localized rendition, not silent fallback.

**FS-PL-015** Highlighting remains perceivable without color alone and screen readers can access the text if parents enable supported accessibility features. Motion of artwork obeys reduced-motion settings.

**FS-PL-016** End-of-segment ties must be deterministic, and segment time validation must prevent inverted intervals, overlaps that confuse the reader and text running beyond audio duration. Exact time format/schema is governed by media/catalog contracts.

## 5. Ambience and bedtime sound

Selected ambient tracks are editorially approved non-story content, offered for sleep/calm as allowed by Product Bible. Ambient player may run alone or alongside narration if available; the parent may set a preferred track. Auto-stop/sleep timer requires reviewed UX and policy decisions.

**FS-PL-017** GET /ambient-sounds returns only eligible approved sounds; choose/play/pause/stop ambience without unintended navigation away from the story.

**FS-PL-018** Default mixing must favor intelligible narration and safe comfortable volume; a new story must not produce a loud sudden increase because ambience was already active.

**FS-PL-019** Pausing the story, stopping ambience, changing profile or interrupting by OS audio focus has consistent independently observable outcomes. Ambient tracks should not mask urgent OS sounds.

**FS-PL-020** Looping ambience or a timer finishing does not count as a completed story for progress/advertising. A timer ending while a story is playing must follow a clearly specified stop/fade rule before implementation.

## 6. Progress, completion and analytics

PUT /playback/sessions/{sessionId}/progress stores server-side position. POST /playback/sessions/{sessionId}/complete marks a qualified session complete; POST /stop ends a session. History and Continue Listening are profile-scoped.

**FS-PL-021** Completion is based on the accepted playback completion policy, not client-provided arbitrary percentages. Repeated completion requests must not inflate achievements, analytics, ads or history. Any completion threshold requires an explicit implementation decision consistent with API/DB.

**FS-PL-022** Position sent to backend respects the existing API unit conventions (seconds) and the database unit mapping; millisecond/second conversion must not cause drift or overflow.

**FS-PL-023** A Completed story may be replayed intentionally without silently resetting its history or another device's authoritative completion state. Continue Listening excludes completed items according to documented read-model policy.

## 7. Failure and edge cases

| Case | Player experience | Safety/consistency |
|---|---|---|
| CDN range request fails | Buffering/retry; preserve time | Never expose private object credentials |
| Signed URL expires | Authorized refresh if supported; else retry session safely | No perpetual privilege |
| Profile switched mid-stream | Stop/re-authorize in new context | No sibling leakage |
| Subscription revoked | New Premium grants denied; ongoing offline behavior follows approved policy | No unlimited cache authorization |
| Media takedown during session | Enforce documented urgent revocation policy | No new grant |
| App terminated in background | Resume from saved checkpoint | No duplicate completion |
| Segment missing | Narration usable with safe fallback if allowed | No unreviewed content |
| Ambient network failure | Story continues when eligible | Optional sound must not block narration |
| Audio focus loss | Pause/duck as required | No unsafe surprise audio |

## 8. Given / When / Then

- **PL-AT-01:** Given no valid entitlement for Premium, when a child taps Play, then no signed Premium media grant is returned.
- **PL-AT-02:** Given audio is at 90 seconds, when user seeks to 150 seconds, then text highlight and illustration match the correct segment, not the previous wall clock.
- **PL-AT-03:** Given call interruption, when app returns, then displayed position and audible state are consistent and resumable.
- **PL-AT-04:** Given repeated Complete requests for a session, then history/completion side effects occur once.
- **PL-AT-05:** Given ambience active then new narration starts, then mix levels preserve clear narration and no unexpected loudness.
- **PL-AT-06:** Given story suspension while a card is cached, when starting a new stream, then the playback grant is denied.
- **PL-AT-07:** Given profile A is playing and profile B is selected, then playback must stop or reauthorize under B before any private data is shown.
- **PL-AT-08:** Given an illustration is absent but optional, when playback reaches its segment, then audio continues and a safe visual fallback appears.

**Decisions to finalize:** exact sleep timer, automatic next-episode behavior, completion threshold, playback limit defaults, download/offline revocation timing. See [Progress/offline](06_Favorites_History_Downloads_and_Sync.md), [Decision Register](../../00_Project/DECISION_REGISTER.md).
