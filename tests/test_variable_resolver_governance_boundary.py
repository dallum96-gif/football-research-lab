from __future__ import annotations

import pytest

import research_field_query
import variable_resolver


def _available_only(family_name: str, field_name: str):
    def _available(family: str, season: str):
        return (field_name,) if family == family_name else tuple()
    return _available


def test_exposed_registry_field_remains_reusable(monkeypatch):
    monkeypatch.setattr(
        variable_resolver,
        "available_fields",
        _available_only("team_match", "totalPass"),
    )

    definition = variable_resolver.variable_definition(
        "totalPass", family="team_match", season="2025-26"
    )

    assert definition.status == "exposed"
    assert definition.source_field == "totalPass"


def test_retained_registry_field_is_not_silently_exposed(monkeypatch):
    monkeypatch.setattr(
        variable_resolver,
        "available_fields",
        _available_only("team_match", "ground"),
    )

    definition = variable_resolver.variable_definition(
        "ground", family="team_match", season="2025-26"
    )

    assert definition.status == "retained"
    with pytest.raises(variable_resolver.VariableUnavailableError, match="retained"):
        variable_resolver.resolve_variable(
            "ground",
            family="team_match",
            season="2025-26",
            fixture_id="1",
        )


def test_discovered_uncatalogued_field_is_not_silently_exposed(monkeypatch):
    monkeypatch.setattr(
        variable_resolver,
        "available_fields",
        _available_only("team_match", "mysteryMetric"),
    )

    definition = variable_resolver.variable_definition(
        "mysteryMetric", family="team_match", season="2025-26"
    )

    assert definition.status == "uncatalogued"
    with pytest.raises(variable_resolver.VariableUnavailableError, match="uncatalogued"):
        variable_resolver.resolve_variable(
            "mysteryMetric",
            family="team_match",
            season="2025-26",
            fixture_id="1",
        )


def test_uncatalogued_source_field_remains_available_for_evidence_first_research(monkeypatch):
    monkeypatch.setattr(
        research_field_query,
        "available_fields",
        _available_only("team_match", "mysteryMetric"),
    )
    monkeypatch.setattr(
        research_field_query,
        "team_match_source_rows",
        lambda season, fixture_id: (
            {"matchId": "100", "team_id": "10", "mysteryMetric": "7"},
            {"matchId": "100", "team_id": "20", "mysteryMetric": "3"},
        ),
    )
    monkeypatch.setattr(research_field_query, "build_catalog", lambda **kwargs: tuple())
    monkeypatch.setattr(research_field_query, "fields_for_family", lambda family: tuple())

    result = research_field_query.fixture_field_values(
        "2025-26", "1", "mysteryMetric"
    )

    assert result["registry_status"] == "UNCATALOGUED"
    assert [row["value"] for row in result["results"]] == ["7", "3"]
