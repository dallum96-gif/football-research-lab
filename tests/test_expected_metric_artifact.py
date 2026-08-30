from expected_metric_artifact import (
    artifact_metadata,
    fixture_expected_metric_row,
    team_expected_metric_observation,
)
from expected_metric_routing import (
    EXPECTED_ASSISTS,
    EXPECTED_GOALS,
    EXPECTED_GOALS_ON_TARGET,
    PLAYER_MATCH_DERIVED_TEAM_MATCH,
)


def test_artifact_metadata_is_pinned_and_governed():
    metadata = artifact_metadata()

    assert metadata["row_count"] == 1520
    assert metadata["representation"] == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert metadata["construction_version"] == "FRL_PLAYER_DERIVED_EXPECTED_METRICS_V1"
    assert metadata["source_commit"] == "1ec7f0dc79055902251cd938650f622b0e79f3cc"
    assert metadata["representation_mixing_allowed"] is False


def test_fixture_lookup_uses_canonical_season_fixture_key():
    row = fixture_expected_metric_row("2022-23", "1")

    assert row is not None
    assert row["season"] == "2022-23"
    assert row["fixture_id"] == "1"
    assert row["representation"] == PLAYER_MATCH_DERIVED_TEAM_MATCH


def test_available_player_derived_xg_preserves_provenance():
    observation = team_expected_metric_observation(
        "2022-23",
        "1",
        "home",
        EXPECTED_GOALS,
    )

    assert observation["status"] == "AVAILABLE"
    assert observation["value"] == 1.2118
    assert observation["representation"] == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert observation["direct_source_match_id"] == "2292810"
    assert observation["player_source_match_id"] == "10385741"
    assert observation["source_commit"] == "1ec7f0dc79055902251cd938650f622b0e79f3cc"


def test_xa_blank_rows_can_contribute_structural_zero_under_governed_rule():
    observation = team_expected_metric_observation(
        "2022-23",
        "1",
        "home",
        EXPECTED_ASSISTS,
    )

    assert observation["status"] == "AVAILABLE"
    assert observation["value"] == 1.16414399
    assert observation["structural_zero_rows"] == 5
    assert observation["unsafe_missing_rows"] == 0


def test_positive_trigger_xg_gap_fails_closed():
    observation = team_expected_metric_observation(
        "2023-24",
        "45",
        "home",
        EXPECTED_GOALS,
    )

    assert observation["status"] == "MISSING_POSITIVE_TRIGGER_INPUT"
    assert observation["value"] is None
    assert observation["unsafe_missing_rows"] == 5


def test_xgot_gap_fails_closed_without_direct_fallback():
    observation = team_expected_metric_observation(
        "2022-23",
        "111",
        "away",
        EXPECTED_GOALS_ON_TARGET,
    )

    assert observation["status"] == "MISSING_POSITIVE_TRIGGER_INPUT"
    assert observation["value"] is None


def test_outside_materialized_period_is_unavailable_not_fabricated():
    observation = team_expected_metric_observation(
        "2021-22",
        "1",
        "home",
        EXPECTED_GOALS,
    )

    assert observation["status"] == "UNAVAILABLE"
    assert observation["value"] is None
    assert observation["reason"] == "FIXTURE_OUTSIDE_MATERIALIZED_ARTIFACT"
