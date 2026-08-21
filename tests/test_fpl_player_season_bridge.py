import audit_fpl_player_season_bridge as audit


def test_normalize_name_handles_diacritics_and_punctuation():
    assert audit.normalize_name("Naby Keïta") == "naby keita"
    assert audit.normalize_name("Georges-Kévin N'Koudou") == "georges kevin nkoudou"


def test_distinct_fpl_identity_keys_are_season_scoped(monkeypatch):
    rows = {
        "2020-21": (
            {"element": "10", "name": "Alex Example", "team_code": "3"},
            {"element": "10", "name": "Alex Example", "team_code": "3"},
        )
    }

    monkeypatch.setattr(audit.player_research, "_load_season_rows", lambda season: rows[season])
    result = audit.distinct_fpl_identities(("2020-21",))

    assert len(result) == 1
    assert result[0].element == "10"


def test_audit_is_read_only_and_fail_closed_on_ambiguous_name(monkeypatch):
    fpl = ({"_season": "2020-21", "element": "10", "name": "Ben Davies", "team_code": "3"},)
    source = (
        {"season": "2020-21", "playerId": "111", "playerName": "Ben Davies", "team_name": "Club A"},
        {"season": "2020-21", "playerId": "222", "playerName": "Ben Davies", "team_name": "Club B"},
    )

    monkeypatch.setattr(audit, "distinct_fpl_identities", lambda seasons: tuple(
        audit.FPLIdentity("2020-21", "10", "Ben Davies", "3")
    for _ in fpl))
    monkeypatch.setattr(audit, "player_season_rows", lambda seasons: source)
    monkeypatch.setattr(audit, "verified_team_names", lambda: {("2020-21", "3"): "Club A"})

    report = audit.audit(("2020-21",))

    assert report["distinct_fpl_identities"] == 1
    assert report["ambiguous_name"] == 1
    assert report["unique_with_team_evidence"] == 0
    assert report["outcomes"][0]["candidate_source_player_ids"] == ["111", "222"]
