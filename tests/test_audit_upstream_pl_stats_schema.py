from audit_upstream_pl_stats_schema import audit, classify_path, discover_files


def test_classify_pl_stats_grains():
    assert classify_path("pl_stats/Arsenal_3/events_stats/2016-17_events_stats.csv") == "team_match"
    assert classify_path("pl_stats/Arsenal_3/players_match_stats/2016-17_players_match_stats.csv") == "player_match"
    assert classify_path("pl_stats/Arsenal_3/players_stats/2016-17_players_stats.csv") == "player_season"
    assert classify_path("pl_stats/Arsenal_3/squad/2016-17_squad.csv") == "squad"
    assert classify_path("pl_stats/_merged/events/2016-17_events_stats.csv") == "team_match"
    assert classify_path("README.md") is None


def test_discover_files_filters_to_supported_csv_surfaces():
    payload = {
        "tree": [
            {"type": "blob", "path": "pl_stats/A/events_stats/a.csv", "sha": "1"},
            {"type": "blob", "path": "pl_stats/A/squad/a.csv", "sha": "2"},
            {"type": "blob", "path": "pl_stats/A/badges.svg", "sha": "3"},
        ]
    }
    rows = discover_files(payload)
    assert len(rows) == 2
    assert {row["grain"] for row in rows} == {"team_match", "squad"}


def test_audit_deduplicates_by_grain_and_field(monkeypatch):
    files = [
        {"path": "a.csv", "sha": "same", "grain": "team_match", "raw_url": "u1"},
        {"path": "b.csv", "sha": "same", "grain": "team_match", "raw_url": "u2"},
        {"path": "c.csv", "sha": "other", "grain": "squad", "raw_url": "u3"},
    ]
    monkeypatch.setattr(
        "audit_upstream_pl_stats_schema.load_cache",
        lambda: {"same": ["matchId", "attendance"], "other": ["playerId", "birthDate"]},
    )
    out = audit(files, workers=1)
    pairs = {(row["grain"], row["field_name"]) for row in out}
    assert ("team_match", "attendance") in pairs
    assert ("squad", "birthDate") in pairs
    attendance = next(row for row in out if row["grain"] == "team_match" and row["field_name"] == "attendance")
    assert attendance["file_count"] == "2"
    assert attendance["unique_blob_count"] == "1"
