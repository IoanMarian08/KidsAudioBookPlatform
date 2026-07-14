# Product Bible

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Active |
| Owner | Ioan Marghioala |
| Contributors | Product, Design, Architecture, Engineering |
| Last Updated | 2026-07-15 |
| Repository | KidsAudioBookPlatform |
| Scope | Product Foundation |

---

## 1. Purpose

This document is the canonical product reference for KidsAudioBookPlatform. It defines the product identity, audience, emotional promise, experience model, business model, content rules, safety boundaries, tone, visual direction, and product decision principles.

It is intended to align product, design, mobile, backend, content, QA, support, operations, and future collaborators. When a feature proposal conflicts with this document, the proposal must be changed or the Product Bible must be deliberately updated through an approved product decision.

The Product Bible explains what the product is and how it should feel. Detailed implementation rules belong in architecture, API, database, security, and operational documentation.

---

## 2. Product Identity

KidsAudioBookPlatform is a safe, calm, parent-controlled story world for young children.

It combines:

- narrated audio stories;
- synchronized text;
- story illustrations;
- series and episodes;
- child profiles;
- personalized child rooms;
- ambient sounds;
- offline listening;
- parent controls;
- free and premium access.

The product is not simply an audiobook catalog. It is not a generic reading application, a social network, an unrestricted content platform, or a game built around rewards and pressure.

The intended emotional mix is:

- safety;
- warmth;
- curiosity;
- adventure;
- calm;
- attention;
- trust.

The product should be especially strong as a bedtime and quiet-time companion while remaining useful during travel, independent play, learning, and family routines.

---

## 3. Internal Motto

> A safe world where every evening begins with a story.

This motto is an internal decision filter. A feature should be questioned when it does not strengthen at least one of the following:

- child safety;
- parent trust;
- story discovery;
- listening quality;
- calm routines;
- product clarity;
- sustainable business value.

---

## 4. Product Promise

### To children

A magical, understandable, calm, and safe place where stories are easy to discover and enjoy.

### To parents

A trusted application where content, access, subscriptions, notifications, profiles, downloads, and safety settings remain under adult control.

### To creators

A future platform where approved stories, narration, illustrations, and educational content can be published through clear workflows and quality standards.

---

## 5. Product Principles

### 5.1 Child First

Every child-facing decision must prioritize safety, clarity, emotional comfort, accessibility, and age-appropriate interaction.

### 5.2 Parent in Control

The parent controls accounts, profiles, purchases, subscriptions, security, communication preferences, downloads, and sensitive settings.

### 5.3 Magic Without Complexity

The child experience should feel rich without requiring complex navigation, reading ability, or technical understanding.

### 5.4 Stories Before Gamification

The story is the primary reward. The product must not depend on manipulative streaks, loss aversion, aggressive points, or pressure loops.

### 5.5 Calm by Design

Motion, sound, color, notifications, advertising, and upsell behavior should avoid overstimulation.

### 5.6 Privacy by Default

Only necessary data should be collected. Child-related data must be minimized, protected, and excluded from unnecessary telemetry or marketing.

### 5.7 Clear Commercial Boundaries

Premium value must be understandable. Conversion should come from useful benefits, not confusion, fear, or pressure on children.

### 5.8 Quality Over Volume

A smaller library of well-produced, safe, and coherent stories is preferable to a large inconsistent catalog.

---

## 6. Audience

### 6.1 Primary child audience

The initial product focuses on children aged 0-7.

The experience must support children who:

- cannot read;
- are beginning to read;
- have short attention spans;
- use shared family devices;
- need large touch targets;
- require simple navigation;
- benefit from repetition and predictable layouts;
- may use the application during bedtime routines.

Suggested internal age bands:

| Age band | Product implications |
|---|---|
| 0-2 | Parent-led use, very simple visuals, calming audio, short content |
| 3-4 | Large controls, strong visual cues, short stories, minimal text dependency |
| 5-7 | More independent discovery, synchronized text, series, educational themes |

Age bands guide recommendations and design but must not be treated as medical or developmental assessments.

### 6.2 Parent audience

Parents need:

