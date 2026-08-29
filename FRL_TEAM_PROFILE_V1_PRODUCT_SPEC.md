# Football Research Laboratory — Team Profile V1 Product Specification

**Status:** Active implementation specification  
**Created:** 29 August 2026  
**Depends on:** `FRL_INTERFACE_DESIGN_PRINCIPLES_V2.md`, `FRL_SHORT_TERM_PRODUCT_ROADMAP.md`, governed FRL query/identity/URA layers

## 1. Objective

Build the first Team Profile workspace as a beautiful, fast, navigable football season record.

The Team Profile is not a compressed Team Stats page. Its primary job is to answer:

> **Who was this team in this season, what defined their season, and where can I go next?**

The profile should feel like a modern football record book inside one continuous FRL application: editorial, playful, colourful in a controlled way, data-backed, and immediately understandable.

The subject and context stay fixed while the view changes.

Canonical interaction model:

```text
ARSENAL                                      2024–25 ▾
Premier League

Overview     Records     XI     Fixtures     Stats
────────

[ current view ]
```

The workspace should favour fast tab/view transitions over vertically stacking every available section.

---

## 2. Definition of done

Team Profile V1 is complete when:

1. a canonical team-season can be opened through the active Next.js product;
2. team identity, competition and season context remain persistent across views;
3. the primary navigation is `Overview`, `Records`, `XI`, `Fixtures`, `Stats`;
4. changing views feels immediate and does not require a full browser refresh;
5. the selected view is represented in the URL so refresh, linking and browser Back/Forward work sensibly;
6. a normal desktop view is designed to fit substantially within the available viewport where practical;
7. long content such as fixture lists or deep tables scrolls within the relevant view rather than forcing one giant page;
8. Overview communicates the season in seconds rather than presenting a metric wall;
9. Records supports a rich catalogue of interesting season records through secondary categories without cramming them all together;
10. XI presents a clearly labelled, evidence-backed Most Played XI as a football-native visual;
11. Fixtures provides a polished compact season-results record with canonical links into Fixture Workspace;
12. Stats establishes the analytical shell and visual language for later Team Stats expansion without dumping the whole variable inventory into V1;
13. all data is sourced through governed FRL Python/API seams, not browser-side source-file access;
14. missing or uncertain evidence fails gracefully and is never fabricated;
15. the page looks and behaves like FRL, not a generic dashboard.

---

## 3. Workspace shell and persistent context

The Team Profile should retain a stable top region containing:

- canonical team display name;
- competition context;
- season selector;
- primary profile navigation;
- optional compact team identity mark/monogram only if it materially improves the design and is evidence-safe.

Changing season should retain the current conceptual view where practical. For example, switching from Arsenal 2024–25 `Records` to Arsenal 2023–24 should remain on `Records` unless that view is genuinely unavailable.

Changing primary tabs must not make the user feel that they have left the Team workspace.

The active tab should be visually clear but restrained. The navigation should read as part of the page architecture rather than a row of large buttons.

Recommended URL semantics may use a path or query representation such as:

```text
/teams/{team}/{season}?view=overview
/teams/{team}/{season}?view=records
/teams/{team}/{season}?view=xi
```

The exact route shape may follow existing Next.js conventions, but the selected view must be linkable and restorable.

---

## 4. Viewport and density rules

The Team Profile must implement the V2 viewport-first rule.

The default desktop experience should not become:

```text
header
metrics
chart
records
XI
fixtures
stats
more charts
```

Each primary tab is one coherent task.

The persistent header/navigation should consume as little height as possible while remaining clear.

Where a view needs overflow:

- fixture lists may scroll within their content region;
- long analytical tables may scroll within their content region;
- secondary record categories should switch content rather than stack;
- avoid adding sections below the fold merely because space exists in the data model.

The user should normally be able to understand the purpose and core information of the selected view without scrolling the entire document.

---

## 5. Overview — the season in five seconds

### Product purpose

Overview should answer:

> **How did this team’s season go?**

It should be the calmest Team Profile view.

### Core information

Where governed evidence supports it, prioritise:

