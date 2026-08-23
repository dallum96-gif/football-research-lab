from entity_attachment_resolver import (
    AttachmentEdge,
    edge_statuses,
    fully_attached,
    resolve_observation,
)


def test_partial_edges_are_preserved_independently():
    record = resolve_observation(
        {
            "observation_id": "obs-1",
            "variable_id": "var-1",
            "season": "2025-26",
            "source_record_id": "src-1",
            "source_player_id": "p-7",
            "source_match_id": "m-8",
            "source_team_id": "t-9",
        },
        fixture={
            "status": "VERIFIED",
            "entity_id": "fixture-8",
            "identity_contract": "canonical_fixture_to_source_match",
        },
        home_team={
            "status": "VERIFIED",
            "entity_id": "team-season-1",
        },
        away_team={
            "status": "VERIFIED",
            "entity_id": "team-season-2",
        },
        player={
            "status": "UNRESOLVED",
            "identity_contract": "player_identity_to_player_match_observations",
        },
    )

    assert edge_statuses(record) == {
        "fixture": "VERIFIED",
        "home_team": "VERIFIED",
        "away_team": "VERIFIED",
        "player": "UNRESOLVED",
    }
    assert not fully_attached(record)
    assert record.fixture.entity_id == "fixture-8"
    assert record.player.entity_id is None


def test_fully_attached_requires_verified_applicable_edges():
    record = resolve_observation(
        {"observation_id": "obs-2", "variable_id": "var-2"},
        fixture={"status": "VERIFIED", "entity_id": "f1"},
        home_team={"status": "VERIFIED", "entity_id": "ht1"},
        away_team={"status": "VERIFIED", "entity_id": "at1"},
        player={"status": "VERIFIED", "entity_id": "p1"},
    )
    assert fully_attached(record)


def test_verified_edge_requires_entity_id():
    try:
        AttachmentEdge(status="VERIFIED")
    except ValueError as exc:
        assert "entity_id" in str(exc)
    else:
        raise AssertionError("Expected VERIFIED edge without entity_id to fail")
