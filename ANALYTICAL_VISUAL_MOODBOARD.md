# Football Research Laboratory — Analytical Visual Moodboard

## Status

**Living reference document.**

This document records visual, analytical and product ideas that should inform future FRL design and modelling work.

It is **not** a fixed UI specification and does not require FRL to reproduce the referenced products or graphics literally.

The purpose is to preserve the analytical concepts, visual grammar and interaction ideas that feel appropriate for the Football Research Laboratory as it develops.

Future design and modelling iterations should read this document alongside:

- `PROJECT_ORIENTATION.md`
- `CURRENT_WORK.md`
- `DATA_CONSTRUCTION.md`
- `UI_DESIGN_SYSTEM.md`
- `AGENTS.md`

---

# 1. Core principle

FRL should increasingly move beyond displaying football statistics toward helping a researcher understand:

> **what happened → where it happened → how it happened → how unusual it was → why it may have happened → how it compares → what might happen next.**

The visualisation should therefore be an **analytical object**, not decoration.

A good FRL visual should normally answer a recognisable football question.

Examples:

- How does this team progress the ball?
- Where does this player receive and distribute possession?
- How territorially dominant is this team?
- What kind of pressing team is this?
- Where has a player's behaviour changed from last season?
- Is a player unusually productive given the risk they take?
- What distinguishes this player's style from positional peers?
- How does a particular XI alter the characteristics of the team?

The information itself should become the design.

---

# 2. General visual philosophy

The strongest references share several characteristics.

## 2.1 Football questions before charts

Do not begin with:

> "We have metric X, so let's make a chart for metric X."

Prefer:

> "We want to understand how Arsenal create territorial dominance. What evidence and visual form best answer that question?"

Derived football concepts are often more valuable than raw-stat dumping.

---

## 2.2 Context is part of the metric

A number without an appropriate comparison population is often incomplete.

FRL visualisations should expose relevant context such as:

- league
- season
- position
- role
- age cohort where appropriate
- minutes threshold
- match state
- home / away
- previous season
- league average
- selected comparison team/player

Percentiles and rankings should always be interpreted against a governed population.

---

## 2.3 Volume, efficiency and context belong together

Avoid presenting success percentages or rates in isolation.

For example:

- defensive duel success + duel volume
- pass completion + pass difficulty/value
- pressing success + pressing frequency
- finishing + shot quality
- progression value + possession volume

A player with low duel volume and very high duel success may tell a different football story from a player with equally high success at enormous volume.

FRL should make those relationships visible.

---

## 2.4 Show patterns and exact evidence

A recurring useful layout is:

**visual pattern + exact values + comparison context**

For example:

- radar/profile on one side
- governed values and percentiles alongside

The visual supports rapid pattern recognition.

The exact values preserve auditability.

FRL should try to provide both rather than forcing one representation to perform both jobs.

---

# 3. Spatial football analytics

Spatial analysis should become a major part of FRL if upstream evidence permits it.

The current platform should not pretend spatial evidence exists where it does not.

A dedicated upstream PulseLive/Opta capability audit should establish what coordinate and event-sequence information can legitimately be recovered.

Priority spatial objects include:

## Pass maps

Show:

- pass origins
- destinations
- completion
- progressive passes
- key passes
- passes into selected zones
- player or team filters

Pass maps answer questions that aggregate passing totals cannot.

---

## Shot maps

Show where attempts occur and, where evidence allows:

- outcome
- xG
- body part
- assist type
- shot type
- match state
- player
- opposition
- time

Shot maps should become a core FRL primitive across:

- Match
- Team
- Player

---

## Touch / action maps

Spatial distributions of:

- touches
- receptions
- defensive actions
- recoveries
- carries
- entries
- possession events

can expose behaviour and role in ways conventional tables cannot.

---

## Zonal maps

Do not assume continuous heatmaps are always superior.

A governed pitch-zone representation can sometimes be clearer and more statistically honest.

Useful applications include:

- touch concentration
- progressive actions
- penalty-area entries
- defensive activity
- changes between periods
- team vs league comparison

---

## Difference maps

A particularly valuable visual family.

