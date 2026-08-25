from variable_resolver import (
    UnknownVariableError,
    UnsupportedContextError,
    resolve_variable,
    variable_definition,
)


def test_empirical_field_can_resolve_without_individual_handler(monkeypatch):
    monkeypatch.setattr(
        "variable_resolver.available_fields",
        lambda family, season: {
            "player_match": ("totalTackle", "successfulDribbles"),
            "team_match": (),
            "player_season": (),
            "squad": (),
        }[family],
    )
    definition = variable_definition("totalTackle", family="player_match", season="2019-20")
    assert definition.family == "player_match"
    assert definition.source_field == "totalTackle"


def test_unregistered_semantic_field_is_not_rejected_when_empirically_present(monkeypatch):
    monkeypatch.setattr(
        "variable_resolver.available_fields",
        lambda family, season: ("exampleNativeField",) if family == "player_match" else (),
    )
    definition = variable_definition("exampleNativeField", season="2020-21")
    assert definition.family == "player_match"


def test_derived_variable_uses_empirical_underlying_field(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "variable_resolver.available_fields",
        lambda family, season: ("wonTackle", "totalTackle") if family == "player_match" else (),
    )

    def fake_player_match_field_values(season, fixture_id, field, *, player_id=None):
        calls.append(field)
        values = {"wonTackle": "8", "totalTackle": "10"}
        return {"results": [{"source_player_id": "p1", "value": values[field]}]}

    monkeypatch.setattr("variable_resolver.player_match_field_values", fake_player_match_field_values)

    result = resolve_variable("wonTacklePct", season="2020-21", fixture_id="1", player_id="p1")
    assert calls == ["wonTackle", "totalTackle"]
    assert result["results"][0]["value"] == 80.0


def test_unknown_variable_still_fails_closed(monkeypatch):
    monkeypatch.setattr("variable_resolver.available_fields", lambda family, season: ())
    try:
        variable_definition("notARealField", season="2020-21")
    except UnknownVariableError:
        return
    raise AssertionError("Unknown variable did not fail closed")


def test_cross_family_ambiguity_requires_context(monkeypatch):
    monkeypatch.setattr("variable_resolver.available_fields", lambda family, season: ("sharedField",))
    try:
        variable_definition("sharedField", season="2020-21")
    except UnsupportedContextError:
        return
    raise AssertionError("Cross-family ambiguity did not require context")
