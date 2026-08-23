from resolve_unmapped_fpl_from_raw_bootstrap import bootstrap_field_presence, resolve


def test_bootstrap_presence_maps_player_and_team_fields():
    payload = {
        "elements": [{"id": 1, "form": "1.2"}],
        "teams": [{"id": 1, "strength": 1000}],
    }
    presence = bootstrap_field_presence(payload)
    assert "form" in presence["player"]
    assert "strength" in presence["team"]


def test_exact_raw_field_resolves_structurally():
    payload = {"elements": [{"form": "1.2"}], "teams": [{"strength": 1000}]}
    rows = [{"source_surface": "fpl", "field_name": "form", "resource": "bootstrap-static.json", "grain": "sample_payload"}]
    out = resolve(rows, payload)
    assert out[0]["resolution_status"] == "STRUCTURALLY_RESOLVED"
    assert out[0]["resolved_grain"] == "player"


def test_unknown_field_fails_closed():
    payload = {"elements": [{"form": "1.2"}]}
    rows = [{"source_surface": "fpl", "field_name": "not_here", "resource": "bootstrap-static.json", "grain": "sample_payload"}]
    out = resolve(rows, payload)
    assert out[0]["resolution_status"] == "NOT_FOUND_IN_RAW_BOOTSTRAP"
    assert out[0]["resolved_grain"] == "UNMAPPED_REVIEW"
