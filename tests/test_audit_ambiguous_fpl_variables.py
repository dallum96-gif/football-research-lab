from audit_ambiguous_fpl_variables import summarise


def test_groups_ambiguous_rows_by_field():
    rows = [
        {
            "field_name": "form",
            "resolution_status": "AMBIGUOUS_RAW_FPL_GRAIN",
            "upstream_matches": "player;gameweek",
            "matched_resources": "bootstrap-static.json;event-live",
            "matched_paths": "elements[].form;events[].form",
        },
        {
            "field_name": "form",
            "resolution_status": "AMBIGUOUS_RAW_FPL_GRAIN",
            "upstream_matches": "player;gameweek",
            "matched_resources": "bootstrap-static.json;event-live",
            "matched_paths": "elements[].form;events[].form",
        },
    ]
    out = summarise(rows)
    assert len(out) == 1
    assert out[0]["field_name"] == "form"
    assert out[0]["candidate_grains"] == "gameweek;player"


def test_ignores_resolved_rows():
    rows = [{
        "field_name": "form",
        "resolution_status": "STRUCTURALLY_RESOLVED",
        "upstream_matches": "player",
        "matched_resources": "bootstrap-static.json",
        "matched_paths": "elements[].form",
    }]
    assert summarise(rows) == []
