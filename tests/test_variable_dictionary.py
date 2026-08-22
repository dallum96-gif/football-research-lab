from pathlib import Path

from build_variable_dictionary import classify, run


def test_known_navigation_categories():
    assert classify("totalShots", "player_match", "player_match")[0] == "Shooting & Finishing"
    assert classify("accurateCross", "team_match", "team_match")[0] == "Crossing & Set Pieces"
    assert classify("yellowCards", "player_season", "player_season")[0] == "Discipline"
    assert classify("savesMade", "player_season", "player_season")[0] == "Goalkeeping"
    assert classify("metersCoveredSprintingKm", "player_match", "player_match")[0] == "Physical & Tracking"


def test_unknown_field_fails_to_review_category():
    assert classify("mysteriousProviderMetric", "unknown", "unknown")[0] == "Unclassified Review"


def test_dictionary_preserves_row_count_and_semantic_status(tmp_path: Path):
    source = tmp_path / "master.csv"
    output = tmp_path / "dictionary.csv"
    source.write_text(
        "source_surface,resource,grain,field_name,field_type,status,statuses_seen,types_seen,notes\n"
        "FRL_LOCAL_CSV,player_match,player_match,totalShots,int,UNCATALOGUED,UNCATALOGUED,int,n\n"
        "FRL_LOCAL_CSV,player_match,player_match,foo,int,UNCATALOGUED,UNCATALOGUED,int,n\n",
        encoding="utf-8",
    )

    count = run(source, output)
    assert count == 2
    rows = output.read_text(encoding="utf-8-sig").splitlines()
    assert len(rows) == 3
    assert "UNCATALOGUED" in rows[1]
    assert "UNCATALOGUED" in rows[2]
