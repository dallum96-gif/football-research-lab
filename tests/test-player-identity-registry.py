import player_identity_registry


def test_module_shape():
    assert hasattr(player_identity_registry, "build_registry")
    assert hasattr(player_identity_registry, "write_registry")
    assert player_identity_registry.FIELDS[0] == "season"


def test_registry_uses_canonical_audit_exact_rows(monkeypatch):
    monkeypatch.setattr(
        player_identity_registry.player_identity_audit,
        "SEASONS",
        ("2025-26",),
    )
    monkeypatch.setattr(
        player_identity_registry.player_identity_audit,
        "audit_season",
        lambda season: {
            "exact": [{
                "fpl_player_code": "1",
                "fpl_name": "Example Player",
                "source_player_id": "99",
                "team_code": "ABC",
            }],
            "missing": [],
            "ambiguous": [],
        },
    )
    monkeypatch.setattr(
        player_identity_registry.player_identity_audit,
        "normalize_name",
        lambda value: value.casefold(),
    )

    rows = player_identity_registry.build_registry()
    assert len(rows) == 1
    assert rows[0]["fpl_element"] == "1"
    assert rows[0]["source_player_id"] == "99"
    assert rows[0]["identity_status"] == "VERIFIED"
    assert rows[0]["match_method"] == "EXACT_NAME_TEAM"
