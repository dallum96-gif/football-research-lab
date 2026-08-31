import math

import team_research_stats
from expected_metric_routing import (
    DIRECT_TEAM_MATCH,
    NO_GOVERNED_SEASON_ROUTE,
    PLAYER_MATCH_DERIVED_TEAM_MATCH,
)
from team_analysis_kernel import (
    COMPETITION_RANK,
    DIRECT_TEAM_DERIVATION,
    OVERVIEW_METRICS,
    RANKING_METRICS,
    RANK_POSITION_PERCENTILE,
    TEAM_VIEW_OVERVIEW_KEYS,
    rank_metric_entries,
    season_overview_analysis,
    team_overview_analysis,
)


def test_competition_rank_preserves_ties_and_existing_percentile_formula():
    entries = [
        {"team": "A", "value": 2.0},
        {"team": "B", "value": 2.0},
        {"team": "C", "value": 1.0},
        {"team": "D", "value": None},
    ]

    rank_metric_entries(entries, higher_is_better=True)

    assert [(row["rank"], row["out_of"], row["percentile"]) for row in entries] == [
        (1, 3, 100.0),
        (1, 3, 100.0),
        (3, 3, 0.0),
        (None, 3, None),
    ]


def test_league_rankings_overview_stays_compact_while_catalogue_can_extend():
    analysis = season_overview_analysis("2024-25")

    assert analysis["population_size"] == 20
    assert analysis["ranking_policy"] == COMPETITION_RANK
    assert analysis["percentile_policy"] == RANK_POSITION_PERCENTILE
    assert len(OVERVIEW_METRICS) == 6
    assert "Corners_per_match" not in {metric.key for metric in OVERVIEW_METRICS}
    assert tuple(analysis["metrics"]) == tuple(metric.key for metric in RANKING_METRICS)

    for metric in RANKING_METRICS:
        result = analysis["metrics"][metric.key]
        assert result["definition"]["label"] == metric.label
        assert result["definition"]["higher_is_better"] is metric.higher_is_better
        assert len(result["entries"]) == 20


def test_family_metric_registry_exposes_the_broad_governed_team_stats_catalogue():
    definitions = {metric.key: metric for metric in RANKING_METRICS}

    assert {
        # Attack
        "Shots off target_per_match",
        "Blocked shots_per_match",
        "Corners_per_match",
        "Offsides_per_match",
        "Big chances created_per_match",
        "Big chances missed_per_match",
        "shot_accuracy",
        "goals_per_shot",
        "failed_to_score_rate",
        # Passing
        "Passes_per_match",
        "Accurate passes_per_match",
        "pass_accuracy",
        "Crosses_per_match",
        # Defence
        "Tackles_per_match",
        "Tackles won_per_match",
        "Interceptions_per_match",
        "Interceptions won_per_match",
        "Clearances_per_match",
        "Effective clearances_per_match",
        "Saves_per_match",
        "clean_sheet_rate",
        # Discipline
        "Fouls conceded_per_match",
        "Fouls won_per_match",
        "Yellow cards_per_match",
        "Red cards_per_match",
    } <= set(definitions)

    assert len(OVERVIEW_METRICS) == 6
    assert {
        "Passes_per_match",
        "Tackles won_per_match",
        "Yellow cards_per_match",
        "shot_accuracy",
    }.isdisjoint({metric.key for metric in OVERVIEW_METRICS})

    assert definitions["shot_accuracy"].representation == DIRECT_TEAM_DERIVATION
    assert definitions["pass_accuracy"].representation == DIRECT_TEAM_DERIVATION


def test_team_view_overview_uses_broader_balanced_profile():
    assert TEAM_VIEW_OVERVIEW_KEYS == (
        "points_per_match",
        "goals_for_per_match",
        "Shots_per_match",
        "Shots on target_per_match",
        "shot_accuracy",
        "Possession_per_match",
        "pass_accuracy",
        "goals_against_per_match",
        "clean_sheet_rate",
        "failed_to_score_rate",
    )


def test_fraction_rates_are_exposed_as_percentage_points():
    season = "2025-26"
    analysis = season_overview_analysis(season)
    result = analysis["metrics"]["pass_accuracy"]

    for entry in result["entries"]:
        stats = team_research_stats.team_season_stats(
            season,
            entry["persistent_team_code"],
        )
        raw = stats.get("pass_accuracy")
        expected = float(raw) * 100.0 if raw is not None else None
        assert entry["value"] == expected


def test_2026_27_direct_family_gaps_remain_unavailable_not_zero():
    analysis = season_overview_analysis("2026-27")

    for key in (
        "Shots off target_per_match",
        "Blocked shots_per_match",
        "Corners_per_match",
        "Offsides_per_match",
        "Big chances created_per_match",
        "Big chances missed_per_match",
        "Passes_per_match",
        "Accurate passes_per_match",
        "Crosses_per_match",
        "Tackles_per_match",
        "Tackles won_per_match",
        "Interceptions_per_match",
        "Interceptions won_per_match",
        "Clearances_per_match",
        "Effective clearances_per_match",
        "Saves_per_match",
        "Fouls conceded_per_match",
        "Fouls won_per_match",
        "Yellow cards_per_match",
        "Red cards_per_match",
    ):
        result = analysis["metrics"][key]
        assert result["definition"]["representation"] == DIRECT_TEAM_MATCH
        assert len(result["entries"]) == 20
        assert all(entry["value"] is None for entry in result["entries"])
        assert all(entry["rank"] is None for entry in result["entries"])
        assert all(entry["percentile"] is None for entry in result["entries"])
        assert all(entry["coverage"]["observed_matches"] == 0 for entry in result["entries"])


