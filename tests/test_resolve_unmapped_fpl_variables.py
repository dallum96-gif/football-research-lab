from resolve_unmapped_fpl_variables import resolve


def test_exact_registry_match_resolves_unique_grain():
    queue = [{"source_surface": "fpl", "field_name": "chance_of_playing_next_round"}]
    upstream = [{
        "source_family": "FPL API",
        "dataset_grain": "player",
        "variable": "chance_of_playing_next_round",
    }]
    rows = resolve(queue, upstream)
    assert rows[0]["resolved_grain"] == "player"
    assert rows[0]["resolution_status"] == "STRUCTURALLY_RESOLVED"


def test_json_path_matches_registry_terminal_name():
    queue = [{"source_surface": "fpl", "field_name": "elements[].chance_of_playing_next_round"}]
    upstream = [{
        "source_family": "FPL API",
        "dataset_grain": "player",
        "variable": "chance_of_playing_next_round",
    }]
    rows = resolve(queue, upstream)
    assert rows[0]["resolved_grain"] == "player"
    assert rows[0]["resolution_status"] == "STRUCTURALLY_RESOLVED"


def test_ambiguous_registry_match_fails_closed():
    queue = [{"source_surface": "fpl", "field_name": "status"}]
    upstream = [
        {"source_family": "FPL API", "dataset_grain": "player", "variable": "status"},
        {"source_family": "FPL API", "dataset_grain": "team", "variable": "status"},
    ]
    rows = resolve(queue, upstream)
    assert rows[0]["resolved_grain"] == "UNMAPPED_REVIEW"
    assert rows[0]["resolution_status"] == "AMBIGUOUS_UPSTREAM_GRAIN"


def test_missing_registry_match_fails_closed():
    queue = [{"source_surface": "fpl", "field_name": "mystery_field"}]
    rows = resolve(queue, [])
    assert rows[0]["resolved_grain"] == "UNMAPPED_REVIEW"
    assert rows[0]["resolution_status"] == "NO_UPSTREAM_REGISTRY_MATCH"
