from squad_source_adapter import resolve_team_season, squad_context


def payload():
    return {
        "payload": {
            "id": {"competitionId": "8", "seasonId": "2025"},
            "team": {"id": "14", "name": "Liverpool", "shortName": "Liverpool"},
            "players": [{"id": "116535", "position": "Goalkeeper"}],
        }
    }


def test_squad_context_requires_explicit_source_keys():
    context = squad_context(payload())
    assert context["source_season_id"] == "2025"
    assert context["source_team_id"] == "14"


def test_squad_route_verifies_unique_team_season():
    registry = ({
        "season": "2025-26",
        "local_team_id": "14",
        "team_season_id": "2025-26-14",
        "canonical_name": "Liverpool",
        "persistent_team_code": "14",
        "mapping_status": "VERIFIED",
    },)
    result = resolve_team_season(
        payload(),
        source_season_map={"2025": "2025-26"},
        registry=registry,
    )
    assert result["status"] == "VERIFIED_TEAM_SEASON_ROUTE"
    assert result["team_season_id"] == "2025-26-14"


def test_squad_route_fails_closed_without_audited_season_map():
    result = resolve_team_season(payload(), source_season_map={}, registry=())
    assert result["status"] == "UNRESOLVED_SEASON"
