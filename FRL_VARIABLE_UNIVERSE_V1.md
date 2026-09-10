# Football Research Laboratory — Variable Universe V1

**Status:** First-pass variable registry / design contract  
**Purpose:** Define the broad universe of football variables FRL may expose for research, visualisation and modelling.

## 1. Principle

FRL should not reduce its data universe to only variables that immediately improve a prediction model.

The project has two legitimate jobs:

1. **Football research** — make the game interesting, interpretable and explorable.
2. **Predictive modelling** — identify variables that contain repeatable pre-match signal.

A variable can therefore be:

- research-facing only;
- model-facing only;
- useful for both;
- a raw observation;
- or a derived feature built from trusted observations.

## 2. Variable lifecycle

Every variable should ultimately have:

| Field | Meaning |
|---|---|
| `name` | Stable machine-readable variable name |
| `grain` | Fixture, team-season, team-window, player-season, etc. |
| `class` | Raw, derived, historical, matchup, model feature |
| `profile` | Appropriate for Team Profile |
| `stats` | Appropriate for Team Stats |
| `research` | Useful for descriptive/exploratory research |
| `model` | Candidate modelling feature |
| `temporal` | Must be computed from information available at a defined point in time |
| `leakage_risk` | None, controlled, or high |
| `provenance` | Source/derivation required |
| `status` | Proposed, available, implemented, validated |

## 3. Team Profile universe

Team Profile should answer **“What is this club's story?”**

### Identity & stature

| Variable | Research | Model | Notes |
|---|---:|---:|---|
| `pl_seasons` | ✓ | | Number of Premier League seasons |
| `current_pl_streak` | ✓ | | Consecutive PL seasons |
| `highest_finish` | ✓ | | Historical club context; not a pre-match feature |
| `average_finish` | ✓ | | Historical context |
| `league_titles` | ✓ | | Historical context |
| `promotion_seasons` | ✓ | | Historical context |

### Season performance

| Variable | Research | Model | Notes |
|---|---:|---:|---|
| `points` | ✓ | ✓ | Season-end or point-in-time depending on context |
| `points_per_match` | ✓ | ✓ | Core rate variable |
| `wins` | ✓ | ✓ | |
| `draws` | ✓ | ✓ | |
| `losses` | ✓ | ✓ | |
| `win_rate` | ✓ | ✓ | |
| `goal_difference` | ✓ | ✓ | |
| `goals_for` | ✓ | ✓ | |
| `goals_against` | ✓ | ✓ | |
| `goals_for_per_match` | ✓ | ✓ | |
| `goals_against_per_match` | ✓ | ✓ | |

### Historical trajectory

| Variable | Research | Model | Temporal requirement |
|---|---:|---:|---|
| `ppg_last_3` | ✓ | ✓ | Pre-match/windowed when modelling |
| `ppg_last_5` | ✓ | ✓ | Pre-match/windowed when modelling |
| `ppg_last_10` | ✓ | ✓ | Pre-match/windowed when modelling |
| `ppg_vs_season_average` | ✓ | ✓ | Must use information available at timestamp |
| `points_trend` | ✓ | ✓ | Derived from historical sequence |
| `goal_difference_trend` | ✓ | ✓ | Derived from historical sequence |
| `attack_trend` | ✓ | ✓ | Derived from GF / match or richer attack metrics |
| `defence_trend` | ✓ | ✓ | Derived from GA / match or richer defensive metrics |
| `season_to_season_ppg_change` | ✓ | | Descriptive historical feature |
| `best_recent_season` | ✓ | | Historical |
| `worst_recent_season` | ✓ | | Historical |

### Form & streaks

| Variable | Research | Model | Temporal requirement |
|---|---:|---:|---|
| `form_last_3` | ✓ | ✓ | Must be point-in-time |
| `form_last_5` | ✓ | ✓ | Must be point-in-time |
| `form_last_10` | ✓ | ✓ | Must be point-in-time |
| `wins_streak` | ✓ | ✓ | Must be point-in-time |
| `unbeaten_streak` | ✓ | ✓ | Must be point-in-time |
| `losses_streak` | ✓ | ✓ | Must be point-in-time |
| `scoring_streak` | ✓ | ✓ | Must be point-in-time |
| `clean_sheet_streak` | ✓ | ✓ | Must be point-in-time |

### Venue profile

| Variable | Research | Model |
|---|---:|---:|
| `home_ppg` | ✓ | ✓ |
| `away_ppg` | ✓ | ✓ |
| `home_win_rate` | ✓ | ✓ |
| `away_win_rate` | ✓ | ✓ |
| `home_gf_per_match` | ✓ | ✓ |
| `away_gf_per_match` | ✓ | ✓ |
| `home_ga_per_match` | ✓ | ✓ |
| `away_ga_per_match` | ✓ | ✓ |
| `home_away_ppg_gap` | ✓ | ✓ |