Rather than only showing current state, FRL should be able to show **change**.

Examples:

- this season vs last season
- player vs positional average
- home vs away
- first half vs second half of season
- before vs after managerial change
- team vs league
- player before vs after role change

The Opta-style zonal touch difference graphic is a strong conceptual reference.

---

# 4. Passing networks and team structure

Passing networks should become a major Team and Match analytical object if the source evidence permits them.

Useful encodings include:

- player/position average location
- node size = involvement/pass volume
- line thickness = passing frequency
- line direction where meaningful
- line colour/value = progression or another governed concept
- formation context

The network should help answer:

> **How does this team actually circulate and progress possession?**

Important analytical consideration:

A full 90-minute aggregation may become misleading after substitutions or formation changes.

Possible future approaches include:

- most-used tactical period
- starting XI period
- formation-specific periods
- selectable match intervals
- season-average network
- individual-match network

Position-aware aggregation may sometimes be more meaningful than treating every substituted player as an independent tactical node.

References:

- Ben Griffis
- Markstats / Markstatsbot

---

# 5. Field tilt and territorial dominance

**Field tilt is a priority desired analytical concept.**

FRL should investigate whether available event/spatial evidence allows a governed field-tilt definition to be constructed.

It may not exist as a source variable.

It may instead be derived from a suitable definition such as territorial possession or attacking-third actions.

Any FRL implementation must document:

- numerator
- denominator
- spatial boundary
- event types used
- possession assumptions
- exclusions
- limitations

Related territorial concepts may include:

- final-third share
- penalty-area entries
- territory gained
- territorial possession
- average defensive line/action height
- attacking-half touches
- opposition-half passing share

---

# 6. Pressing and defensive behaviour

The FC_Mossman pressing-efficiency work is a strong conceptual reference.

Rather than presenting isolated pressing totals, FRL should ask football questions such as:

- How frequently does the team press?
- How often does pressure produce a turnover?
- How often do those turnovers become shots?
- Where do turnovers occur?
- How quickly is possession converted into threat?

A useful visual grammar is an annotated scatter:

- x-axis = pressing/turnover behaviour
- y-axis = downstream effectiveness
- point size = pressing volume
- annotations = interpretable football archetypes

Example conceptual quadrants:

- generally ineffective press
- frequently forces turnovers
- turnovers frequently produce shots
- high-frequency/high-return pressing

This is a strong example of:

> **derived concepts > raw-stat dumping**

Upstream evidence requirements may include:

- ordered events
- timestamps
- possession/sequence identity
- pressure/turnover events
- spatial coordinates
- shot linkage

---

# 7. Scatterplots as analytical maps

Scatterplots are particularly useful when each axis describes a meaningful football trade-off.

Do not restrict FRL to leaderboards.

Useful examples:

- risk vs reward
- volume vs efficiency
- possession share vs progression
- press frequency vs press effectiveness
- defensive activity vs success
- shot volume vs shot quality
- crossing frequency vs crossing effectiveness
- directness vs territorial gain

The objective is often to expose:

- clusters
- archetypes
- outliers
- trade-offs
- unexpected performers

Annotations should translate statistical regions into football language where defensible.

---

# 8. Expected performance and residual analysis

FRL should eventually support visualisations that show **deviation from expectation**, not merely raw values.

Examples:

- expected vs actual finishing
- expected vs actual progression
- chance creation relative to possession
- defensive output relative to exposure
- pressing outcome relative to pressing volume
- possession value relative to pass risk

Residual-type analysis can answer:

> **Who is producing more or less than we would expect given the conditions under which they operate?**

This is a natural bridge between descriptive analytics and FRL's future modelling layer.

Reference:

- Ben Griffis discussion of SkillCorner EPV
- SkillCorner Passing Risk–Reward Profile

---

# 9. Possession value

SkillCorner's Expected Possession Value work is a useful conceptual reference.

The important idea is not necessarily the exact proprietary implementation.

The useful analytical concept is:

> an action can be evaluated according to how it changes the future attacking value of the possession.

This allows distinctions between:

- safe recyclers
- high-risk creators
- high-volume progressors
- selective high-value passers
- players producing less value than expected for their risk

