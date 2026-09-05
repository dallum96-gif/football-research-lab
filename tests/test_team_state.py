from __future__ import annotations

from datetime import datetime, timezone

from expected_metric_routing import PLAYER_MATCH_DERIVED_TEAM_MATCH
from team_state import STATE_VERSION, fixture_team_states


def _dt(value: object) -> datetime:
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _metric(window: dict, key: str) -> dict:
    return next(row for row in window["metrics"] if row["key"] == key)


def test_fixture_team_state_excludes_target_and_future_fixtures():
    states = fixture_team_states("2025-26", "200")
    assert states["state_version"] == STATE_VERSION
    target = _dt(states["as_of"])

    for side in ("home", "away"):
        state = states[side]
        assert state["temporal_contract"]["target_kickoff_enforced"] is True
        assert state["temporal_contract"]["predictive_research_status"] == "EXPERIMENTAL_UNTIL_INFORMATION_AVAILABILITY_AUDIT"
        recent = state["windows"]["recent_5"]
        assert recent["sample_size"] == 5
        assert all(str(row["fixture_id"]) != "200" or str(row["season"]) != "2025-26" for row in recent["contributing_fixtures"])
        assert all(_dt(row["kickoff_time"]) < target for row in recent["contributing_fixtures"])


def test_team_state_keeps_xg_on_one_governed_representation():
    states = fixture_team_states("2025-26", "200")
    for side in ("home", "away"):
        recent = states[side]["windows"]["recent_5"]
        assert recent["representation_mixing_detected"] is False
        assert recent["expected_goal_representations"] == [PLAYER_MATCH_DERIVED_TEAM_MATCH]
        assert _metric(recent, "xg_for")["observed_matches"] == 5
        assert _metric(recent, "xg_against")["observed_matches"] == 5


def test_team_state_retains_expected_goals_as_unavailable_before_source_period():
    states = fixture_team_states("2020-21", "200")
    for side in ("home", "away"):
        recent = states[side]["windows"]["recent_5"]
        xg_for = _metric(recent, "xg_for")
        xg_against = _metric(recent, "xg_against")
        assert xg_for["coverage_status"] == "UNAVAILABLE"
        assert xg_against["coverage_status"] == "UNAVAILABLE"
        assert xg_for["representation"] == PLAYER_MATCH_DERIVED_TEAM_MATCH
        assert recent["expected_goal_representations"] == []


def test_team_state_preserves_contributing_fixture_evidence_and_schedule_context():
    states = fixture_team_states("2025-26", "200")
    for side in ("home", "away"):
        recent = states[side]["windows"]["recent_10"]
        assert recent["sample_size"] == 10
        assert len(recent["contributing_fixtures"]) == 10
        assert recent["schedule_strength_observed_matches"] > 0
        assert recent["derived"]["shot_share"]["observed_matches"] == 10
        assert recent["derived"]["xg_share"]["observed_matches"] == 10
