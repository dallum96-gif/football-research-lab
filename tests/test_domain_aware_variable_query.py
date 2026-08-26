from variable_universe import list_variables, resolve_all


def test_fpl_domain_is_discoverable_without_entering_core_families(monkeypatch):
    monkeypatch.setattr(
        "variable_universe.fpl_catalogue",
        lambda: (
            {"field_name": "total_points", "subclass": "FPL Points"},
            {"field_name": "now_cost", "subclass": "Price & Value"},
        ),
    )

    rows = list_variables(season="2025-26", family="fpl")

    assert {row.name for row in rows} == {"total_points", "now_cost"}
    assert {row.family for row in rows} == {"fpl"}
    assert {row.definition for row in rows} == {"FPL Points", "Price & Value"}


def test_fpl_resolve_all_stays_in_fpl_domain(monkeypatch):
    monkeypatch.setattr(
        "variable_universe.fpl_catalogue",
        lambda: ({"field_name": "total_points", "subclass": "FPL Points"},),
    )
    monkeypatch.setattr(
        "variable_universe.resolve_variable",
        lambda name, **context: {"variable": name, "family": context["family"]},
    )

    result = resolve_all(
        season="2025-26",
        player_id="123",
        gameweek="1",
        family="fpl",
        variables=("total_points",),
    )

    assert result == {"total_points": {"variable": "total_points", "family": "fpl"}}