FRL may eventually construct or evaluate its own governed possession-value models if the event evidence is sufficiently rich.

Do not reproduce proprietary definitions without evidence.

---

# 10. Player analytical profiles

## 10.1 Avoid one universal player radar

Player visualisation should be **role-aware**.

A centre-back should not be evaluated through exactly the same analytical vocabulary as a winger.

Potential families include:

- centre-back
- full-back / wing-back
- defensive midfielder
- central midfielder
- attacking midfielder
- winger
- striker

Longer term, FRL may use derived role clusters rather than relying only on nominal positions.

---

## 10.2 General profile + specialist views

A strong player architecture may eventually resemble:

**Overview → role profile → specialist analytical views**

Specialist views could include:

- Passing
- Progression
- Creation
- Shooting
- Carrying
- Defending
- Aerial
- Possession
- Spatial
- Form / change

The FC_Mossman multi-template approach is a useful conceptual reference.

---

## 10.3 Percentile profiles

Percentile/radar-type graphics remain useful when:

- the peer population is explicit
- metrics suit the player's role
- minimum sample rules are governed
- higher does not automatically imply better where the metric represents style
- exact values remain inspectable

The visual should answer:

> **What is the shape of this player?**

rather than pretend to be a definitive player rating.

References:

- FC_Mossman
- Ted Knutson / StatsBomb-style player templates
- Gradient Sports

---

# 11. Performance vs style

FRL should distinguish two different analytical questions:

> **How good is this team/player?**

and

> **How does this team/player play?**

These are not the same thing.

A style metric may have no inherent "better" direction.

Examples of style dimensions:

- possession
- directness
- crossing
- progression route
- pressing tendency
- defensive height
- goalkeeper involvement
- build-up preference
- width
- transition frequency

A team/player style fingerprint should therefore not automatically be presented as a performance score.

Ben Griffis's league/team style profiles are a useful conceptual reference.

---

# 12. Team style fingerprint

A future Team Profile should be able to answer:

> **What kind of football does this team play?**

A team style fingerprint might combine governed dimensions covering:

- possession
- progression
- creativity
- width/crossing
- directness
- set pieces
- pressing
- defensive behaviour
- goalkeeper build-up
- transition play

Useful comparison modes:

- current team vs Premier League
- current season vs previous season
- team vs selected opponent
- team vs manager-era baseline

The exact visual form remains open.

Radial profiles are one option but should not be adopted automatically.

---

# 13. Shape of the Season

The existing FRL **Shape of the Season** visual is explicitly worth preserving.

It succeeds because it shows the rhythm of a season at a glance rather than merely repeating totals.

It communicates:

- sequences
- momentum
- interruptions
- winning/losing spells
- overall season texture

This should remain a recognisable Team Profile object and can evolve rather than be discarded.

Potential future extensions could include optional overlays such as:

- opposition strength
- xG result
- expected points
- home/away
- manager/tactical periods

Any extension should preserve the visual's current simplicity.

---

# 14. Match and player pitch-map interface language

The Sofascore example suggests a useful product pattern:

**one governed pitch canvas with selectable analytical layers**

For example:

- SHOTS
- PASSES
- CARRIES
- DEFENSIVE ACTIONS

with secondary filters such as:

- all
- successful
- unsuccessful
- progressive
- key
- into final third
- into penalty area

FRL should prefer reusable analytical canvases where sensible rather than creating an unrelated card for every metric.

---

# 15. Tactics Board / Lineup Lab

This is a strong long-term product ambition.

The current Team Profile includes an `XI` section.

That section should eventually have room to become a genuine:

# **Lineup / Tactics Lab**

rather than simply displaying a static most-used XI.

Potential capabilities:

- choose formation
- drag/select players into positions
- swap players from the squad
- create custom XI
- save/compare combinations
- compare current vs alternative XI
- inspect role fit
- inspect player analytical profiles from the board
- create a "shadow team"
- construct hypothetical recruitment lineups

References:

- Soccermatics / Earpiece shadow-team interface
- Daniel Evans football-management-game work

---

# 16. Team ratings from selected lineups

