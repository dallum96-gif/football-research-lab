from source_family_adapters import canonical_fixture, fixture_metadata, resolve_source_match


def test_canonical_fixture_missing_is_fail_closed():
    assert canonical_fixture("2026-27", "2645195") is None


def test_resolve_source_match_rejects_non_canonical_fixture():
    try:
        resolve_source_match("2026-27", "2645195")
    except ValueError as exc:
        assert "Canonical fixture not found" in str(exc)
    else:
        raise AssertionError("Expected non-canonical live fixture to fail closed")


def test_fixture_metadata_exposes_verified_source_fields(monkeypatch):
    import source_family_adapters

    monkeypatch.setattr(
        source_family_adapters,
        "resolve_source_match",
        lambda season, fixture_id: {
            "season": season,
            "fixture_id": fixture_id,
            "source_match_id": "2645195",
            "relationship_contract": "canonical_fixture_to_source_match",
            "relationship_status": "VERIFIED",
            "home": {
                "ground": "Emirates Stadium, London",
                "attendance": "60098",
                "halfTimeFor": "2",
                "result": "H",
                "kickoff": "2026-08-21 20:00:00",
            },
            "away": {
                "ground": "Emirates Stadium, London",
                "attendance": "60098",
                "halfTimeFor": "0",
                "result": "A",
                "kickoff": "2026-08-21 20:00:00",
            },
        },
    )

    metadata = fixture_metadata("2026-27", "1")
    assert metadata["source_match_id"] == "2645195"
    assert metadata["ground"] == "Emirates Stadium, London"
    assert metadata["attendance"] == 60098
    assert metadata["half_time_home_score"] == 2
    assert metadata["half_time_away_score"] == 0
    assert metadata["metadata_consistent"] is True


def test_verified_source_match_carries_relationship_contract(monkeypatch):
    import source_family_adapters

    monkeypatch.setattr(source_family_adapters, "canonical_fixture", lambda season, fixture_id: {"season": season, "fixture_id": fixture_id})
    monkeypatch.setattr(
        source_family_adapters,
        "fixture_source_match",
        lambda fixture, identity_rows: (
            "123",
            {"team_id": "3", "ground": "Emirates Stadium, London"},
            {"team_id": "9", "ground": "Emirates Stadium, London"},
        ),
    )
    monkeypatch.setattr(source_family_adapters, "_identity_rows", lambda: tuple())

    result = resolve_source_match("2026-27", "1")
    assert result["relationship_contract"] == "canonical_fixture_to_source_match"
    assert result["relationship_status"] == "VERIFIED"