- fast onboarding;
- clear privacy and safety information;
- transparent pricing;
- reliable playback;
- predictable controls;
- easy profile management;
- simple subscription management;
- useful support;
- confidence that children cannot reach adult areas accidentally.

### 6.3 Future audiences

Potential future audiences include:

- kindergartens;
- schools;
- therapists or educators;
- authors;
- narrators;
- illustrators;
- family accounts with older children.

These audiences are not allowed to weaken the simplicity of the initial child and parent experience.

---

## 7. Two-World Experience Model

The application contains two intentionally different worlds.

### 7.1 Child World

The Child World is visual, warm, calm, limited, and easy to understand.

It includes:

- profile selection;
- personal Child Room;
- continue listening;
- story discovery;
- favorites;
- collections and categories;
- audio player;
- synchronized text;
- illustrations;
- ambient sound access;
- safe child-facing cards and prompts.

It must not expose:

- billing;
- email addresses;
- passwords;
- subscription management;
- destructive controls;
- account deletion;
- support forms;
- administrative controls;
- raw technical errors;
- unrestricted external links.

### 7.2 Parent World

The Parent World is clear, practical, protected, and information-rich.

It includes:

- child profile management;
- subscription and trial management;
- offers and plan information;
- notification preferences;
- download management;
- security settings;
- account settings;
- support access;
- privacy and deletion requests;
- child activity summaries where appropriate.

The visual language remains friendly but should not imitate the playful child interface.

---

## 8. Account and Profile Model

The parent account is the authenticated account owner.

A child profile is not an independent unrestricted account. It exists under the parent account and contains child-specific preferences and listening state.

Each child profile may include:

- display name or nickname;
- age band or date of birth where justified;
- avatar;
- room theme;
- favorite animal;
- favorite color;
- interests;
- preferred categories;
- preferred ambient sound;
- favorites;
- history;
- continue-listening state;
- offline downloads;
- accessibility preferences.

Premium supports multiple child profiles. The exact free-profile limit is controlled by the active commercial policy.

Profile deletion must require parent authorization and follow data-retention rules.

---

## 9. Profile Selection

Profile selection should appear after account authentication and on relevant application relaunches.

The experience should feel similar to choosing a personal story room rather than selecting a technical user account.

The screen should prioritize:

- large avatars;
- child names or nicknames;
- minimal text;
- a protected parent entry point;
- no billing or account details.

---

## 10. Child Room

The Child Room is the main child-facing home experience.

It should include:

- personal greeting;
- profile avatar;
- mascot presence;
- continue story;
- story of the day or featured story;
- recommended stories;
- categories;
- collections;
- favorites;
- ambient sound access;
- recently added content where appropriate.

### Time-based atmosphere

The room background adapts to the local time of day:

| Period | Direction |
|---|---|
| Morning | Fresh, soft sunlight, light colors |
| Afternoon | Balanced, playful, clear |
| Evening | Warm, calm, sunset tones |
| Night | Dark blue, stars, moon, reduced brightness |

Time-based backgrounds are part of the initial product experience. They must not cause excessive battery usage or visual distraction.

---

## 11. Mascot

The mascot is a rabbit.

The rabbit should feel:

- calm;
- friendly;
- expressive;
- safe;
- memorable;
- inclusive;
- connected to stories and bedtime.

The final mascot name is a product decision. Candidate names may include Lumi, Nori, Pufi, Luno, Tupi, or Bubu, but no name is canonical until formally selected.

The mascot may serve as:

- onboarding guide;
- story discovery guide;
- notification personality;
- loading and empty-state character;
- brand identity;
- future story character;
- future merchandising identity.

The mascot must not pressure children to purchase, return, maintain streaks, or ask adults for money.

---

## 12. Content Model

Supported content structures include:

- standalone stories;
- series;
- episodes;
- collections;
- seasonal collections;
- bedtime stories;
- educational stories;
- calming stories;
- adventure stories;
- animal stories;
- ambient audio tracks.

Each story should define:

- title;
- description;
- localized metadata;
- audio asset;
- text or transcript;
- illustrations;
- age recommendation;
- categories;
- duration;
- access type;
- publication status;
- series and episode references where applicable;
- content warnings where appropriate;
- language;
- narrator and creator credits;
- synchronization data;
- offline eligibility.