### Season shape

| Variable | Research | Model | Notes |
|---|---:|---:|---|
| `early_season_ppg` | ✓ | ✓ | Point-in-time windows |
| `mid_season_ppg` | ✓ | ✓ | Point-in-time windows |
| `late_season_ppg` | ✓ | ✓ | Historical descriptive; safe for modelling only before a future match if constructed cumulatively |
| `strongest_phase` | ✓ | | Descriptive |
| `weakest_phase` | ✓ | | Descriptive |
| `late_season_change` | ✓ | ✓ | Requires temporal construction |

## 4. Team Stats universe

Team Stats should answer **“What does this team actually do?”**

### Results

`wins`, `draws`, `losses`, `points`, `points_per_match`, `win_rate`, `unbeaten_rate`, `points_from_losing_positions`.

### Attack

`goals`, `goals_per_match`, `xg`, `xg_per_match`, `shots`, `shots_per_match`, `shots_on_target`, `shots_on_target_per_match`, `shots_off_target`, `blocked_shots`, `shot_accuracy`, `goal_conversion`, `goals_per_shot`, `goals_per_shot_on_target`, `corners`, `corners_per_match`, `offsides`.

### Possession & build-up

`possession`, `passes`, `passes_per_match`, `pass_accuracy`, `crosses`, `cross_accuracy`, `through_balls` where available.

### Defence

`goals_conceded`, `goals_against_per_match`, `xga`, `xga_per_match`, `shots_faced`, `shots_on_target_faced`, `clean_sheets`, `clean_sheet_rate`, `tackles`, `interceptions`, `clearances`, `blocks`, `defensive_efficiency`.

### Discipline

`fouls_committed`, `fouls_won`, `yellow_cards`, `red_cards`, `offsides_won`, `offsides_conceded` where available.

### Efficiency

`goals_per_shot`, `goals_per_shot_on_target`, `points_per_goal`, `clean_sheet_rate`, `failed_to_score_rate`, `shots_per_goal`, `xg_overperformance`, `xg_underperformance`.

### Splits

Each major statistical variable should eventually support relevant splits:

- home / away;
- recent window;
- full season;
- opponent-strength bucket;
- game-state where the underlying data supports it.

## 5. Derived variable universe

Derived variables are where the largest future feature space will sit.

### Rolling windows

`rolling_3`, `rolling_5`, `rolling_10` versions of relevant rates such as:

- PPG;
- GF / match;
- GA / match;
- xG / match;
- xGA / match;
- shots / match;
- shots on target / match;
- clean-sheet rate.

### Change variables

- `current_vs_season_ppg`
- `current_vs_previous_window_ppg`
- `attack_acceleration`
- `defence_acceleration`
- `form_acceleration`
- `season_to_date_change`
- `home_away_gap`

### Strength variables

- `goal_difference_strength`
- `attack_strength`
- `defence_strength`
- `opponent_adjusted_ppg`
- `opponent_adjusted_gf`
- `opponent_adjusted_ga`
- `schedule_strength`

### Matchup variables

For a fixture A vs B, construct directional differences such as:

- `ppg_difference`
- `recent_ppg_difference`
- `attack_strength_difference`
- `defence_strength_difference`
- `home_attack_vs_away_defence`
- `away_attack_vs_home_defence`
- `form_difference`
- `schedule_strength_difference`.

## 6. Modelling boundary

A variable is **model-eligible** only when its calculation can be reconstructed exactly from information available before the prediction timestamp.

Examples:

- `season_end_finish` — useful research variable, but not a pre-match feature for that season.
- `current_ppg_entering_fixture` — model-eligible.
- `last_5_ppg_entering_fixture` — model-eligible.
- `post-match xG` for the fixture being predicted — prohibited leakage.
- `future season points` — prohibited leakage.

The same underlying concept may therefore exist in separate forms:

- **historical descriptive value**;
- **point-in-time feature value**.

Those are not interchangeable.

## 7. Priority

### Already strong / obvious

PPG, points, GF, GA, GD, W/D/L, win rate, home/away splits, form windows, rolling PPG, rolling GF/GA.

### High-value next additions

xG/xGA, shots, shots on target, shot efficiency, clean-sheet rate, failed-to-score rate, schedule strength, opponent-adjusted performance, game-state variables.

### Exploratory / potentially rich

Momentum, acceleration, consistency, volatility, streak quality, phase strength, attacking/defensive imbalance, matchup interactions.

## 8. Future registry rule

The eventual machine-readable registry should preserve the distinction between:

**what FRL can display**, **what FRL can calculate**, and **what FRL can legally use as a pre-match model feature**.

The variable universe should grow continuously without allowing the modelling feature set to silently inherit future information.
