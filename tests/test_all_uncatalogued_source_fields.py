from audit_all_uncatalogued_source_fields import run


def test_every_uncatalogued_field_receives_one_review_disposition():
    rows = run()
    assert rows
    keys = [(row.family, row.source_field) for row in rows]
    assert len(keys) == len(set(keys))

    allowed = {
        "LIKELY_DIRECT_METRIC",
        "NEEDS_SEMANTIC_REVIEW",
        "STRUCTURAL_OR_METADATA",
    }
    assert {row.disposition for row in rows} <= allowed


def test_review_is_fail_closed():
    rows = run()
    assert all(row.disposition != "PROMOTE" for row in rows)
