import source_field_catalog as catalog


def test_catalog_classifies_discovered_field_coverage(monkeypatch):
    values = {
        ("team_match", "custom"): {"2016-17", "2017-18", "2018-19"},
    }

    monkeypatch.setattr(catalog, "_source_fields", lambda family, season: (
        ("custom",) if (family, "custom") in values and season in values[(family, "custom")] else ()
    ))

    rows = catalog.build_catalog(
        seasons=("2016-17", "2017-18", "2018-19"),
        families=("team_match",),
    )

    row = next(item for item in rows if item["source_field"] == "custom")
    assert row["seasons_present"] == 3
    assert row["coverage_class"] == "CORE_DECADE"
    assert row["registry_status"] == "UNCATALOGUED"


def test_catalog_preserves_curated_registry_mapping(monkeypatch):
    monkeypatch.setattr(catalog, "_source_fields", lambda family, season: ("goalsFor",))

    rows = catalog.build_catalog(
        seasons=("2025-26",),
        families=("team_match",),
    )

    row = next(item for item in rows if item["source_field"] == "goalsFor")
    assert row["registry_status"] == "retained"


def test_field_metadata_fails_closed_for_unknown_field(monkeypatch):
    monkeypatch.setattr(catalog, "_source_fields", lambda family, season: ("known",))
    try:
        catalog.field_metadata("team_match", "unknown", seasons=("2025-26",))
    except ValueError as exc:
        assert "Unknown source field" in str(exc)
    else:
        raise AssertionError("Unknown source field should fail closed")
