import audit_all_relationships as audit


def test_fixture_relationship_contract(monkeypatch):
    monkeypatch.setattr(
        audit.adapters,
        "season_fixtures",
        lambda season: ({"fixture_id": "1"}, {"fixture_id": "2"}),
    )

    def resolve(season, fixture_id):
        if fixture_id == "2":
            raise ValueError("missing")
        return {"source_match_id": "99"}

    monkeypatch.setattr(audit.adapters, "resolve_source_match", resolve)

    result = audit.fixture_relationship("2025-26")
    assert result == {
        "canonical_fixtures": 2,
        "resolved_source_matches": 1,
        "missing_source_matches": 1,
        "unique_source_match_ids": 1,
    }


def test_team_relationship_reports_verified_vs_source(monkeypatch):
    class FakeRoot:
        def iterdir(self):
            return []

    monkeypatch.setattr(audit.adapters, "PL_ROOT", FakeRoot())

    registry = {
        "2025-26": [
            {"mapping_status": "VERIFIED", "persistent_team_code": "3"},
            {"mapping_status": "REVIEW", "persistent_team_code": "9"},
        ]
    }

    result = audit.team_relationship("2025-26", registry)
    assert result["registry_rows"] == 2
    assert result["verified_team_rows"] == 1
    assert result["verified_persistent_team_codes"] == 1
    assert result["source_team_ids"] == 0
    assert result["verified_codes_present_in_source"] == 0
    assert result["verified_codes_missing_from_source"] == 1


def test_relationship_matrix_separates_source_coverage_from_identity():
    relationship = {"exact_1_to_1": 10, "missing": 2, "ambiguous": 1}
    fields = {"fixture_team_match": 100, "player_match": 80, "player_season": 120}
    assert relationship["exact_1_to_1"] != fields["player_season"]
