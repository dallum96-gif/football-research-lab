from variable_universe import list_variables
from variable_resolver import resolve_variable, variable_definition


def test_fpl_is_a_separate_variable_family(monkeypatch):
    monkeypatch.setattr(
        "variable_universe.fpl_catalogue",
        lambda: (
            {"field_name": "total_points", "subclass": "POINTS"},
            {"field_name": "now_cost", "subclass": "PRICE_VALUE"},
        ),
    )

    rows = list_variables(season="2025-26", family="fpl")

    assert {row.name for row in rows} == {"total_points", "now_cost"}
    assert {row.family for row in rows} == {"fpl"}


def test_fpl_definition_comes_from_fpl_registry(monkeypatch):
    monkeypatch.setattr(
        "variable_resolver.fpl_variable_definition",
        lambda name: {"field_name": name, "subclass": "POINTS"},
    )

    definition = variable_definition("total_points", family="fpl", season="2025-26")

    assert definition.family == "fpl"
    assert definition.source_field == "total_points"
    assert definition.definition == "POINTS"


def test_fpl_player_resolution_uses_fpl_evidence_seam(monkeypatch):
    monkeypatch.setattr(
        "variable_resolver.fpl_player_gameweek_values",
        lambda **kwargs: {
            "query_type": "frl_fpl_variable",
            "research_family": "FPL",
            "variable": kwargs["field_name"],
            "results": [{"value": "10"}],
        },
    )
    monkeypatch.setattr(
        "variable_resolver.fpl_variable_definition",
        lambda name: {"field_name": name, "subclass": "POINTS"},
    )

    result = resolve_variable(
        "total_points",
        season="2025-26",
        player_id="123",
        gameweek="1",
        family="fpl",
    )

    assert result["research_family"] == "FPL"
    assert result["variable"] == "total_points"
    assert result["results"][0]["value"] == "10"


def test_core_family_resolution_remains_separate(monkeypatch):
    monkeypatch.setattr(
        "variable_resolver.available_fields",
        lambda family, season: (
            ("successfulDribbles",) if family == "player_match" else ()
        ),
    )

    definition = variable_definition("successfulDribbles", season="2025-26")

    assert definition.family == "player_match"
