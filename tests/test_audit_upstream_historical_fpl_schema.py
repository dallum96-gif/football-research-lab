from pathlib import Path

from audit_upstream_historical_fpl_schema import audit, load_queue, terminal_name


def test_terminal_name_handles_json_paths():
    assert terminal_name("elements[].chance_of_playing_next_round") == "chance_of_playing_next_round"


def test_audit_matches_historical_headers():
    queue = [
        {"source_surface": "fpl", "field_name": "elements[].form"},
        {"source_surface": "fpl", "field_name": "elements[].mystery"},
    ]
    files = [
        {"grain": "player", "season_file": "2016-17_all_players_gw.csv", "path": "x", "raw_url": "u1"},
    ]

    import audit_upstream_historical_fpl_schema as mod
    original = mod.fetch_header
    mod.fetch_header = lambda url: ["element", "form", "minutes"]
    try:
        rows = audit(queue, files)
    finally:
        mod.fetch_header = original

    assert rows[0]["historical_presence"] == "FOUND"
    assert rows[0]["historical_grains"] == "player"
    assert rows[1]["historical_presence"] == "NOT_FOUND"
