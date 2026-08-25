from variable_universe import list_variables, resolve_all, variable_catalogue


def test_player_fixture_variable_catalogue_is_context_driven(monkeypatch):
    monkeypatch.setattr(
        "variable_universe.available_fields",
        lambda family, season: {
            "player_match": ("successfulDribbles", "wonTackle", "totalTackle"),
            "team_match": (),
            "player_season": (),
            "squad": (),
        }[family],
    )

    rows = list_variables(season="2020-21", fixture_id="1", player_id="p1")
    names = {row.name for row in rows}

    assert "successfulDribbles" in names
    assert "wonTacklePct" in names


def test_variable_catalogue_is_serialisable(monkeypatch):
    monkeypatch.setattr(
        "variable_universe.available_fields",
        lambda family, season: ("successfulDribbles",) if family == "player_match" else (),
    )

    rows = variable_catalogue(season="2020-21", fixture_id="1", player_id="p1")
    assert rows[0]["name"] == "successfulDribbles"
    assert rows[0]["family"] == "player_match"


def test_resolve_all_can_select_subset(monkeypatch):
    monkeypatch.setattr(
        "variable_universe.available_fields",
        lambda family, season: ("successfulDribbles",) if family == "player_match" else (),
    )
    monkeypatch.setattr(
        "variable_universe.resolve_variable",
        lambda name, **context: {"variable": name, "context": context},
    )

    result = resolve_all(
        season="2020-21",
        fixture_id="1",
        player_id="p1",
        variables=("successfulDribbles",),
    )
    assert set(result) == {"successfulDribbles"}
    assert result["successfulDribbles"]["variable"] == "successfulDribbles"