All public content must pass editorial and safety review before publication.

---

## 13. Story Experience

The core experience combines audio, synchronized text, and illustrations.

### MVP synchronization

Segment-level synchronization is sufficient for the MVP. A segment may contain:

- text;
- start time;
- end time;
- optional illustration reference;
- optional speaker or scene metadata.

This enables:

- highlighted text;
- illustration changes;
- resume behavior;
- accessible reading support;
- consistent playback state.

Word-level synchronization may be introduced later when content production and technical validation justify it.

### Player expectations

The player should support:

- play and pause;
- seek with child-safe controls;
- previous and next segment where appropriate;
- continue listening;
- playback progress persistence;
- sleep timer in a later phase or MVP if capacity allows;
- independent ambient-sound volume;
- offline playback for entitled content;
- lock-screen and background controls where supported.

The player must not be cluttered with technical controls.

---

## 14. Discovery and Recommendation

Discovery should be understandable and safe.

Primary discovery mechanisms include:

- categories;
- age bands;
- collections;
- series;
- search;
- favorites;
- recently listened;
- continue listening;
- editorial recommendations;
- time-of-day suggestions.

Recommendations should initially rely on transparent editorial and behavioral rules. Advanced personalization may be introduced later after privacy, quality, and explainability review.

The product must not create filter bubbles that repeatedly expose children to only one narrow content type.

---

## 15. Ambient Sounds

Ambient sounds are a first-class product capability, not decorative background audio.

Potential sounds include:

- white noise;
- rain;
- waves;
- forest;
- night ambience;
- wind;
- heartbeat;
- fireplace;
- birds;
- car;
- train;
- river.

Ambient sounds may be used:

- inside the Child Room;
- during story playback;
- as standalone sleep audio;
- during bedtime preparation.

The child or parent may control story and ambient volume separately.

Audio mixing must avoid sudden volume changes and must respect device audio policies.

---

## 16. Parent Zone

Parent Zone is the protected adult area.

Access requires:

- parent PIN;
- optional device biometrics;
- PIN fallback;
- short-lived parent elevation;
- recent re-authentication for high-risk operations.

Parent Zone may contain:

- profiles;
- subscriptions;
- trial information;
- offers;
- notifications;
- contact and support;
- downloads;
- account settings;
- security settings;
- privacy settings;
- child activity summaries;
- account deletion and export actions.

The application must never rely on a simple swipe, arithmetic puzzle, or hidden button as the primary security boundary.

---

## 17. Free and Premium Model

### 17.1 Free

The intended free experience includes:

- approximately 50 free stories at launch;
- one or a limited number of child profiles;
- core playback capabilities;
- selected ambient sounds;
- controlled advertising;
- limited or no offline access according to active policy.

The free tier must remain useful and trustworthy. It should demonstrate product value without intentionally creating a broken experience.

### 17.2 Premium

Premium includes:

- complete eligible story catalog;
- no advertisements;
- offline downloads;
- multiple profiles;
- premium series and collections;
- full ambient sound access;
- enhanced personalization and future premium capabilities.

### 17.3 Subscription options

Initial options:

- monthly subscription;
- annual subscription;
- three-day trial.

Exact prices, regional availability, trial eligibility, grace periods, and store-specific rules are configuration and commercial policy, not hard-coded product assumptions.

---

## 18. Advertising

Advertising is allowed only for eligible free users.

Core rules:

- never interrupt a story in the middle;
- target a maximum of one advertisement after every two completed listening sessions under the initial policy;
- recommended ad duration is approximately 15 seconds;
- suppress immediately after Premium activation;
- avoid manipulative countdowns or fake controls;
- do not encourage children to click;
- do not use unsafe external links;
- do not use behavioral advertising based on child data;
- do not expose inappropriate categories;
- provide a gentle parent-directed Premium message.

Example:

> Want stories without ads? Ask a parent to open Parent Zone.

The advertising policy must remain configurable and auditable.

---

## 19. Offline Experience

Premium users may download eligible stories for offline use.

Offline capabilities should include:

