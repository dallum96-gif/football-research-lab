from audit_unmapped_variable_queue import build_queue, profile


def test_queue_only_contains_unmapped_rows(tmp_path):
    source = tmp_path / "input.csv"
    output = tmp_path / "queue.csv"
    source.write_text(
        "source_surface,resource,grain,field_name,field_type,decomposed_grain,decomposition_basis,notes\n"
        "fpl,match,sample_payload,fixture.id,string,fixture,path marker,\n"
        "fpl,match,sample_payload,weird_value,number,UNMAPPED_REVIEW,insufficient structural evidence,\n",
        encoding="utf-8",
    )
    queue = build_queue(source, output)
    assert len(queue) == 1
    assert queue[0]["field_name"] == "weird_value"
    assert queue[0]["review_status"] == "OPEN"
    assert output.exists()


def test_profile_counts_open_queue():
    queue = [{
        "source_surface": "fpl",
        "resource": "match",
        "original_grain": "sample_payload",
        "field_name": "x",
        "field_type": "number",
        "decomposed_grain": "UNMAPPED_REVIEW",
        "decomposition_basis": "",
        "notes": "",
        "review_status": "OPEN",
        "resolution": "",
        "evidence_required": "raw path/context or source-schema evidence",
    }]
    p = profile(queue)
    assert p["count"] == 1
    assert p["source_surface"]["fpl"] == 1
    assert p["resource"]["match"] == 1
