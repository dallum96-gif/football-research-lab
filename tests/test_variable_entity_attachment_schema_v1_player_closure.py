from materialize_variable_entity_attachment_schema_v1 import _player_identity_attachment


def test_direct_verified_registry_and_research_identity_closes_player():
    status, entity_id, source_ref, basis = _player_identity_attachment(
        "2023-24",
        "1003339",
        [{"identity_status": "VERIFIED"}],
        {"1003339": {"jarell quansah"}},
    )
    assert status == "VERIFIED"
    assert entity_id == "research:jarell quansah"
    assert source_ref == "1003339"
    assert "verified registry" in basis


def test_ambiguous_research_identity_is_reviewed():
    status, entity_id, source_ref, basis = _player_identity_attachment(
        "2023-24",
        "123",
        [],
        {"123": {"player one", "player two"}},
    )
    assert status == "REVIEW"
    assert entity_id == ""
    assert source_ref == "123"
    assert "multiple Player Research identities" in basis


def test_missing_research_identity_remains_unresolved():
    status, entity_id, source_ref, basis = _player_identity_attachment(
        "2023-24",
        "456",
        [],
        {},
    )
    assert status == "UNRESOLVED"
    assert entity_id == ""
    assert source_ref == "456"
    assert "no existing verified Player Research closure" in basis
