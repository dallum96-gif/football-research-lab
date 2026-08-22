import audit_searchable_field_universe as audit


def test_universe_counts_catalog_rows(monkeypatch):
    monkeypatch.setattr(
        audit,
        "build_catalog",
        lambda: (
            {
                "family": "team_match",
                "source_field": "goalsFor",
                "registry_status": "exposed",
                "coverage_class": "CORE_DECADE",
                "first_seen_season": "2016-17",
                "last_seen_season": "2025-26",
                "seasons_present": 10,
                "seasons_total": 10,
            },
            {
                "family": "player_match",
                "source_field": "customMetric",
                "registry_status": "UNCATALOGUED",
                "coverage_class": "SINGLE_SEASON",
                "first_seen_season": "2025-26",
                "last_seen_season": "2025-26",
                "seasons_present": 1,
                "seasons_total": 10,
            },
        ),
    )
    report = audit.run()
    assert report["total_fields"] == 2
    assert report["by_family"] == {"team_match": 1, "player_match": 1}
    assert report["by_status"]["UNCATALOGUED"] == 1
    assert report["uncatalogued"][0]["source_field"] == "customMetric"
