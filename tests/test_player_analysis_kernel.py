from __future__ import annotations

import player_analysis_kernel
from api.player_stats import (
    get_player_profile,
    get_player_rankings,
    get_player_seasons,
    get_player_stats,
    get_players,
)


CURRENT_SEASON = "2026-27"
RAYA_CODE = "154561"
KEPA_CODE = "109745"


def test_player_profiles_keep_registered_zero_minute_players_but_rankings_do_not() -> None:
    players = get_players(CURRENT_SEASON)
    kepa = next(player for player in players if player.player_code == KEPA_CODE)

    assert kepa.player_name == "Kepa Arrizabalaga Revuelta"
    assert kepa.position == "GKP"
    assert kepa.minutes == 0
    assert kepa.appearances == 0

    rankings = get_player_rankings(CURRENT_SEASON, "GKP")
    eligible_codes = {
        entry.player_code
        for metric in rankings.metrics
        for entry in metric.entries
    }

    assert KEPA_CODE not in eligible_codes
    assert rankings.population_size == sum(
        1
        for player in players
        if player.position == "GKP" and player.minutes > 0
    )


def test_current_player_profile_and_stats_use_the_same_governed_identity() -> None:
    profile = get_player_profile(CURRENT_SEASON, RAYA_CODE)
    stats = get_player_stats(CURRENT_SEASON, RAYA_CODE)

    assert profile.player_code == RAYA_CODE
    assert stats.player.player_code == RAYA_CODE
    assert profile.player_name == stats.player.player_name == "David Raya Martín"
    assert profile.position == stats.player.position == "GKP"
    assert profile.appearances == stats.player.appearances == 1
    assert profile.starts == stats.player.starts == 1
    assert profile.minutes == stats.player.minutes == 90
    assert stats.cohort.position == "GKP"
    assert stats.cohort.minimum_minutes == 1


def test_per_90_values_are_derived_from_pooled_player_season_totals() -> None:
    stats = get_player_stats(CURRENT_SEASON, RAYA_CODE)
    saves = next(metric for metric in stats.metrics if metric.key == "saves_per_90")

    assert saves.representation == player_analysis_kernel.PLAYER_SEASON_DERIVATION
    assert saves.value == 1.0
    assert saves.rank is not None
    assert saves.out_of == stats.cohort.minimum_minutes * 0 + saves.eligible_players


def test_current_season_does_not_invent_absent_rich_passing_metrics() -> None:
    analysis = player_analysis_kernel.season_position_analysis(CURRENT_SEASON, "MID")

    assert analysis["metrics"]["attempted_passes"]["availability"] == "UNAVAILABLE"
    assert analysis["metrics"]["completed_passes"]["availability"] == "UNAVAILABLE"
    assert analysis["metrics"]["pass_completion"]["availability"] == "UNAVAILABLE"


def test_richer_player_metrics_can_surface_when_source_fields_are_present() -> None:
    player = {
        "minutes": 900,
        "attempted_passes": 500,
        "completed_passes": 400,
        "key_passes": 20,
        "big_chances_created": 5,
        "dribbles": 30,
    }

    assert player_analysis_kernel.metric_value(
        player,
        player_analysis_kernel.DEFINITIONS_BY_KEY["attempted_passes"],
    ) == 500
    assert player_analysis_kernel.metric_value(
        player,
        player_analysis_kernel.DEFINITIONS_BY_KEY["completed_passes"],
    ) == 400
    assert player_analysis_kernel.metric_value(
        player,
        player_analysis_kernel.DEFINITIONS_BY_KEY["pass_completion"],
    ) == 80.0
    assert player_analysis_kernel.metric_value(
        player,
        player_analysis_kernel.DEFINITIONS_BY_KEY["key_passes_per_90"],
    ) == 2.0
    assert player_analysis_kernel.metric_value(
        player,
        player_analysis_kernel.DEFINITIONS_BY_KEY["big_chances_created_per_90"],
    ) == 0.5
    assert player_analysis_kernel.metric_value(
        player,
        player_analysis_kernel.DEFINITIONS_BY_KEY["dribbles_per_90"],
    ) == 3.0


def test_player_season_navigation_is_source_backed() -> None:
    seasons = get_player_seasons(RAYA_CODE)

    assert seasons
    assert all(option.player_code == RAYA_CODE for option in seasons)
    assert CURRENT_SEASON in {option.season for option in seasons}
