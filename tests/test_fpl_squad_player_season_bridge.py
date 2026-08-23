from audit_fpl_squad_player_season_bridge import audit, squad_club_from_source_file


def test_squad_source_path_exposes_club_partition():
    path = r"C:\data\pl_stats\Arsenal_3\squad\2016-17_squad.csv"
    assert squad_club_from_source_file(path) == "Arsenal"


def test_squad_audit_is_read_only_and_reports_population():
    report = audit(("2016-17",))
    assert report["fpl_identities"] > 0
    assert report["squad_rows"] > 0
    assert report["player_season_ids"] > 0


def test_squad_candidates_use_player_season_identity_keys():
    report = audit(("2016-17",))
    assert report["squad_candidate_no_player_season"] == 0
