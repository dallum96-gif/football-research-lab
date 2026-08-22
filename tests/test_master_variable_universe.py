from pathlib import Path

from enumerate_master_variable_universe import dedupe, flatten_keys, local_catalog_rows


def test_flatten_keys_keeps_nested_json_paths():
    payload = {"stats": {"xg": 1.2}, "events": [{"minute": 12, "player": {"id": 7}}]}
    fields = dict(flatten_keys(payload))
    assert "stats.xg" in fields
    assert "events[].minute" in fields
    assert "events[].player.id" in fields


def test_dedupe_is_resource_and_grain_aware():
    rows = [
        {
            "source_surface": "PL",
            "resource": "match",
            "grain": "match",
            "field_name": "goals",
            "field_type": "int",
            "status": "OBSERVED",
            "notes": "a",
        },
        {
            "source_surface": "PL",
            "resource": "match",
            "grain": "match",
            "field_name": "goals",
            "field_type": "int",
            "status": "OBSERVED",
            "notes": "b",
        },
        {
            "source_surface": "PL",
            "resource": "player_season",
            "grain": "player_season",
            "field_name": "goals",
            "field_type": "int",
            "status": "OBSERVED",
            "notes": "c",
        },
    ]
    result = dedupe(rows)
    assert len(result) == 2


def test_local_catalog_is_not_empty():
    assert local_catalog_rows()