Once FRL has created governed player rating/model outputs, the Lineup Lab could recalculate team characteristics for selected combinations.

Potential outputs might include:

- overall model rating
- build-up
- progression
- chance creation
- finishing
- pressing
- defensive resistance
- aerial strength
- width
- transition threat

Important:

Do **not** invent Football Manager-style chemistry or synergy values merely because they are entertaining.

Combination effects should only be introduced where FRL has analytical/model evidence supporting:

- role fit
- positional balance
- interactions
- complementary characteristics

Until then, team outputs should aggregate only properties FRL can defend.

---

# 17. Interactive football structures

A broader product principle from Earpiece and Daniel Evans:

> **Do not only visualise football data. Where appropriate, let the researcher manipulate football structures with it.**

Examples:

- tactical boards
- custom XI
- player replacements
- shadow squads
- role selection
- formation changes
- comparison lineups
- recruitment scenarios

FRL should increasingly feel like an analytical laboratory rather than a collection of reports.

---

# 18. Team Profile implications

The existing Team Profile contains useful structure but also duplication and low-value information.

Current useful navigation:

- Overview
- Records
- XI
- Fixtures & Results
- Form

This conceptual structure should survive, but the navigation should become more fully integrated into the new FRL interface language.

The Overview should avoid repeating obvious aggregate information across multiple blocks.

Examples of low-value duplication include repeatedly surfacing:

- points
- record
- goals
- league finish
- recent results

where the same information already exists elsewhere.

The Team Profile should increasingly prioritise analytical questions over dashboard statistics.

Possible future overview objects include:

- Shape of the Season
- team identity/style fingerprint
- territorial dominance / field tilt
- attacking profile
- defensive/pressing profile
- progression/build-up
- shot profile
- league-relative analytical scatter
- recent tactical changes

Not all should necessarily appear simultaneously.

Composition and hierarchy matter more than quantity.

---

# 19. Visual presentation principles

FRL's established visual direction remains:

- warm/light global FRL chrome
- near-black analytical workspaces
- warm-white typography
- restrained muted colours
- FRL orange/red for interaction and emphasis
- minimal ornamental interface furniture
- no generic dashboard-card aesthetic
- no unnecessary gradients/glows/shadows
- precise typography and spacing
- information density without visual noise

Analytical graphics do not all need to use identical colours or forms.

They should, however, feel like members of the same FRL visual system.

---

# 20. Reference accounts / products

The following accounts/products formed the initial moodboard.

This list should grow over time.

## FC_Mossman / Spencer Mossman

Useful references for:

- player percentile templates
- role-specific profiles
- pressing efficiency
- multidimensional scatterplots
- peer-group comparison
- football-language interpretation

Handle:

`@fc_mossman`

---

## Gradient Sports

Useful references for:

- strong player identity
- highly legible grading
- positional benchmarking
- simple bar-based comparison
- delta-to-average presentation

Handle:

`@Gradient_Sports`

---

## Ted Knutson / mixedknuts

Useful references for:

- role-specific player radar templates
- recruitment-oriented visual analysis
- exact value + percentile pairing
- football role interpretation

Handle:

`@mixedknuts`

---

## StatsBomb visual tradition

Useful references for:

- position-specific player templates
- radar/profile grammar
- metric contextualisation
- recruitment analytics

Use principles rather than copying legacy presentation.

---

## Sofascore

Useful references for:

- pass maps
- shot maps
- dribble maps
- defensive-action maps
- one pitch with multiple selectable analytical layers

Handle:

`@Sofascore`

---

## Ben Griffis

One of the strongest references for FRL.

Useful work includes:

- passing networks
- average positions
- progression encoding
- formation-aware analysis
- league/team style fingerprints
- analytical scatterplots
- residual/model interpretation

Handle:

`@BeGriffis`

---

## SkillCorner

Useful references for:

- Expected Possession Value
- passing risk vs reward
- model-based player archetypes
- off-ball/spatial analytics
- multidimensional football modelling

Handle:

`@SkillCorner`

---

## Opta Analyst

Useful references for:

