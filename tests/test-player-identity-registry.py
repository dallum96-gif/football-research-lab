import player_identity_registry


def test_module_shape():
    assert hasattr(player_identity_registry, "build_registry")
    assert hasattr(player_identity_registry, "write_registry")
    assert player_identity_registry.FIELDS[0] == "season"


def test_registry_uses_canonical_audit_exact_rows(monkeypatch):
    monkeypatch.setattr(
        player_identity_registry,
        "_canonical_exact_rows",
        lambda: [{
            "season": "2025-26",
            "fpl_element": "1",
            "fpl_name_normalized": "example player",
            "team_code": "ABC",
            "source_player_id": "99",
            "match_method": "EXACT_NAME_TEAM",
            "confidence": "VERIFIED",
            "identity_status": "VERIFIED",
            "evidence_basis": "test",
        }],
    )
    monkeypatch.setattr(player_identity_registry, "_historical_index_candidates", lambda: [])

    rows = player_identity_registry.build_registry()
    assert len(rows) == 1
    assert rows[0]["fpl_element"] == "1"
    assert rows[0]["source_player_id"] == "99"
    assert rows[0]["identity_status"] == "VERIFIED"
    assert rows[0]["match_method"] == "EXACT_NAME_TEAM"


def test_registry_promotes_non_conflicting_historical_index_candidate(monkeypatch):
    monkeypatch.setattr(player_identity_registry, "_canonical_exact_rows", lambda: [])
    monkeypatch.setattr(
        player_identity_registry,
        "_historical_index_candidates",
        lambda: [{
            "season": "2016-17",
            "fpl_element": "16",
            "fpl_name_normalized": "aaron ramsey",
            "team_code": "",
            "source_player_id": "23571",
            "match_method": "HISTORICAL_PL_INDEX_NAME_PLAYER_MATCH",
            "confidence": "VERIFIED",
            "identity_status": "VERIFIED",
            "evidence_basis": "historical evidence",
        }],
    )

    rows = player_identity_registry.build_registry()
    assert len(rows) == 1
    assert rows[0]["season"] == "2016-17"
    assert rows[0]["fpl_element"] == "16"
    assert rows[0]["source_player_id"] == "23571"
    assert rows[0]["identity_status"] == "VERIFIED"
    assert rows[0]["match_method"] == "HISTORICAL_PL_INDEX_NAME_PLAYER_MATCH"


def test_registry_does_not_duplicate_same_identity_from_second_route(monkeypatch):
    canonical = {
        "season": "2016-17",
        "fpl_element": "16",
        "fpl_name_normalized": "aaron ramsey",
        "team_code": "3",
        "source_player_id": "23571",
        "match_method": "EXACT_NAME_TEAM",
        "confidence": "VERIFIED",
        "identity_status": "VERIFIED",
        "evidence_basis": "canonical exact",
    }
    historical = {**canonical, "match_method": "HISTORICAL_PL_INDEX_NAME_PLAYER_MATCH"}
    monkeypatch.setattr(player_identity_registry, "_canonical_exact_rows", lambda: [canonical])
    monkeypatch.setattr(player_identity_registry, "_historical_index_candidates", lambda: [historical])

    rows = player_identity_registry.build_registry()
    assert len(rows) == 1
    assert rows[0]["match_method"] == "EXACT_NAME_TEAM"


def test_registry_rejects_conflicting_routes(monkeypatch):
    canonical = {
        "season": "2016-17",
        "fpl_element": "16",
        "fpl_name_normalized": "aaron ramsey",
        "team_code": "3",
        "source_player_id": "23571",
        "match_method": "EXACT_NAME_TEAM",
        "confidence": "VERIFIED",
        "identity_status": "VERIFIED",
        "evidence_basis": "canonical exact",
    }
    historical = {**canonical, "source_player_id": "999999", "match_method": "HISTORICAL_PL_INDEX_NAME_PLAYER_MATCH"}
    monkeypatch.setattr(player_identity_registry, "_canonical_exact_rows", lambda: [canonical])
    monkeypatch.setattr(player_identity_registry, "_historical_index_candidates", lambda: [historical])

    assert player_identity_registry.build_registry() == []


def test_registry_does_not_promote_missing_or_ambiguous_rows(monkeypatch):
    monkeypatch.setattr(player_identity_registry, "_canonical_exact_rows", lambda: [])
    monkeypatch.setattr(player_identity_registry, "_historical_index_candidates", lambda: [])

    assert player_identity_registry.build_registry() == []


if __name__ == "__main__":
    tests = [
        test_module_shape,
        test_registry_uses_canonical_audit_exact_rows,
        test_registry_promotes_non_conflicting_historical_index_candidate,
        test_registry_does_not_duplicate_same_identity_from_second_route,
        test_registry_rejects_conflicting_routes,
        test_registry_does_not_promote_missing_or_ambiguous_rows,
    ]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER IDENTITY REGISTRY TESTS: {len(tests)}/{len(tests)}")
