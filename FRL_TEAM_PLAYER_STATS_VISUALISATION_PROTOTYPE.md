# FRL Team & Player Stats Visualisation Prototype

**Status:** Product design prototype / architecture decision  
**Date:** 2026-08-30  
**Scope:** Team Stats, Player Stats, rankings, comparison, and the relationship between Profiles and analytical workspaces

---

## 1. The product question

FRL needs somewhere for detailed team statistics to live.

It also needs somewhere to answer a different but closely related question:

> **How does every team compare on a particular statistic?**

A third question will eventually matter too:

> **How do a selected set of teams compare across a range of statistics?**

The same problem will later apply to players.

The key design decision is that these should **not become separate statistical systems**. They should be different ways of looking through the **same governed FRL metric layer**.

The core product rule is:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

---

# 2. Team Profile and Team Stats should remain separate

## Team Profile

The Team Profile answers:

> **Tell me about Arsenal.**

It is primarily an identity, history and season-story surface.

Its job is to organise things such as:

- club identity
- season context
- records
- XI / personnel
- fixtures and results
- form
- narrative season state
- navigation into deeper analytical work

The Team Profile should remain relatively human, visual and story-oriented.

It should **not gradually become a giant statistical dashboard**.

Instead, the Profile should provide a clear route into the analytical environment:

> **View Arsenal in Team Stats →**

The selected team and season should carry through automatically.

---

## Team Stats

Team Stats answers:

> **Measure Arsenal.**

This is where FRL becomes explicitly analytical.

It should support:

- governed metrics
- league context
- ranks
- percentiles
- distributions
- rates
- trends
- home / away splits
- historical comparisons
- research pathways

The distinction should remain durable:

> **Profile = identity and story.**  
> **Stats = measurement and investigation.**

---

# 3. Team Stats should be a workspace, not one page

There are two immediately important analytical questions.

## Team View

> **How did one team perform across many measures?**

This is one team viewed vertically across many metrics.

Example:

### Arsenal · 2024/25

| Metric | Value | League rank | Percentile |
|---|---:|---:|---:|
| Points per match | 1.95 | 2nd | P95 |
| Goals per match | 1.82 | 3rd | P90 |
| Goals against | 0.89 | 1st | P100 |
| Shots per match | 14.37 | 5th | P79 |
| Shots on target | 4.95 | 6th | P74 |
| Possession | 56.96% | 4th | P84 |

The user moves:

> **down the metrics for one team**

This view answers questions like:

- What was Arsenal elite at?
- Where were they merely above average?
- What was comparatively weaker?
- Did their performance change over the season?
- Were they different home and away?
- Did outputs align with underlying process?

---

## League Rankings

> **How did every team rank for a particular measure?**

This is the inverse orientation.

Example:

### Shots per match · Premier League · 2024/25

| Rank | Team | Shots |
|---|---|---:|
| 1 | Team A | ... |
| 2 | Team B | ... |
| 3 | Team C | ... |
| 4 | Team D | ... |
| 5 | Arsenal | 14.37 |
| ... | ... | ... |

The user moves:

> **down the teams for one metric**

This answers questions like:

- Who led the league for shots?
- Which teams dominated possession?
- Who conceded the fewest chances?
- Which clubs were extreme outliers?
- Where exactly does Arsenal sit within the population?

These two views are effectively **transposes of one another**.

That symmetry should become a central part of FRL's analytical architecture.

---

# 4. They should live in the same place — but not be the same page

The cleanest structure is:

## TEAM STATS

**Team View · League Rankings**

Later:

**Team View · League Rankings · Compare**

Beneath that mode switch should sit the analytical families:

**Overview · Attack · Possession · Passing · Defence · Discipline**

This means the analytical category stays constant while the lens changes.

For example:

### Team View → Attack

Could show Arsenal's:

- shot volume
- shots on target
- shot quality
- xG
- big chances
- conversion
- attacking efficiency
- attacking trends
- league percentile for each metric

