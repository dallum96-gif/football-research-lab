"""First-pass FRL variable universe metadata.

This registry is intentionally descriptive: it records where a variable belongs,
its modelling eligibility, and its temporal/leakage boundary. It does not yet
calculate any variables.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


LeakageRisk = Literal["none", "controlled", "high"]
Status = Literal["proposed", "available", "implemented", "validated"]
VariableClass = Literal["raw", "derived", "historical", "matchup", "model_feature"]


@dataclass(frozen=True)
class VariableSpec:
    name: str
    grain: str
    variable_class: VariableClass
    profile: bool
    stats: bool
    research: bool
    model: bool
    temporal: bool
    leakage_risk: LeakageRisk
    status: Status = "proposed"


VARIABLE_UNIVERSE_V1: tuple[VariableSpec, ...] = (
    # Core team performance
    VariableSpec("points", "team-season", "raw", True, True, True, True, True, "controlled", "available"),
    VariableSpec("points_per_match", "team-season", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("wins", "team-season", "raw", True, True, True, True, True, "controlled", "available"),
    VariableSpec("draws", "team-season", "raw", True, True, True, True, True, "controlled", "available"),
    VariableSpec("losses", "team-season", "raw", True, True, True, True, True, "controlled", "available"),
    VariableSpec("win_rate", "team-season", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("goal_difference", "team-season", "derived", True, True, True, True, True, "controlled", "available"),
    VariableSpec("goals_for", "team-season", "raw", True, True, True, True, True, "controlled", "available"),
    VariableSpec("goals_against", "team-season", "raw", True, True, True, True, True, "controlled", "available"),
    VariableSpec("goals_for_per_match", "team-season", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("goals_against_per_match", "team-season", "derived", True, True, True, True, True, "controlled", "implemented"),
    # Form / trajectory
    VariableSpec("ppg_last_5", "team-window", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("ppg_last_10", "team-window", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("ppg_vs_season_average", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
    VariableSpec("form_acceleration", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
    VariableSpec("wins_streak", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
    VariableSpec("unbeaten_streak", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
    VariableSpec("scoring_streak", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
    # Venue
    VariableSpec("home_ppg", "team-window", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("away_ppg", "team-window", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("home_away_ppg_gap", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
    # Statistical identity
    VariableSpec("xg", "team-match", "raw", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("xga", "team-match", "raw", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("shots", "team-match", "raw", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("shots_on_target", "team-match", "raw", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("possession", "team-match", "raw", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("clean_sheet_rate", "team-window", "derived", True, True, True, True, True, "controlled", "implemented"),
    VariableSpec("failed_to_score_rate", "team-window", "derived", True, True, True, True, True, "controlled", "implemented"),
    # Matchup / model layer
    VariableSpec("ppg_difference", "fixture", "matchup", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("recent_ppg_difference", "fixture", "matchup", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("attack_strength_difference", "fixture", "matchup", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("defence_strength_difference", "fixture", "matchup", False, True, True, True, True, "controlled", "proposed"),
    VariableSpec("opponent_adjusted_ppg", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
    VariableSpec("schedule_strength", "team-window", "derived", True, True, True, True, True, "controlled", "proposed"),
)


def profile_variables() -> tuple[VariableSpec, ...]:
    return tuple(v for v in VARIABLE_UNIVERSE_V1 if v.profile)


def stats_variables() -> tuple[VariableSpec, ...]:
    return tuple(v for v in VARIABLE_UNIVERSE_V1 if v.stats)


def model_candidates() -> tuple[VariableSpec, ...]:
    return tuple(v for v in VARIABLE_UNIVERSE_V1 if v.model and v.temporal and v.leakage_risk != "high")
