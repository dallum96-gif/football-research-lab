from pathlib import Path

import audit_source_field_coverage as audit


def test_audit_has_explicit_family_to_source_mapping():
    assert audit._season_files("events_stats", "2025-26") is not None
    assert audit._season_files("players_match_stats", "2025-26") is not None
    assert audit._season_files("players_stats", "2025-26") is not None
    assert audit._season_files("squad", "2025-26") is not None


def test_audit_output_is_repo_data_path():
    assert audit.OUTPUT.parent.name == "data"
    assert audit.OUTPUT.name == "source_field_coverage.csv"
