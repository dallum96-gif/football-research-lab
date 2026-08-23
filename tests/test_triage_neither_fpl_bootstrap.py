from triage_neither_fpl_bootstrap import path_root, triage


def test_path_root_handles_nested_json_path():
    assert path_root("elements[].chance_of_playing_next_round") == "elements"
    assert path_root("game_config.scoring.assists") == "game_config"


def test_known_bootstrap_family_is_candidate_only():
    rows = [{
        "source_layer_state": "NEITHER",
        "field_name": "elements[].news",
        "resource": "bootstrap-static.json",
        "field_type": "str",
        "current_raw_found": "NO",
        "historical_found": "NO",
    }]
    out = triage(rows)
    assert out[0]["triage_status"] == "OBJECT_FAMILY_CANDIDATE"
    assert out[0]["object_family_candidate"] == "player"


def test_unknown_root_fails_to_unknown_bootstrap_root():
    rows = [{
        "source_layer_state": "NEITHER",
        "field_name": "mystery_root.foo",
        "resource": "bootstrap-static.json",
        "field_type": "str",
        "current_raw_found": "NO",
        "historical_found": "NO",
    }]
    out = triage(rows)
    assert out[0]["triage_status"] == "UNKNOWN_BOOTSTRAP_ROOT"
    assert out[0]["object_family_candidate"] == ""