- final/current league position;
- points;
- played / W-D-L record;
- goals for and goals against or goal difference;
- compact recent/current form;
- leading scorer;
- most appearances / most minutes / most starts, choosing the clearest governed record;
- one additional meaningful season hook such as clean sheets, longest unbeaten run, or another record supported by evidence.

Do not turn every number into a separate decorated card.

### Visual centrepiece

Overview should contain one meaningful season-shape visual rather than multiple graphs.

Preferred candidates, in order of product usefulness:

1. **league-position trajectory** across the season, where correct historical table reconstruction supports it;
2. **season results/form ribbon** showing W/D/L sequence with hover/click fixture context;
3. another compact season trajectory only where it communicates a clear story and remains evidence-safe.

The visual must use native FRL typography, colours, tooltips and surfaces.

### Overview record teasers

The Overview may surface a small number of human-interest hooks that lead into Records, for example:

```text
Season best
16 matches unbeaten  → Records
```

This is a teaser, not a second Records page.

### Explicit exclusions

Do not place large analytical metric tables, advanced possession/passing/shot breakdowns, the full XI, or the full fixture list on Overview.

---

## 6. Records — a rich season record book without cramming

### Product purpose

Records should be one of the most distinctive and enjoyable Team Profile views.

The system may know or derive many records. The design constraint is not the total number of records available; the constraint is how many are visible at once.

Core principle:

> **FRL can contain a lot without showing a lot at once.**

Use secondary record categories inside the Records view.

Recommended V1 navigation:

```text
Results     Runs & streaks     Goals     Players     Matchday
```

Secondary categories should change the Records panel in-place, preserve the Team Profile shell and feel instantaneous.

### 6.1 Results

Candidate records where safely derivable include:

- biggest win;
- biggest defeat;
- biggest home win;
- biggest away win;
- highest-scoring match;
- most common winning scoreline;
- most common draw scoreline;
- most common losing scoreline;
- longest sequence without a draw;
- longest sequence without a defeat;
- longest sequence without a win;
- home/away record highlights where meaningful.

Records should include fixture/opponent/date context where available, with the fixture navigable into Fixture Workspace.

### 6.2 Runs & streaks

Candidate records include:

- longest winning streak;
- longest unbeaten streak;
- longest losing streak;
- longest winless streak;
- longest scoring streak;
- longest goalless streak;
- longest clean-sheet streak;
- longest conceding streak;
- current winning/unbeaten/scoring/clean-sheet streaks where the selected season/current cutoff makes the concept meaningful;
- best home unbeaten/winning run;
- best away unbeaten/winning run.

A compact result sequence may be used to make runs tangible, for example:

```text
W  W  W  D  W  W  W
```

The sequence should be interactive where feasible, exposing fixture context rather than functioning as decoration.

### 6.3 Goals

Candidate records include:

- most goals scored in a match;
- most goals conceded in a match;
- total goals scored;
- total goals conceded;
- clean sheets;
- matches scoring 2+ / 3+ / 4+ goals;
- matches conceding 0 / 1 / 2+ goals;
- best scoring month/period where the grouping is well defined;
- best defensive month/period;
- earliest/latest goals only where event evidence and semantics are sufficiently governed;
- longest scoring / clean-sheet runs may be cross-linked from Runs & streaks rather than duplicated heavily.

### 6.4 Players

Candidate season records include:

- top scorer;
- most assists where governed and comparable;
- most appearances;
- most starts;
- most minutes;
- most-used substitute;
- goalkeeper with most appearances/starts;
- player involved in most wins only if the derivation is defined carefully;
- other player-season records selected from the governed capability inventory as their semantics become established.

Do not invent captain, injury, availability or squad-history records unless those relationships are genuinely supported.

Player names should become navigable into Player Profile as that surface becomes available.

### 6.5 Matchday

Candidate records include:

- highest attendance;
- lowest attendance where coverage makes comparison legitimate;
- highest-scoring fixture;
- fixture with most cards where event evidence supports it;
- most frequent venue/ground context only if meaningful;
- latest/earliest decisive event only where event semantics are safe;
- other match-centre records supported by governed fixture/event evidence.

Attendance records must respect partial/missing attendance coverage and must not imply completeness when it is not established.

### Records presentation rules

Records should look editorial, not like a KPI-card grid.

