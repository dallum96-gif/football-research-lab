from audit_source_field_evidence import _summarise


def test_summary_numeric_series_reports_range_and_examples():
    import pandas as pd

    result = _summarise(pd.Series([1, 2, 2, None]))
    assert result["rows"] == 4
    assert result["non_null"] == 3
    assert result["distinct"] == 2
    assert result["minimum"] == 1.0
    assert result["maximum"] == 2.0
    assert result["examples"] == ["1.0", "2.0"]


def test_summary_text_series_does_not_invent_numeric_range():
    import pandas as pd

    result = _summarise(pd.Series(["yes", "no", "yes"]))
    assert result["distinct"] == 2
    assert result["minimum"] is None
    assert result["maximum"] is None
    assert result["examples"] == ["yes", "no"]
