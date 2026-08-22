from resolve_unmapped_fpl_from_all_raw import build_occurrences, resolve


def test_build_occurrences_finds_nested_fixture_and_player_fields(tmp_path):
    root = tmp_path / "fpl"
    (root / "element-summary").mkdir(parents=True)
    (root / "fixtures.json").write_text('{"id": 1, "stats": []}', encoding="utf-8")
    (root / "element-summary" / "element-1.json").write_text('{"history": [{"minutes": 90}], "fixtures": [{"fixture": 1}]}', encoding="utf-8")
    occurrences = build_occurrences(root)
    assert "id" in occurrences
    assert "minutes" in occurrences
    assert "fixture" in occurrences


def test_exact_field_resolves_from_all_raw_payloads():
    occurrences = {
        "minutes": [{"grain": "player_season", "resource": "element-summary", "field_path": "history[].minutes", "parent_path": "history[]", "field_type": "int", "sample": "element-1.json"}]
    }
    rows = [{"source_surface": "fpl", "field_name": "history[].minutes", "resource": "element-summary", "original_grain": "sample_payload"}]
    out = resolve(rows, occurrences)
    assert out[0]["resolution_status"] == "STRUCTURALLY_RESOLVED"
    assert out[0]["resolved_grain"] == "player_season"


def test_unobserved_field_fails_closed():
    rows = [{"source_surface": "fpl", "field_name": "mystery", "resource": "x", "original_grain": "sample_payload"}]
    out = resolve(rows, {})
    assert out[0]["resolution_status"] == "NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL"
    assert out[0]["resolved_grain"] == "UNMAPPED_REVIEW"