Use strong typography, scorelines, dates, opponents, compact sequences, subtle colour, and meaningful whitespace.

Prefer 4–8 strong records visible in one category at a time over a wall of 25 tiles.

Where a category contains more useful records, use compact internal navigation, pagination, horizontal transition, or another progressive-disclosure pattern rather than growing the page indefinitely.

---

## 7. XI — Most Played XI

### Product purpose

The XI view should answer:

> **Which players most defined this team’s season on the pitch?**

It should be highly visual and football-native.

### Evidence basis

The Most Played XI must be explicitly derived from governed player participation evidence.

Possible ranking basis:

1. starts, where starting-status coverage is reliable;
2. minutes, where minutes provide the more complete and comparable basis;
3. appearances only where starts/minutes are unavailable or unsuitable.

The chosen rule must be explicit in the UI, for example:

```text
Most Played XI
By starts · Premier League 2024–25
```

### Formation/layout

Do not imply that the Most Played XI was a real tactical XI used together unless that claim has separately been established.

The view may use a presentation formation to arrange the selected players, but the derivation must remain clear.

Where source-backed position/formation evidence allows a sensible deterministic arrangement, use it. Otherwise favour a clearly labelled presentation layout rather than tactical guesswork.

### Interaction

The pitch should dominate the view.

Each player may expose on hover/focus:

- starts;
- appearances;
- minutes;
- goals/assists where established and useful;
- primary position where governed.

Do not clutter every player node with all of this information simultaneously.

Player nodes should eventually be navigable to Player Profile.

### Supporting content

A compact bench/next-most-used group may be included only if it fits comfortably and improves the story. Avoid placing a giant player table beneath the pitch.

---

## 8. Fixtures — the season record

### Product purpose

Fixtures should present the team’s match history as a beautifully designed football record.

This view may legitimately contain a long list; it should therefore use a contained scrolling region where practical while retaining the Team Profile header and primary tabs.

### Core row information

Prefer:

- date;
- opponent;
- home/away;
- score;
- result;
- optional competition/gameweek context if necessary.

The opponent and score should be the strongest information. Date and venue/home-away state should be quieter.

Group by month or another natural chronological marker where it improves scanning.

Every resolvable historical fixture should link into the existing canonical Fixture Workspace.

### Interaction

Use subtle row hover/selection states. Avoid turning every row into a card.

Filtering may be added later if it earns its place; V1 should prioritise the clean season record over a control-heavy fixture explorer inside the profile.

---

## 9. Stats — analytical gateway, not a dump

### Product purpose

Stats is the transition from Profile to deeper Team research.

The Team Profile `Stats` tab may either host the initial analytical surface directly or route into a dedicated Team Stats workspace while preserving team/season context.

Preferred conceptual sub-navigation:

```text
Overview     Attack     Possession     Passing     Defence     Discipline
```

Exact categories must be informed by the governed Variable Capability Inventory rather than by familiarity with other football websites.

### V1 density

Each analytical sub-view should generally favour:

- one primary chart or visual question;
- one compact supporting table/ranking block;
- concise context/interpretation;
- optional deeper navigation.

Do not stack many charts simply to demonstrate capability.

### Native visual language

Charts and tables must obey `FRL_INTERFACE_DESIGN_PRINCIPLES_V2.md`:

- native warm-light surfaces;
- FRL typography;
- controlled coral/olive/charcoal palette;
- subtle grid/separators;
- direct labels where useful;
- no generic plotting-library appearance;
- no raw dataframe rendering;
- responsive sizing within the viewport-first workspace.

---

## 10. Colour, typography and visual personality

The Team Profile should use the active FRL warm-light identity rather than older dark-dashboard guidance.

The design should feel colourful enough to have personality without becoming multicoloured decoration.

Use:

- warm parchment/off-white background;
- creamy/native surfaces;
- near-black/charcoal primary text;
- coral/orange as the primary accent;
- olive/green as a secondary accent;
- restrained result semantics for wins/draws/losses;
- dark sidebar/navigation contrast where already established.

Typography should provide much of the visual hierarchy:

- confident team name;
- quiet competition/season context;
- compact uppercase category labels;
- strong tabular record numbers;
- elegant scorelines;
- native chart/table labels.

