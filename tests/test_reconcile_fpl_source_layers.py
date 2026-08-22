from pathlib import Path

import reconcile_fpl_source_layers as mod


def test_source_layer_states():
    rows = [
        {"source_surface": "fpl", "field_name": "both", "resource": "bootstrap-static.json", "grain": "sample_payload", "field_type": "int"},
        {"source_surface": "fpl", "field_name": "current", "resource": "element", "grain": "sample_payload", "field_type": "int"},
        {"source_surface": "fpl", "field_name": "historical", "resource": "match", "grain": "sample_payload", "field_type": "int"},
        {"source_surface": "fpl", "field_name": "neither", "resource": "bootstrap-static.json", "grain": "sample_payload", "field_type": "int"},
    ]
    current = {
        "both": {"resolution_status": "STRUCTURALLY_RESOLVED", "resolved_grain": "player"},
        "current": {"resolution_status": "AMBIGUOUS_RAW_FPL_GRAIN", "resolved_grain": "UNMAPPED_REVIEW"},
        "historical": {"resolution_status": "NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL", "resolved_grain": "UNMAPPED_REVIEW"},
        "neither": {"resolution_status": "NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL", "resolved_grain": "UNMAPPED_REVIEW"},
    }
    historical = {
        "both": {"historical_presence": "FOUND", "historical_grains": "player"},
        "current": {"historical_presence": "NOT_FOUND"},
        "historical": {"historical_presence": "FOUND", "historical_grains": "fixture"},
        "neither": {"historical_presence": "NOT_FOUND"},
    }
    states = {}
    for row in rows:
        field = row["field_name"]
        current_found = current[field]["resolution_status"] != "NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL"
        historical_found = historical[field]["historical_presence"] == "FOUND"
        if current_found and historical_found:
            state = "BOTH"
        elif current_found:
            state = "CURRENT_RAW_ONLY"
        elif historical_found:
            state = "HISTORICAL_PUBLISHED_ONLY"
        else:
            state = "NEITHER"
        states[field] = state
    assert states == {
        "both": "BOTH",
        "current": "CURRENT_RAW_ONLY",
        "historical": "HISTORICAL_PUBLISHED_ONLY",
        "neither": "NEITHER",
    }


def test_load_csv_exists_on_real_audit_file(tmp_path: Path):
    path = tmp_path / "x.csv"
    path.write_text("field_name,resource\na,match\n", encoding="utf-8")
    assert mod.load_csv(path) == [{"field_name": "a", "resource": "match"}]
