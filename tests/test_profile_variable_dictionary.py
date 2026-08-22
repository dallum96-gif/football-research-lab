from pathlib import Path

from profile_variable_dictionary import _enrich_decomposed_rows, profile


def test_profile_counts_all_rows():
    rows = [
        {"grain": "player_match", "resource": "player_match", "navigation_category": "Shooting & Finishing", "semantic_status": "VERIFIED", "source_surface": "FRL_LOCAL_CSV"},
        {"grain": "team_match", "resource": "team_match", "navigation_category": "Crossing & Set Pieces", "semantic_status": "UNCATALOGUED", "source_surface": "FRL_LOCAL_CSV"},
    ]
    p = profile(rows)
    assert sum(p["grain"].values()) == 2
    assert p["grain"]["player_match"] == 1
    assert p["category"]["Crossing & Set Pieces"] == 1


def test_profile_preserves_distinct_grains():
    rows = [
        {"grain": "player_match", "resource": "r", "navigation_category": "Shooting & Finishing", "semantic_status": "", "source_surface": "x"},
        {"grain": "team_match", "resource": "r", "navigation_category": "Shooting & Finishing", "semantic_status": "", "source_surface": "x"},
    ]
    p = profile(rows)
    assert p["grain"]["player_match"] == 1
    assert p["grain"]["team_match"] == 1


def test_decomposed_rows_use_resolved_grain_for_profile():
    rows = [
        {
            "source_surface": "fpl",
            "resource": "match",
            "grain": "sample_payload",
            "field_name": "fixture.id",
            "decomposed_grain": "fixture",
        },
        {
            "source_surface": "fpl",
            "resource": "match",
            "grain": "sample_payload",
            "field_name": "event.minutes",
            "decomposed_grain": "event",
        },
    ]
    p = profile(rows)
    assert p["grain"]["fixture"] == 1
    assert p["grain"]["event"] == 1
    assert p["original_grain"]["sample_payload"] == 2


def test_decomposed_rows_are_enriched_from_dictionary(tmp_path: Path):
    dictionary = tmp_path / "dictionary.csv"
    dictionary.write_text(
        "source_surface,resource,grain,field_name,navigation_category,semantic_status\n"
        "fpl,match,sample_payload,fixture.id,Tactical & Match Context,OBSERVED_IN_RAW_PAYLOAD\n",
        encoding="utf-8",
    )
    rows = [
        {
            "source_surface": "fpl",
            "resource": "match",
            "grain": "sample_payload",
            "field_name": "fixture.id",
            "decomposed_grain": "fixture",
        }
    ]
    enriched = _enrich_decomposed_rows(rows, dictionary)
    p = profile(enriched)
    assert p["grain"]["fixture"] == 1
    assert p["category"]["Tactical & Match Context"] == 1
    assert p["semantic"]["OBSERVED_IN_RAW_PAYLOAD"] == 1