- spatial difference maps
- zonal comparison
- season-vs-season change
- clearly communicated spatial analysis

---

## Soccermatics / David Sumpter

Useful references for:

- translating football analysis into usable tools
- shadow teams
- interactive squad structures
- researcher-driven workflows

Handle:

`@Soccermatics`

---

## Earpiece

Useful references for:

- shortlist → shadow XI
- pitch-based squad manipulation
- recruitment workflows
- football-native interaction design

---

## Daniel Evans

Useful references for:

- Football Manager-style information density
- player attribute/profile presentation
- interactive football-management environments
- tactics-board thinking
- systems connecting players, tactics and analysis

Handle:

`@DEvansData`

---

## Markstats / Markstatsbot

Particularly relevant references for:

- passing networks
- average positions
- field tilt
- defensive action height
- xG / xThreat
- progression
- match analytical profiles

Handles/ecosystem:

`@markstatsbot`
`@markrstats`

---

## liverpxxl9

Useful reference for communicating passing-network interpretation in ordinary football language.

Handle:

`@liverpxxl9`

---

# 21. Data capabilities this moodboard implies

Many desired visualisations require richer evidence than FRL currently exposes.

A dedicated upstream audit should inspect PulseLive/Opta-style data for:

- event IDs
- event sequence/order
- timestamps
- possession IDs
- possession sequences
- x/y coordinates
- end x/y coordinates
- player
- recipient
- team
- event type
- event outcome
- qualifiers
- pass type
- shot type
- body part
- formation
- tactical changes
- substitutions
- pressure events
- turnovers
- recoveries
- carries
- touches
- defensive actions

Particular priority:

> **Determine whether FRL can acquire governed spatial football data.**

Without it, pass maps, shot maps, passing networks and many territorial models cannot be implemented faithfully.

Missing evidence must remain missing rather than be inferred without justification.

---

# 22. Future analytical primitives

The initial moodboard suggests that FRL should eventually develop reusable primitives for:

1. Pitch map
2. Shot map
3. Pass map
4. Passing network
5. Touch/action heatmap
6. Zonal difference map
7. Field tilt
8. Average positions
9. Defensive action height
10. Team/player percentile profile
11. Role-specific radar/profile
12. Analytical scatterplot
13. Residual/expected-vs-actual plot
14. Shape of the Season
15. Team style fingerprint
16. Pressing efficiency profile
17. Progression profile
18. Possession-value visualisation
19. Tactical XI
20. Interactive lineup builder

These should eventually share governed data contracts and reusable visual components rather than being independently improvised on each page.

---

# 23. Current priorities

The current design sequence is:

**Fixtures → League Table → Teams → Team Profile → Players**

Fixtures, League Table and Teams have established the newer FRL visual language.

The immediate design target is now:

# **Team Profile**

followed by:

# **Players / Player Profile**

This moodboard should inform both.

After the initial visual-reference exercise, a separate upstream investigation should determine whether PulseLive contains sufficient spatial/event evidence to support the desired next generation of FRL analytics.

---

# 24. Standing instruction for future iterations

When designing a new FRL analytical surface:

1. Identify the football question first.
2. Determine what governed evidence exists.
3. Distinguish raw metrics from derived analytical concepts.
4. Choose the visual form that best exposes the relevant pattern.
5. State the comparison population/context.
6. Preserve exact values and provenance where appropriate.
7. Do not imply unavailable evidence.
8. Prefer reusable analytical primitives over one-off dashboard widgets.
9. Keep performance and style conceptually distinct.
10. Make complex analysis understandable without stripping away its analytical meaning.

The long-term ambition is for FRL to feel like:

> **a football research environment in which the user can interrogate data, see football patterns, test ideas, compare states, build models and manipulate football structures — with every conclusion traceable back to governed evidence.**

---

# 25. Maintenance

Daniel intends to continue collecting interesting football analytics and visualisation references.

When a new reference materially adds to the analytical vocabulary, update this document with:

- the source/account
- the football question being answered
- the useful visual or interaction principle
- possible FRL application
- any implied upstream data requirement

Avoid adding references merely because they look attractive.

The moodboard exists to preserve **useful analytical ideas**.