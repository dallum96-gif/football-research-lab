from audit_ambiguous_fpl_variables import run


def test_ambiguity_report_collapses_candidates(tmp_path):
    source = tmp_path / "in.csv"
    source.write_text(
        "source_surface,resource,field_name,field_type,resolution_status,upstream_matches\n"
        "fpl,bootstrap-static.json,form,str,AMBIGUOUS_RAW_FPL_GRAIN,player;team\n"
        "fpl,event-live,event_points,int,AMBIGUOUS_RAW_FPL_GRAIN,player;gameweek\n"
        "fpl,bootstrap-static.json,form,str,STRUCTURALLY_RESOLVED,player\n",
        encoding="utf-8",
    )
    out = run(source, tmp_path / "out.csv")
    assert [r["field_name"] for r in out] == ["event_points", "form"]
    form = next(r for r in out if r["field_name"] == "form")
    assert form["candidate_grains"] == "player;team"


def test_empty_input_is_safe(tmp_path):
    source = tmp_path / "in.csv"
    source.write_text(
        "source_surface,resource,field_name,field_type,resolution_status,upstream_matches\n",
        encoding="utf-8",
    )
    out = run(source, tmp_path / "out.csv")
    assert out == []
