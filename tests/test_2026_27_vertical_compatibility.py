from __future__ import annotations

import pytest
from fastapi import HTTPException

import fpl_variable_access
import query_api
import research_access
import source_family_adapters
import team_analysis_kernel
import team_research_stats
import variable_resolver
from api.frl_api import get_fixture_detail, get_team_stats_overview
from api.player_performance import fixture_player_performance
from api.team_stats_rankings import get_team_stats_league_rankings


SEASON = "2026-27"


def test_current_season_fixture_and_table_keep_completed_and_scheduled_states_distinct() -> None:
    assert SEASON in query_api.list_seasons()

    completed = get_fixture_detail(SEASON, "1")
    assert completed.fixture.home_team_name == "Arsenal"
    assert (completed.fixture.home_score, completed.fixture.away_score) == (3, 0)
    assert completed.stats is None
    assert completed.player_match_status == "UNAVAILABLE"

    scheduled = get_fixture_detail(SEASON, "11")
    assert scheduled.fixture.home_score is None
    assert scheduled.fixture.away_score is None
    assert scheduled.stats is None
    assert scheduled.player_match_status == "UNAVAILABLE"

    table = query_api.league_table(SEASON)
    assert len(table["teams"]) == 20
    assert sum(int(row["played"]) for row in table["teams"]) == 20

    with pytest.raises(HTTPException) as exc_info:
        get_fixture_detail(SEASON, "9999")
    assert exc_info.value.status_code == 404


def test_fpl_player_fixture_resolution_is_explicit_and_preserves_zero_as_observed() -> None:
    result = variable_resolver.resolve_variable(
        "history[].expected_goals",
        season=SEASON,
        fixture_id="1",
        player_id="2",
        family="fpl",
    )

    assert len(result["results"]) == 1
    row = result["results"][0]
    assert row["fixture_id"] == "1"
    assert row["source_fixture_code"] == "2645195"
    assert row["source_player_code"] == "109745"
    assert row["participation_status"] == "REGISTERED_ZERO_MINUTES"
    assert row["value"] == "0.00"
    assert result["provenance"]["source_representation"] == "FPL_PLAYER_FIXTURE"
    assert result["provenance"]["historical_opta_equivalence_asserted"] is False
    assert result["provenance"]["source_release_shas"] == [
        "1ec7f0dc79055902251cd938650f622b0e79f3cc"
    ]


def test_fpl_fixture_and_player_fixture_surfaces_are_not_silently_coalesced() -> None:
    player_rows = variable_resolver.resolve_variable(
        "history[].expected_goals",
        season=SEASON,
        fixture_id="1",
        family="fpl",
    )
    fixture_rows = variable_resolver.resolve_variable(
        "fixtures[].finished",
        season=SEASON,
        fixture_id="1",
        family="fpl",
    )

    assert len(player_rows["results"]) == 62
    assert player_rows["provenance"]["source_representation"] == "FPL_PLAYER_FIXTURE"
    assert fixture_rows["results"] == [
        {
            "season": SEASON,
            "fixture_id": "1",
            "source_field": "finished",
            "value": "True",
        }
    ]
    assert fixture_rows["provenance"]["source_representation"] == "FPL_FIXTURE"

    with pytest.raises(fpl_variable_access.FPLVariableUnavailableError):
        variable_resolver.resolve_variable(
            "elements[].total_points",
            season=SEASON,
            fixture_id="1",
            family="fpl",
        )


def test_ura_exposes_current_player_fixture_evidence_and_representation_coverage() -> None:
    result = research_access.query(
        research_access.ResearchRequest(
            variable="history[].expected_goals",
            season=SEASON,
            family="fpl",
            fixture_id="1",
            player_id="1",
        )
    )
    assert len(result["results"]) == 1
    assert result["results"][0]["value"] == "0.00"
    assert result["provenance"]["source_representation"] == "FPL_PLAYER_FIXTURE"

    coverage = research_access.coverage(
        variable="history[].expected_goals",
        seasons=[SEASON],
        family="fpl",
    )
    assert coverage["population"] == 610
    assert coverage["observed"] == 610
    assert coverage["results"][0]["source_representation"] == "FPL_PLAYER_FIXTURE"


def test_current_player_identity_preserves_cross_source_and_source_native_states() -> None:
    verified = source_family_adapters.resolve_fpl_player_identity(SEASON, "2")
    source_native = source_family_adapters.resolve_fpl_player_identity(SEASON, "1")

    assert verified["identity_status"] == "VERIFIED"
    assert verified["frl_player_source_id"] == "232422"
    assert verified["verified"] is True
    assert source_native["identity_status"] == "SOURCE_NATIVE_VERIFIED"
    assert source_native["frl_player_source_id"] == "581310"
    assert source_native["verified"] is True


def test_team_stats_use_current_results_but_fail_closed_for_absent_team_match_metrics() -> None:
    stats = team_research_stats.team_season_stats(SEASON, "3")
    assert stats["matches"] == 1
    assert stats["goals_for"] == 3.0
    assert stats["goals_against"] == 0.0
    assert stats["points_per_match"] == 3.0
    assert stats["metric_coverage"]["Shots"]["observed_matches"] == 0
    assert stats["metric_coverage"]["Shots"]["missing_matches"] == 1
    assert stats["metric_coverage"]["Shots"]["coverage_status"] == "UNAVAILABLE"

    analysis = team_analysis_kernel.team_overview_analysis(SEASON, "3")
    assert analysis is not None
    assert analysis["expected_goals"]["value"] is None
    assert analysis["expected_goals"]["representation"] == "NO_GOVERNED_SEASON_ROUTE"
    assert "FPL" in analysis["expected_goals"]["note"]

    overview = get_team_stats_overview(SEASON, "3")
    availability = {item.key: item for item in overview.availability}
    assert availability["points_per_match"].status == "AVAILABLE"
    assert availability["Shots_per_match"].status == "UNAVAILABLE"
    assert availability["expected_goals_per_match"].status == "UNAVAILABLE"

    rankings = get_team_stats_league_rankings(SEASON)
    by_metric = {metric.key: metric for metric in rankings.metrics}
    assert len(by_metric["points_per_match"].entries) == 20
    assert all(row.value is not None for row in by_metric["points_per_match"].entries)
    assert all(row.value is None for row in by_metric["Shots_per_match"].entries)


def test_fixture_player_performance_uses_source_native_fpl_metrics_without_opta_claim() -> None:
    response = fixture_player_performance(SEASON, "1")
    home = {metric.key: metric for metric in response.home.metrics}
    away = {metric.key: metric for metric in response.away.metrics}

    assert response.home.status == "AVAILABLE"
    assert response.away.status == "AVAILABLE"
    assert home["expected_goals"].player is not None
    assert home["expected_goals"].player.player_name == "Bukayo Saka"
    assert home["expected_goals"].player.value == 0.64
    assert home["saves"].player is not None
    assert home["saves"].player.value == 1.0
    assert away["defensive_contribution"].player is not None
    assert away["defensive_contribution"].player.value == 10.0
    for metric in response.home.metrics + response.away.metrics:
        assert metric.provenance["source_representation"] == "FPL_PLAYER_FIXTURE"
        assert metric.provenance["historical_opta_equivalence_asserted"] is False