def test_2026_27_unavailable_derived_rich_metrics_stay_missing():
    analysis = season_overview_analysis("2026-27")

    for key in ("shot_accuracy", "goals_per_shot", "pass_accuracy"):
        result = analysis["metrics"][key]
        assert result["definition"]["representation"] == DIRECT_TEAM_DERIVATION
        assert all(entry["value"] is None for entry in result["entries"])
        assert all(entry["rank"] is None for entry in result["entries"])


def test_2026_27_result_derived_metrics_remain_available_for_season_aware_gui():
    analysis = season_overview_analysis("2026-27")

    for key in (
        "goals_for_per_match",
        "goals_against_per_match",
        "failed_to_score_rate",
        "clean_sheet_rate",
    ):
        result = analysis["metrics"][key]
        assert len(result["entries"]) == 20
        assert all(entry["value"] is not None for entry in result["entries"])
        assert all(entry["rank"] is not None for entry in result["entries"])
        assert all(entry["coverage"]["observed_matches"] > 0 for entry in result["entries"])


def test_corners_are_rankable_with_source_faithful_coverage_not_blank_as_zero():
    season = "2025-26"
    analysis = season_overview_analysis(season)
    result = analysis["metrics"]["Corners_per_match"]

    assert result["definition"]["representation"] == DIRECT_TEAM_MATCH
    assert result["definition"]["coverage_key"] == "Corners"
    assert sum(entry["coverage"]["missing_matches"] for entry in result["entries"]) > 0

    for entry in result["entries"]:
        stats = team_research_stats.team_season_stats(
            season,
            entry["persistent_team_code"],
        )
        expected = stats.get("Corners_per_match")
        assert entry["value"] == (float(expected) if expected is not None else None)
        coverage = stats["metric_coverage"]["Corners"]
        assert entry["coverage"]["observed_matches"] == coverage["observed_matches"]
        assert entry["coverage"]["missing_matches"] == coverage["missing_matches"]


def test_expanded_direct_metric_uses_existing_team_match_observations():
    season = "2025-26"
    analysis = season_overview_analysis(season)
    result = analysis["metrics"]["Tackles won_per_match"]

    assert result["definition"]["representation"] == DIRECT_TEAM_MATCH
    assert result["definition"]["coverage_key"] == "Tackles won"

    for entry in result["entries"]:
        stats = team_research_stats.team_season_stats(
            season,
            entry["persistent_team_code"],
        )
        expected = stats.get("Tackles won_per_match")
        assert entry["value"] == (float(expected) if expected is not None else None)


def test_kernel_ranking_matches_the_pre_kernel_overview_algorithm():
    analysis = season_overview_analysis("2024-25")
    result = analysis["metrics"]["Shots_per_match"]
    entries = result["entries"]

    values = [
        float(team_research_stats.team_season_stats("2024-25", row["persistent_team_code"])["Shots_per_match"])
        for row in entries
    ]
    ordered = sorted(values, reverse=True)

    for entry in entries:
        value = float(entry["value"])
        expected_rank = ordered.index(value) + 1
        expected_percentile = round(
            100.0 * (len(ordered) - expected_rank) / (len(ordered) - 1),
            1,
        )
        assert entry["rank"] == expected_rank
        assert math.isclose(entry["percentile"], expected_percentile)


def test_2024_25_xg_uses_product_ready_player_derived_representation():
    analysis = season_overview_analysis("2024-25")

    assert len(analysis["expected_goals"]) == 20
    assert {
        row["representation"] for row in analysis["expected_goals"].values()
    } == {PLAYER_MATCH_DERIVED_TEAM_MATCH}
    assert all(
        row["coverage_complete"]
        for row in analysis["expected_goals"].values()
    )
    assert all(row["observed_matches"] == 38 for row in analysis["expected_goals"].values())


def test_2023_24_player_xg_gap_remains_missing_instead_of_direct_fallback():
    analysis = season_overview_analysis("2023-24")
    xg = list(analysis["expected_goals"].values())

    assert {row["representation"] for row in xg} == {PLAYER_MATCH_DERIVED_TEAM_MATCH}
    assert sum(row["missing_matches"] for row in xg) == 2
    assert sum(not row["coverage_complete"] for row in xg) == 2
    assert all(
        row["xg_overperformance"] is None
        for row in xg
        if not row["coverage_complete"]
    )


def test_2025_26_single_season_xg_uses_complete_direct_representation():
    analysis = season_overview_analysis("2025-26")
    xg = list(analysis["expected_goals"].values())

    assert {row["representation"] for row in xg} == {DIRECT_TEAM_MATCH}
    assert all(row["coverage_complete"] for row in xg)
    assert all(row["observed_matches"] == 38 for row in xg)


def test_pre_2022_team_view_exposes_no_governed_expected_goals_route():
    analysis = season_overview_analysis("2021-22")

    assert {
        row["representation"] for row in analysis["expected_goals"].values()
    } == {NO_GOVERNED_SEASON_ROUTE}
    assert all(row["value"] is None for row in analysis["expected_goals"].values())


def test_team_view_is_projection_of_the_same_season_analysis_result():
    season = season_overview_analysis("2024-25")
    sample = season["metrics"]["points_per_match"]["entries"][0]
    team = team_overview_analysis("2024-25", sample["persistent_team_code"])

    assert team is not None
    assert tuple(item["key"] for item in team["metrics"]) == TEAM_VIEW_OVERVIEW_KEYS
    assert len(team["metrics"]) == 10
    metric = next(item for item in team["metrics"] if item["key"] == "points_per_match")
    assert metric["value"] == sample["value"]
    assert metric["rank"] == sample["rank"]
    assert metric["out_of"] == sample["out_of"]
    assert metric["percentile"] == sample["percentile"]
