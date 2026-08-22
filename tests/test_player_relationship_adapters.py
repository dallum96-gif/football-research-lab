import player_relationship_adapters as pra


def test_unknown_legacy_fpl_season_is_unavailable(monkeypatch):
    monkeypatch.setattr(pra, "_identity_rows", lambda: ({"season": "2025-26", "fpl_element": "1", "source_player_id": "9"},))
    result = pra.resolve_fpl_player_identity("2016-17", "1")
    assert result["relationship_status"] == "UNAVAILABLE"
    assert result["verified"] is False


def test_missing_element_in_testable_season_is_unresolved(monkeypatch):
    monkeypatch.setattr(pra, "_identity_rows", lambda: ({"season": "2025-26", "fpl_element": "1", "source_player_id": "9"},))
    result = pra.resolve_fpl_player_identity("2025-26", "999")
    assert result["relationship_status"] == "UNRESOLVED"


def test_unique_fpl_identity_is_verified(monkeypatch):
    monkeypatch.setattr(pra, "_identity_rows", lambda: ({
        "season": "2025-26",
        "fpl_element": "1",
        "source_player_id": "9",
        "identity_status": "VERIFIED",
    },))
    result = pra.resolve_fpl_player_identity("2025-26", "1")
    assert result["relationship_status"] == "VERIFIED"
    assert result["frl_player_source_id"] == "9"


def test_player_season_requires_unique_source_id(monkeypatch):
    monkeypatch.setattr(pra, "player_season_source_rows", lambda season: ({"playerId": "9", "playerName": "One"},))
    result = pra.source_player_season_identity("2025-26", "9")
    assert result["relationship_status"] == "VERIFIED"
    assert result["player_season"]["playerName"] == "One"


def test_missing_player_match_observation_is_not_identity_failure(monkeypatch):
    monkeypatch.setattr(pra, "resolve_source_match", lambda season, fixture_id: {"relationship_status": "VERIFIED"})
    monkeypatch.setattr(pra, "player_match_source_rows", lambda season, fixture_id: ())
    monkeypatch.setattr(pra, "source_player_id", lambda row: row.get("playerId"))
    result = pra.player_match_observation_status("2025-26", "1", "9", player_identity_verified=True)
    assert result["relationship_contract"] == "player_identity_to_player_match_observations"
    assert result["relationship_status"] == "UNAVAILABLE"
    assert result["observation_present"] is False
