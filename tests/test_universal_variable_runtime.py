from variable_resolver import (
    UnsupportedContextError,
    variable_definition,
    resolve_variable,
)


def test_successful_dribbles_resolves_as_player_fixture_variable(monkeypatch):
    def fake_player_match_field_values(season, fixture_id, field, *, player_id=None):
        assert season == "2024-25"
        assert fixture_id == "123"
        assert field == "successfulDribbles"
        assert player_id == "p1"
        return {
            "results": [
                {
                    "season": season,
                    "fixture_id": fixture_id,
                    "source_player_id": "p1",
                    "source_field": field,
                    "value": "3",
                }
            ]
        }

    monkeypatch.setattr(
        "variable_resolver.player_match_field_values",
        fake_player_match_field_values,
    )

    result = resolve_variable(
        "successfulDribbles",
        season="2024-25",
        fixture_id="123",
        player_id="p1",
    )

    assert result["variable"] == "successfulDribbles"
    assert result["family"] == "player_match"
    assert result["results"][0]["value"] == "3"


def test_derived_pass_completion_uses_two_real_source_fields(monkeypatch):
    calls = []

    def fake_player_match_field_values(season, fixture_id, field, *, player_id=None):
        calls.append(field)
        values = {
            "accuratePass": "45",
            "totalPass": "50",
        }
        return {
            "results": [
                {
                    "source_player_id": "p1",
                    "value": values[field],
                }
            ]
        }

    monkeypatch.setattr(
        "variable_resolver.player_match_field_values",
        fake_player_match_field_values,
    )

    result = resolve_variable(
        "passCompletionPct",
        season="2024-25",
        fixture_id="123",
        player_id="p1",
    )

    assert calls == ["accuratePass", "totalPass"]
    assert result["results"][0]["value"] == 90.0


def test_ambiguous_native_field_requires_family():
    # totalPass is present in multiple source families in the registry.
    try:
        variable_definition("totalPass")
    except UnsupportedContextError:
        return
    raise AssertionError("Ambiguous source field did not require explicit family")
