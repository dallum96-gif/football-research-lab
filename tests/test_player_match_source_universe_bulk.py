from __future__ import annotations

from scripts.audit_player_match_source_universe import build_audit
from raw_team_stat_research import raw_team_stat_fields
from rich_player_projection import aggregate_source_records
from source_field_registry import fields_for_family


def _statuses(family: str) -> dict[str, str]:
    return {spec.source_field: spec.semantic_status for spec in fields_for_family(family)}


def test_complete_player_match_decade_union_is_accounted_for():
    audit = build_audit()
    assert audit["observed_source_field_union"] == 86
    assert audit["all_observed_fields_accounted_for"] is True
    assert audit["uncatalogued_observed_fields"] == []
    assert audit["registry_status_counts_for_observed_fields"] == {
        "exposed": 81,
        "restricted": 1,
        "retained": 4,
    }


def test_partial_period_player_fields_are_included_not_discarded():
    audit = build_audit()
    rows = {row["source_field"]: row for row in audit["rows"]}
    assert rows["expectedGoals"]["seasons"] == ["2022-23", "2023-24", "2024-25", "2025-26"]
    assert rows["ballCarriesCount"]["seasons"] == ["2024-25", "2025-26"]
    assert rows["metersCoveredSprintingKm"]["seasons"] == ["2025-26"]
    assert rows["metersCoveredWalkingKm"]["registry_status"] == "exposed"


def test_stale_player_match_dribble_aliases_fail_closed_and_real_contest_fields_are_exposed():
    statuses = _statuses("player_match")
    assert statuses["successfulDribbles"] == "restricted"
    assert statuses["unsuccessfulDribbles"] == "restricted"
    assert statuses["totalContest"] == "exposed"
    assert statuses["wonContest"] == "exposed"


def test_rich_player_dribble_projection_uses_contest_fields():
    records = (
        {"totalContest": "6", "wonContest": "4"},
        {"totalContest": "4", "wonContest": "2"},
    )
    result = aggregate_source_records(records, {"totalContest", "wonContest"})
    assert result["successful_dribbles"] == 6.0
    assert result["unsuccessful_dribbles"] == 4.0


def test_all_249_raw_team_paths_have_a_generic_raw_route_and_59_remain_raw_only_representation():
    raw = set(raw_team_stat_fields())
    registered = set(_statuses("team_match"))
    assert len(raw) == 249
    assert len(raw - registered) == 59
