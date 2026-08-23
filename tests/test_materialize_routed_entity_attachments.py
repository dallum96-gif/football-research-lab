from materialize_routed_entity_attachments import _team_season_id


def test_team_season_resolution_requires_unique_verified_match():
    registry = ({
        "season": "2025-26",
        "local_team_id": "14",
        "team_season_id": "2025-26-14",
        "mapping_status": "VERIFIED",
    },)
    assert _team_season_id("2025-26", "14", list(registry)) == ("2025-26-14", "VERIFIED")


def test_team_season_resolution_fails_closed_on_ambiguity():
    registry = (
        {"season": "2025-26", "local_team_id": "14", "team_season_id": "a", "mapping_status": "VERIFIED"},
        {"season": "2025-26", "local_team_id": "14", "team_season_id": "b", "mapping_status": "VERIFIED"},
    )
    assert _team_season_id("2025-26", "14", list(registry)) == ("", "AMBIGUOUS_OR_MISSING")