- resumable downloads;
- download status;
- storage awareness;
- checksum validation;
- protected local storage;
- synchronized progress after reconnection;
- clear handling of expired or revoked entitlements;
- graceful operation without connectivity.

Security-sensitive decisions remain server-authoritative, with only a documented offline grace policy where necessary.

---

## 20. Notifications

Notifications are primarily addressed to the parent account.

Supported categories include:

- security;
- account;
- subscription;
- billing;
- new content;
- bedtime reminders;
- download status;
- service announcements;
- support;
- optional marketing.

Child-facing prompts should remain inside the child experience and must be safe, non-commercial, and non-pressuring.

Examples:

- “A new adventure is waiting.”
- “It is story time.”
- “The bedtime story is ready.”

Parents must be able to configure optional categories and channels. Security or legally required communication may remain mandatory.

---

## 21. Tone of Voice

### 21.1 Child-facing tone

The child-facing voice is:

- simple;
- warm;
- magical;
- encouraging;
- calm;
- concrete.

Examples:

- “Who is listening today?”
- “Shall we continue the story?”
- “Where are we going today?”
- “The characters are waiting.”

Avoid:

- guilt;
- urgency;
- fear;
- complex technical language;
- purchase pressure;
- excessive exclamation marks.

### 21.2 Parent-facing tone

The parent-facing voice is:

- clear;
- practical;
- calm;
- transparent;
- respectful.

Examples:

- “Manage child profiles”
- “Subscription settings”
- “Safety settings”
- “Contact support”

Billing, privacy, security, and deletion text must prioritize clarity over marketing language.

---

## 22. Visual Identity

### Recommended palette direction

- Midnight Blue;
- Warm Cream;
- Golden Yellow;
- Sage Green;
- Soft Lavender;
- Sky Blue;
- Warm Brown.

### Typography direction

- Nunito for general UI;
- Baloo 2 or an approved rounded display typeface for selected titles;
- Atkinson Hyperlegible or another accessibility-focused typeface where long reading requires it.

### Illustration direction

- digital watercolor;
- soft edges;
- pastel colors;
- warm light;
- gentle characters;
- consistent visual language;
- no aggressive shadows;
- no disturbing realism;
- no frightening imagery for young audiences.

Visual decisions must also support contrast, readability, reduced motion, and accessibility.

---

## 23. Safety and Privacy Rules

Children must never be able to:

- purchase subscriptions;
- change billing;
- delete profiles;
- delete accounts;
- contact support independently;
- access invoices;
- change security settings;
- manage advertisements;
- access administrative content;
- communicate with strangers;
- publish public content;
- open unrestricted external links.

The product must avoid:

- unmoderated public content;
- public comments;
- chat;
- location sharing;
- manipulative engagement loops;
- aggressive advertising;
- raw system errors;
- unnecessary collection of child data;
- personalized advertising based on child behavior.

Child names, raw tokens, PINs, sensitive account data, and unnecessary personal information must not appear in operational logs or analytics.

---

## 24. Accessibility

Accessibility is part of product quality, not a later add-on.

The product should support:

- large touch targets;
- readable typography;
- strong contrast;
- screen-reader labels for parent flows;
- reduced-motion preferences;
- predictable navigation;
- captions or transcripts where available;
- audio-first use;
- minimal reliance on color alone;
- understandable error recovery.

Child flows should be tested with limited reading ability and motor precision in mind.

---

## 25. Error and Empty-State Experience

Child-facing errors should be calm and actionable.

Examples:

- “This story needs the internet right now.”
- “We could not start the story. Let us try again.”
- “This download is not ready yet.”

Errors must not reveal technical details, identifiers, stack traces, provider names, or security information.

Empty states should guide the next safe action without pressure.

---

## 26. Support Experience

Support is parent-facing and accessible from Parent Zone.

Support should cover:

- account access;
- billing and subscription questions;
- playback problems;
- download problems;
- content concerns;
- privacy requests;
- account deletion;
- safety reports.

Support records must be auditable and must minimize child-related personal data.

---

## 27. Admin and Editorial Experience

The administrative dashboard supports approved staff, not children or normal parent users.

It should enable:

- content creation and editing;
- story, series, and episode management;
- upload and processing workflows;
- metadata and age recommendation management;
- review and approval;
- publication and scheduling;
- archive and correction;
- collection management;
- notification and campaign management;
- support workflows;
- audit access according to role.

High-risk administrative actions require explicit authorization, reason capture, and audit logging.

---

## 28. MVP Product Scope

The MVP is expected to include:

- parent account registration and authentication;
- child profiles;
- profile selection;
- Child Room;
- time-based backgrounds;
- story catalog;
- story details;
- audio playback;
- segment-synchronized text;
- illustrations;
- favorites;
- continue listening;
- series and episodes;
- categories and collections;
- Parent Zone;
- free and Premium entitlement rules;
- approximately 50 free stories;
- three-day trial;
- monthly and annual Premium options;
- controlled advertisements for free users;
- offline downloads for Premium;
- notifications;
- contact and support;
- administrative content workflow.

MVP scope may be reduced only through an explicit product decision that records impact and follow-up.

---

## 29. Non-Goals for MVP

The following are not MVP goals:

- social networking;
- user-to-user chat;
- public comments;
- public user-generated content;
- livestreaming;
- video-first content;
- open creator marketplace;
- complex creator payouts;
- production AI-generated stories without editorial control;
- heavy gamification;
- child accounts independent of a parent;
- unrestricted web browsing;
- real-time multiplayer experiences.

---

## 30. Future Product Directions

Potential future capabilities include:

- multilingual content;
- author and creator dashboards;
- personalized stories with strict parent controls;
- AI-assisted editorial tools;
- educational journeys;
- kindergarten or school accounts;
- advanced recommendations;
- richer mascot animation;
- evolving Child Rooms;
- bedtime routines;
- breathing and relaxation exercises;
- family sharing;
- accessibility-focused content modes;
- creator collaboration workflows.

Future ideas remain hypotheses until validated through research, safety review, commercial analysis, and architecture review.

---

## 31. Product Decision Checklist

Before approving a feature, confirm:

1. Does it improve the child or parent experience?
2. Is it safe for children aged 0-7?
3. Can a child reach an adult-only action?
4. Does it collect more data than necessary?
5. Is the commercial behavior transparent?
6. Does it preserve calm and clarity?
7. Is the feature understandable without instructions?
8. Does it work with multiple profiles?
9. Does it behave correctly offline or during partial failure?
10. Is the feature accessible?
11. Is it observable and supportable?
12. Does it have a clear owner and success measure?

A feature that fails safety, privacy, or parent-control checks must not ship.

---

## 32. Canonical Decisions

The following decisions are currently canonical:

- target child audience: ages 0-7;
- authenticated principal: parent account;
- child profiles exist under the parent account;
- mobile platforms: iOS and Android;
- shared mobile implementation: Flutter;
- mascot: rabbit;
- free catalog target: approximately 50 stories;
- Premium options: monthly and annual;
- trial: three days;
- free advertising policy: approximately one ad after every two completed listening sessions;
- advertisements never interrupt stories;
- offline downloads: Premium;
- multiple profiles: Premium;
- child experience and Parent Zone are strictly separated;
- Parent Zone uses PIN with optional biometrics;
- notifications are persisted and configurable;
- product values: safety, curiosity, adventure, calm, and attention.

---

## 33. Related Documents

- `README.md`
- `Project_Charter.md`
- `Project_Goals.md`
- `Definition_of_Done.md`
- `ADR/README.md`
- `../03_Architecture/Software_Architecture.md`
- `../03_Architecture/Mobile_Architecture.md`
- `../03_Architecture/Security_Architecture.md`
- `../03_Architecture/Notifications.md`
- `../03_Architecture/Admin_Dashboard.md`

---

## 34. Maintenance Rules

This document must be reviewed when:

- the target audience changes;
- pricing or tier structure changes materially;
- the advertising policy changes;
- a new user type is introduced;
- child safety rules change;
- the Parent Zone model changes;
- a major content type is introduced;
- product positioning changes;
- a future idea becomes committed scope.

Changes must preserve a clear distinction between validated decisions, current scope, and future hypotheses.