### League Rankings → Attack

Could rank all Premier League clubs for:

- shots
- shots on target
- xG
- big chances
- conversion
- attacking efficiency

Same governed metrics.

Different analytical orientation.

---

# 5. Future Compare mode

Eventually Team Stats should add:

## Compare

> **How did a selected set of teams compare across many measures?**

Conceptually:

- **Team View = one team × many metrics**
- **League Rankings = many teams × one/few metrics**
- **Compare = selected teams × many metrics**

Example:

### Arsenal vs Liverpool vs Manchester City

Compare:

- possession
- shots
- shots on target
- xG
- conversion
- passes
- territorial measures
- defensive actions
- discipline
- future derived FRL metrics

Compare should **not be built first**.

Team View and League Rankings should establish the analytical grammar first.

---

# 6. Proposed Team Stats navigation

```text
TEAM STATS

┌──────────────────────────────────────────────┐
│ Team View │ League Rankings │ Compare later │
└──────────────────────────────────────────────┘

Overview
Attack
Possession
Passing
Defence
Discipline
```

The mode describes **what is being compared**.

The category describes **which part of football is being analysed**.

---

# 7. Team View visual grammar

The first Team Stats prototype has already revealed several useful design ideas.

These should be retained and refined.

## 7.1 League-context metric cards

A metric should not simply say:

> Shots: 14.4

It should say:

> **14.4 shots per match**  
> **5th of 20**  
> **79th percentile**

The absolute value matters, but FRL should make the context equally effortless to understand.

---

## 7.2 Percentile rails

Percentile rails are useful because they can represent very different metrics using the same visual grammar.

They answer:

> **Where does this team sit within the comparable league population?**

They should remain restrained.

FRL should avoid colourful videogame-style attribute bars. The percentile is analytical context, not decoration.

---

## 7.3 Trends

Season averages can hide important changes.

Team View should eventually support trends such as:

- rolling PPG
- rolling shots
- rolling shots on target
- rolling xG
- xG difference
- possession
- defensive shot suppression
- attacking efficiency

The current five-match rolling PPG prototype is conceptually useful.

However:

> **The current graph overflow bug must be fixed before that component is considered finished.**

The purpose of trends is to answer:

> **Was this team consistently like this, or did something change?**

---

## 7.4 Home / away splits

Where meaningful, Team Stats should expose differences between home and away performance.

Potential metrics include:

- points per match
- goals for
- goals against
- shots
- possession
- xG
- chance creation
- defensive metrics
- territorial metrics

The interface should show meaningful differences without exaggerating trivial variation.

---

## 7.5 Distributions

Percentiles are useful summaries.

But a user should eventually be able to inspect the actual underlying league distribution.

Example:

> Arsenal possession: 56.96%  
> 4th in the league  
> P84

A deeper interaction could show all 20 clubs on the same distribution.

That creates a natural movement from:

> **Team View → League Rankings**

---

# 8. League Rankings visual grammar

League Rankings should not simply become a spreadsheet.

It should combine the precision of a ranking table with enough visual structure to reveal patterns.

Potential elements:

- explicit rank
- TeamKit identity
- team name
- metric value
- percentile
- distribution marker
- season selector
- analytical family selector
- sortable metric columns
- optional home / away split
- link from any team directly into Team View

A useful interaction loop would be:

> **League Rankings → Arsenal → Analyse Team**

and:

> **Team View → 5th of 20 → View League Ranking**

The two modes should feel like opposite sides of the same analytical object.

---

# 9. Player Stats should follow the same architecture

The same conceptual distinction should apply to players.

## Player Profile

The Player Profile answers:

> **Tell me about Mohamed Salah.**

Potential content:

- identity
- club
- position
- appearances
- minutes
- season participation
- match history
- career / season records
- notable performances
- role context
- navigation into deeper statistical analysis

Again:

> **Profile = identity and story.**

The Player Profile should link into:

> **View Salah in Player Stats →**

---

## Player Stats

Player Stats answers:

> **Measure Mohamed Salah.**

The same top-level structure can apply:

**Player View · League Rankings**

Later:

**Player View · League Rankings · Compare**

---

# 10. Player rankings need governed comparison populations

Player comparisons are more complicated than team comparisons.

FRL should never casually rank players whose roles or sample sizes make the comparison misleading.

Player ranking controls may eventually include:

- position
- role
- minimum minutes
- starts
- team
- age
- season
- competition
- totals
- per-90 rates
- percentages
- per-possession measures
- other governed populations

The comparison population must always be explicit.

For example:

> **Premier League forwards with 900+ minutes**

is analytically stronger than simply:

> **All players**

---

# 11. Possible Player Stats analytical families

The exact player categories remain provisional.

A sensible starting point could be:

**Overview · Shooting · Creation · Possession · Defending · Discipline**

Later, governed data may justify categories such as:

- Goalkeeping
- Progression
- Receiving
- Carrying
- Pressing
- Set pieces
- Aerial play

But FRL should not invent categories merely because conventional football-statistics sites contain them.

The variable capability inventory should determine what deserves to exist.

---

# 12. One governed metric layer

This is the most important technical and methodological principle.

FRL should not implement:

- one statistical system for Profiles
- another for Team View
- another for Rankings
- another for Compare
- another for Research

Instead:

> **One governed metric layer → multiple analytical lenses**

A metric should have one governed definition.

That metric can then appear in:

- Team View
- League Rankings
- Compare
- Player View
- Player Rankings
- Visualisations
- Research
- predictive models where methodologically appropriate

This avoids duplicated calculations and metric drift.

---

# 13. Cross-surface consistency must be exact

If Team View says:

> **Arsenal — Shots per match — 5th of 20**

then League Rankings must show:

> **5. Arsenal — 14.37 shots per match**

from the exact same governed calculation.

There should never be separate implementations that merely happen to produce similar numbers.

One source.

Multiple views.

---

# 14. Profile-to-Stats navigation

Profiles should expose analytical doorways without absorbing the analytical workspace.

## Team Profile

Potential actions:

> **View Arsenal in Team Stats →**

> View attack metrics

> View league rankings

> Compare season

## Player Profile

Potential actions:

> **View Salah in Player Stats →**

> View shooting metrics

> View league ranking

> Compare players

These are transitions between product modes.

They are not reasons to duplicate the analytical dashboard inside Profile.

---

# 15. Why Profile and Stats should remain separate

Combining Profile and Stats is initially tempting because both concern the same entity.

But the user intent is different.

A Profile is generally **browsed**.

A Stats workspace is **investigated**.

Separating them means:

1. Profiles remain approachable.
2. Stats can grow much deeper.
3. Analytical controls have space.
4. Rankings naturally live beside analysis.
5. Compare can later join the same workspace.
6. Player architecture can mirror Team architecture.
7. Research can connect naturally from statistical observations.
8. FRL avoids giant entity pages with endless tabs.

---

# 16. The long-term FRL analytical journey

A strong future journey could be:

```text
Team Profile
     ↓
Team View
     ↓
Notice an unusual percentile
     ↓
League Rankings
     ↓
Inspect the population
     ↓
Compare selected teams
     ↓
Open Research
     ↓
Formulate a hypothesis
     ↓
Test it against governed historical data
```

This matters because FRL should not merely display football statistics.

Its interfaces should help users **generate research questions**.

---

# 17. Immediate Team Stats V1

The first Team View should remain restrained.

## Team View → Overview

Initial components:

- TeamKit + team identity
- season selector
- team selector
- six high-signal metrics
- league rank
- percentile
- percentile rail
- rolling season trend
- home / away comparison
- secondary metrics
- links into deeper analytical families

The currently governed seam already gives us useful measures including:

- points per match
- goals for
- goals against
- possession
- shots
- shots on target
- passes
- accurate passes
- tackles
- interceptions
- clearances
- fouls
- yellow cards
- red cards
- optional xG
- optional xA
- optional big-chance data

V1 should favour:

> **a small number of trustworthy metrics**

over:

> **hundreds of available numbers dumped onto a page**

---

# 18. Immediate League Rankings V1

Once Team View → Overview is stable, the complementary page should be:

## League Rankings → Overview

Initial ranked metrics could include:

- points per match
- goals per match
- goals against per match
- shots per match
- shots on target per match
- possession

These are deliberately the same core measures used on Team View Overview.

That proves the two lenses are using the same underlying system.

---

# 19. Cross-linking requirements

Team View and League Rankings should be tightly connected.

Example Team View card:

> **Shots per match**  
> 14.37  
> **5th of 20 → View ranking**

That should take the user directly to:

> **League Rankings → Attack → Shots per match**

Likewise, selecting Arsenal inside Rankings should offer:

> **Analyse Arsenal →**

This produces a navigable analytical system rather than disconnected pages.

---

# 20. Compare comes later

Compare is desirable.

But it should not distract us from proving the first two analytical lenses.

Recommended order:

1. Team View → Overview
2. League Rankings → Overview
3. Team View analytical families
4. League Ranking analytical families
5. Player equivalent
6. Compare mode

Once the components, metrics and comparison populations already exist, Compare becomes much easier to build correctly.

---

# 21. Visual principles

The Team / Player Stats environment should retain the FRL visual language that has worked elsewhere.

## Keep

- warm parchment surfaces
- compact information density
- restrained coral
- restrained olive
- TeamKit identity
- strong editorial typography
- quiet metadata
- league context
- subtle playfulness
- clear hierarchy
- useful percentile treatments
- meaningful graphs

## Avoid

- generic SaaS dashboards
- giant KPI tiles
- rainbow attribute bars
- decorative charts
- unexplained rankings
- incomparable player populations
- duplicated calculations
- hundreds of metrics on one screen
- Profiles becoming analytical mega-pages

---

# 22. North-star principle

The purpose of Team Stats and Player Stats is not simply to show numbers.

The surface should help the user move naturally through:

> **Observation → Context → Comparison → Question**

A user looking at Arsenal should quickly understand:

- what they were elite at
- what they were merely good at
- what was comparatively weak
- whether that changed through the season
- whether home and away differed
- how the league population compared
- what deserves investigating next

That is much more valuable than another football-statistics table.

---

# 23. Prototype architecture

```text
TEAM PROFILE
Identity · Records · XI · Fixtures & Results · Form
        │
        └── View in Team Stats →
                    │
                    ▼
TEAM STATS
┌──────────────────────────────────────────────┐
│ Team View │ League Rankings │ Compare later │
└──────────────────────────────────────────────┘
        │
        ├── Overview
        ├── Attack
        ├── Possession
        ├── Passing
        ├── Defence
        └── Discipline
```

Player equivalent:

```text
PLAYER PROFILE
Identity · Participation · Matches · Records · Context
        │
        └── View in Player Stats →
                    │
                    ▼
PLAYER STATS
┌───────────────────────────────────────────────┐
│ Player View │ League Rankings │ Compare later │
└───────────────────────────────────────────────┘
        │
        ├── Overview
        ├── Shooting
        ├── Creation
        ├── Possession
        ├── Defending
        └── Discipline
```

The exact Player Stats categories remain provisional and should be governed by the variable capability inventory.

---

# 24. Final design decision

The architecture should therefore follow this rule:

> **Profiles describe entities.**

> **Stats analyse entities.**

> **Rankings analyse populations.**

> **Compare analyses selected entities together.**

> **Research tests the questions these surfaces reveal.**

They are separate experiences.

But they should behave like one connected analytical system.

And underneath all of them:

> **one governed FRL data and metric layer.**

That is the Team / Player Stats visualisation prototype direction.