Avoid repetitive boxed metric cards, giant hero sections, rainbow record tiles, gradients/glows, or decorative football imagery unrelated to evidence.

---

## 11. Seamless interaction requirements

Primary and secondary view switching should feel like one application.

Where technically sensible:

- use Next.js/client-side navigation rather than document reloads;
- preserve already known team/season context;
- maintain useful cached data safely;
- use subtle 100–180ms-class visual transitions rather than theatrical animation;
- ensure keyboard/focus states remain usable;
- ensure URL state reflects selected views;
- preserve browser Back/Forward semantics.

A user should be able to move conceptually through:

```text
Team Profile → XI → Player Profile → Matches → Fixture Workspace
```

without feeling that FRL has become a collection of unrelated sites.

---

## 12. Data and research rules

The interface is downstream of governed FRL evidence.

Do not:

- read source CSV/JSON files directly in the browser;
- create a second team identity universe;
- calculate authoritative football semantics independently in TypeScript when they belong in Python/query layers;
- fabricate unavailable records to fill the design;
- assume missing values are zero;
- imply that a partial attendance/event/player source is complete;
- present presentation-only formation/layout decisions as source evidence;
- allow final-season evidence to leak into historical/as-of views where the user has requested an earlier information cutoff.

Derived records must have explicit definitions in code and be reproducible from governed inputs.

The record system should be designed so new safe record definitions can be added without redesigning the Records page.

---

## 13. Recommended implementation order

Implement the Team Profile incrementally rather than building all five views simultaneously.

### Phase A — workspace shell + Overview

- canonical team-season route;
- persistent header/season context;
- primary tab navigation;
- URL-addressable view state;
- Overview record/season summary;
- one integrated season visual;
- Arsenal primary canary.

**Review visually before proceeding.**

### Phase B — Records framework

- secondary record-category navigation;
- governed record derivation contract;
- initial Results / Runs & streaks / Goals / Players / Matchday categories;
- record-to-fixture/player navigation where supported.

**Review visually before expanding record count.**

### Phase C — XI

- derive Most Played XI through governed participation evidence;
- pitch presentation;
- player hover/focus details;
- player navigation seam.

### Phase D — Fixtures

- compact chronological fixture record;
- contained scroll behaviour;
- canonical fixture deep links.

### Phase E — Stats gateway

- establish Team Stats tab/sub-navigation;
- use Variable Capability Inventory to choose supported analytical groups;
- implement one polished analytical view first before broad expansion.

This sequence is intentionally visual/product-led. Do not wait until every backend capability is perfect before reviewing the interface, and do not build every possible record/stat before the interaction model has been validated.

---

## 14. Primary visual canaries

Use at least:

- **Arsenal** as the primary design canary;
- one contrasting team-season with a materially different record/performance profile;
- one season with partial/missing optional evidence where useful to verify graceful degradation.

A design that only looks good for one high-performing club is not universal enough.

---

## 15. Acceptance test

Before accepting Team Profile V1, ask:

1. Can I identify the team, competition and season immediately?
2. Do the five primary views feel like views of one workspace rather than separate webpages?
3. Does Overview tell the season story in seconds?
4. Is Records rich without becoming crowded?
5. Are record categories imaginative enough to make historical exploration enjoyable?
6. Does XI feel like a football visual rather than a table placed on a pitch background?
7. Can I reach any displayed fixture through the canonical Fixture Workspace?
8. Does the Stats view feel analytical without overwhelming the profile?
9. Do charts and tables look native to FRL?
10. Does the selected desktop view fit comfortably in the available viewport where practical?
11. Does required overflow happen inside the relevant content region rather than creating an enormous page?
12. Does season/view navigation preserve context and feel immediate?
13. Are player/team/fixture entities treated as navigable research objects?
14. Are missing, partial and derived evidence states honest?
15. Is there anything visible merely because the data exists rather than because it improves the current view?

If the answer to 15 is yes, remove or move it behind navigation.

---

## 16. Product rule

The governing Team Profile rule is:

> **Show the season as a football story first, a record book second, and an analytical dataset only when the user deliberately asks for Stats. Keep the team and season stable, let the view change around them, and make richness discoverable rather than overwhelming.**
